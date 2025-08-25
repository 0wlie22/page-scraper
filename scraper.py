# pyright: basic
import logging
import time
import requests
import re
import json
from playwright.sync_api import sync_playwright
import html
import json
from shapely.geometry import shape, Point



# from requests.models import default_hooks
# from tinydb import Query, TinyDB


class Appartment:
    def __init__(self, id: int, index: int, url: str, coordinates: tuple, price: str):
        self.id = id
        self.index = index
        self.coordinates = coordinates
        self.url = url
        self.price = price

    def __str__(self):
        return f"Nr: {self.index}, URL: {self.url}, Price: {self.price}\n"


class Scraper:
    def __init__(self):
        self.url = "https://www.ss.com/lv/fTgTeF4QAzt4FD4eFFM=.html?map=17020&map2=17020&cat=14195&mode=3"
        self.cookies_url = "https://www.ss.com/lv/real-estate/flats/riga/all/fDgQeF4S.html"
        with open("bad_regions.geojson") as f:
            geojson = json.load(f)

        self.bad_coordinates = [shape(feature["geometry"]) for feature in geojson["features"]]
        # self.db = TinyDB("db.json")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(self.cookies_url)
            self.cookies = context.cookies()
            print("COOKIES: ", self.cookies[0]['value'])
            self.scrape_page()
            page.close()

    def scrape_page(self):
        cookies = {
            "PHPSESSID": self.cookies[0]['value']
        }
        response = requests.get(self.url, cookies=cookies)
        
        match = re.search(r"var\s+MARKER_DATA\s*=\s*(\[.*?\]);", response.text, re.S)
        marker_data = []
        if match:
            marker_data_str = match.group(1)  # the raw JS array
            try:
                marker_data = json.loads(marker_data_str)  # parse as JSON
            except json.JSONDecodeError:
                marker_data = marker_data_str

        for data in marker_data:
            elements = data.split("<br>")
            elements = [html.unescape(item).replace("<b>", "").replace("</b>", "") for item in elements]

            if len(elements) != 8:
                continue

            if validCost(elements):
                coordinates = tuple(elements[0].split("|")[0:2])
                address = elements[1]
                rooms = elements[2].split(" ")[1]
                floor = elements[4].split(" ")[1].split("/")
                # print(elements)
                print(self.bad_coordinates[0])
                # if validFloor(floor):
                #     cost = elements[6]
                #     if validNeighbourhood:
                #         # print(coordinates, address, rooms, floor, cost)



            # self.db.insert(
            #     {
            #         "id": flat.id,
            #         "url": flat.url,
            #         "price": flat.price,
            #     }
            # )

            # self.notify(flat_url, flat.price)
            # time.sleep(0.5)  # to not hit ntfy rate limit

    def notify(self, flat_url, price):
        response = requests.post(
            "https://ntfy.sh/tesy",
            headers={
                "Click": f"{flat_url}",
                "Title": f"New flat found: {price[:3]}",
            },
        )

        logging.info(f"Notification sent. Code: {response.status_code}")

def validCost(elements: list):
    return "mēn" not in elements[6] and "dienā" not in elements[6] and "īret" not in elements[6] and not "pērku" in elements[5] and "vēlos" not in elements[5]

def validFloor(floor: list) -> bool:
    if len(floor) > 1:
        return not floor[0] == floor[1] or int(floor[0]) >= 3
    return int(floor[0]) >= 3

def validRooms(rooms: int) -> bool:
    return rooms <=3 and rooms >= 2

def validNeighbourhood(coordinates: tuple) -> bool:
    point = Point(coordinates)
    print(self.bad_coordinates)
    return any(poly.contains(point) for poly in self.bad_coordinates)

        
# 693828259240c49e4b7e704067aa99b0
# 1fbe7847ec4682d57f81a8a6b9b5d48f
