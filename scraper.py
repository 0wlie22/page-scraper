import logging

import requests
from bs4 import BeautifulSoup
from tinydb import Query, TinyDB


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
        self.db = TinyDB("db.json")

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

            flat_url = f"{self.flat_url}{flat_id}"

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

            self.notify(index_counter, flat_url, flat.price)

    def notify(self, index, flat_url, price):
        requests.post(
            "http://ntfy.sh/flat-advertisments",
            json={"index": index, "url": flat_url, "price": price[0:3]},
        )
