import logging
import time

import requests
from bs4 import BeautifulSoup
from requests.models import default_hooks
from tinydb import Query, TinyDB

DB_PATH = "/var/db/db.json"


class Flat:
    def __init__(self, id, index, url, description, price):
        self.id = id
        self.index = index
        self.url = url
        self.description = description
        self.price = price

    def __str__(self):
        return f"Nr: {self.index}, URL: {self.url}, Description: {self.description}, Price: {self.price}\n"


class Scraper:
    def __init__(self, base_url, flat_url):
        self.base_url = base_url
        self.flat_url = flat_url
        self.db = TinyDB(DB_PATH)

    def scrape_page(self, page_number):
        url = f"{self.base_url}page{page_number}.html"
        response = requests.get(url)

        parsed_html = BeautifulSoup(response.text, "html.parser")
        table = parsed_html.body.find("table", {"align": "center"})
        lines = table.find_all("tr")

        index_counter = 0

        for line in lines[1:-1]:
            flat_id = line.find_all("td")[1].find("a").get("href").split("/")[-1].split(".")[0]

            if self.db.search(Query().id == flat_id):
                logging.info(f"Flat {flat_id} already in the database")
                continue

            price = line.find_all("td")[-1].text.split(" ")
            description = line.find_all("td")[2].text

            if "mēn" not in price[2] or float(price[0].replace(",", "")) > 350:
                continue

            index_counter += 1

            flat_url = f"{self.flat_url}{flat_id}.html"

            flat = Flat(
                id=flat_id,
                index=index_counter,
                url=flat_url,
                description=description,
                price="".join(price),
            )

            logging.info(flat)

            self.db.insert(
                {
                    "id": flat.id,
                    "url": flat.url,
                    "description": flat.description,
                    "price": flat.price,
                }
            )

            self.notify(flat_url, flat.price, flat.description)
            time.sleep(0.5) # to not hit ntfy rate limit

    def notify(self, flat_url, price, description):
        requests.post(
            "https://ntfy.sh/flat-advertisments",
            headers={"Click": f"{flat_url}",
                     "Title": "New flat found"},
            data=f"{description} - {price}"
        )
        logging.info("Notification sent")
