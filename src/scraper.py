import html
import json
import logging
import os
import re
import time
import unicodedata

import demjson3
import requests
from playwright.sync_api import sync_playwright
from shapely.geometry import Point, shape
from tinydb import Query, TinyDB

from apartment import Appartment
from config import NTFY_URL, REGIONS_FILE, SS_COOKIES_URL, SS_URL


class Scraper:
    def __init__(self, dry_run: bool = False):
        self.url = SS_URL
        self.cookies_url = SS_COOKIES_URL
        self.dry_run = dry_run
        regions_path = REGIONS_FILE
        if not os.path.isabs(regions_path):
            regions_path = os.path.join(
                os.path.dirname(__file__), os.pardir, regions_path
            )
            regions_path = os.path.normpath(regions_path)
        with open(regions_path) as f:
            geojson = json.load(f)

        self.bad_coordinates = [
            shape(feature["geometry"]) for feature in geojson["features"]
        ]
        db_path = os.getenv("DB_PATH", "db.json")
        self.db = TinyDB(db_path)

    def run(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(self.cookies_url)
            self.cookies = context.cookies()
            print("COOKIES: ", self.cookies[0]["value"])
            self.scrape_page()
            page.close()

    def scrape_page(self):
        cookies = {"PHPSESSID": self.cookies[0]["value"]}
        response = requests.get(self.url, cookies=cookies)

        match = re.search(r"var\s+MARKER_DATA\s*=\s*(\[.*?\]);", response.text, re.S)
        print(match)
        marker_data = []
        if match:
            marker_data_str = match.group(1)
            try:
                marker_data = demjson3.decode(marker_data_str)
            except demjson3.JSONDecodeError as e:
                print(f"Can't decode marker data: {e}")
                return

        if not marker_data:
            print("No marker data found.")
            return

        for index, data in enumerate(marker_data, start=1):
            elements = data.split("<br>")
            elements = [
                html.unescape(item).replace("<b>", "").replace("</b>", "")
                for item in elements
            ]

            if len(elements) != 8:
                continue

            coordinates = tuple(elements[0].split("|")[0:2])
            neighbourhood = elements[0].split("|")[2].split(" ")[1]
            address = elements[1]
            rooms = elements[2].split(" ")[1]
            floor = elements[4].split(" ")[1].split("/")
            link_parts = elements[7].split("|")
            apartment = Appartment(
                id=link_parts[0] if link_parts else "",
                index=index,
                url=(
                    f"https://ss.com{link_parts[1]}"
                    if len(link_parts) > 1 and link_parts[1].startswith("/")
                    else link_parts[1]
                    if len(link_parts) > 1
                    else ""
                ),
                coordinates=coordinates,
                price=elements[6],
            )
            apartment.rooms = rooms
            apartment.floor = floor
            apartment.address = address
            apartment.neighbourhood = neighbourhood
            apartment.price = elements[6]

            logging.debug(
                "Parsed apartment: %s",
                {
                    "id": apartment.id,
                    "url": apartment.url,
                    "coordinates": apartment.coordinates,
                    "neighbourhood": apartment.neighbourhood,
                    "address": apartment.address,
                    "rooms": apartment.rooms,
                    "floor": apartment.floor,
                    "price": apartment.price,
                },
            )

            if not apartment.set_cost(apartment.price):
                logging.debug(
                    "Skipping apartment with invalid cost: %s", apartment.price
                )
                continue

            if not self.validNeighbourhood(apartment.coordinates):
                logging.debug(
                    "Skipping apartment in excluded neighbourhood: %s",
                    apartment.neighbourhood or "",
                )
                continue

            if not apartment.set_rooms(apartment.rooms or ""):
                logging.debug(
                    "Skipping apartment with invalid rooms: %s", apartment.rooms
                )
                continue

            if not apartment.set_floor(apartment.floor or []):
                logging.debug(
                    "Skipping apartment with invalid floor: %s",
                    apartment.floor_display(),
                )
                continue

            if self.is_in_db(apartment):
                logging.debug(
                    "Skipping apartment already in database: %s", apartment.url
                )
                continue

            apartment.print()
            if not self.dry_run:
                self.db.insert(
                    {
                        "id": apartment.id,
                        "url": apartment.url,
                        "price": apartment.price,
                    }
                )
            else:
                logging.debug(
                    "Dry run enabled; skipping DB insert for %s", apartment.url
                )

            if not self.dry_run:
                status_code = self.notify(apartment)
                while status_code != 200:
                    time.sleep(60)
                    status_code = self.notify(apartment)
                time.sleep(0.5)
            else:
                logging.debug(
                    "Dry run enabled; skipping notification for %s",
                    apartment.url,
                )

    def notify(self, apartment: Appartment) -> int:
        title_address = apartment.address or ""
        title_address = unicodedata.normalize("NFKD", title_address)
        title_address = title_address.encode("ascii", "ignore").decode("ascii")
        response = requests.post(
            NTFY_URL,
            headers={
                "Click": f"{apartment.url}",
                "Title": f"New apartment: {title_address}",
            },
            data=f"{apartment.price} | {apartment.floor_display()} floor",
        )

        logging.info(f"Notification sent. Code: {response.status_code}")

        return response.status_code

    def is_in_db(self, apartment: Appartment) -> bool:
        query = Query()
        if apartment.id:
            return self.db.contains(query.id == apartment.id)
        if apartment.url:
            return self.db.contains(query.url == apartment.url)
        return False

    def validNeighbourhood(self, coordinates: tuple) -> bool:
        coordinates = (float(coordinates[0]), float(coordinates[1]))
        point = Point(coordinates[1], coordinates[0])
        for polygon in self.bad_coordinates:
            if polygon.contains(point):
                return False
        return True
