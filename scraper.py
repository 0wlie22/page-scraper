import logging
import time

import requests
from bs4 import BeautifulSoup
from tinydb import Query, TinyDB

DB_PATH = "/var/db/db.json"
NTFY_URL = "https://ntfy.sh/tesy"

class Flat:
    def __init__(self, table: list, id: str, url: str) -> None:
        self.id = id
        self.url = url
        self.street = table[3].text
        self.rooms = table[4].text
        self.area = table[5].text
        self.floor = table[6].text
        self.type = table[7].text
        self.price = table[9].text.split(" ")

    def __str__(self) -> str:
        return f"Flat {self.id}: {self.street}, {self.rooms}, {self.area}, {self.floor}, {self.type}, {self.price}"


class Scraper:
    def __init__(self, base_url, flat_url) -> None:
        self.base_url = base_url
        self.flat_url = flat_url
        self.db = TinyDB(DB_PATH)

    def scrape_page(self, page_number) -> None:
        url = f"{self.base_url}page{page_number}.html"
        response = requests.get(url)

        parsed_html = BeautifulSoup(response.text, "html.parser")
        if not parsed_html.body:
            logging.error(f"Failed to parse page {page_number}")
            return

        table = parsed_html.body.find("table", {"align": "center"})
        if not table:
            logging.error(f"Failed to find table in page {page_number}")
            return

        lines = table.find_all("tr") # pyright: ignore
        if not lines:
            logging.error(f"Failed to find table in page {page_number}")
            return


        for line in lines[1:-1]:
            flat_id = line.find_all("td")[1].find("a").get("href").split("/")[-1].split(".")[0]

            # Check if the flat is already in the database
            if self.db.search(Query().id == flat_id):
                logging.info(f"Flat {flat_id} already in the database")
                continue

            flat = Flat(line.find_all("td"), flat_id, f"{self.flat_url}{flat_id}.html")

            # Check if the flat is rented by days or is too expensive
            if "mēn" not in flat.price[2] or float(flat.price[0].replace(",", "")) > 350:
                logging.info(f"Flat {flat_id} is too expensive")
                continue

            flat.price = flat.price[0]

            logging.info(flat)

            self.db.insert(
                {
                    "id": flat.id,
                    "url": flat.url
                }
            )

            self.notify(flat)
            time.sleep(0.5) # to not hit ntfy rate limit
            break

    @staticmethod
    def notify(flat: Flat):
        requests.post(
            "https://ntfy.sh/flat-advertisments",
            headers={
                "Click": f"{flat.url}",
                "Title": "New flat found"
            },
            data=f"New flat found{flat.street}, {flat.rooms}, {flat.area}, {flat.floor}, {flat.type}, {flat.price}"
        )

        logging.info("Notification sent")
