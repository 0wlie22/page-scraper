import requests
from bs4 import BeautifulSoup
from tinydb import Query, TinyDB


class Flat:
    def __init__(self, id, url, description, price):
        self.id = id
        self.url = url
        self.description = description
        self.price = price

    def __str__(self):
        return f"ID: {self.id}, URL: {self.url}, Description: {self.description}, Price: {self.price}"


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

        for line in lines[1:-1]:
            flat_id = line.find_all("td")[1].find("a").get("href").split("/")[-1]

            if self.db.search(Query().id == flat_id):
                continue

            price = line.find_all("td")[-1].text.split(" ")
            description = line.find_all("td")[2].text

            if "mēn" not in price[2] or float(price[0].replace(",", "")) > 350:
                continue

            flat_url = f"{self.flat_url}{flat_id}"

            flat = Flat(
                id=flat_id, url=flat_url, description=description, price="".join(price)
            )

            self.db.insert(
                {
                    "id": flat.id,
                    "url": flat.url,
                    "description": flat.description,
                    "price": flat.price,
                }
            )

            self.notify(flat_url, flat.price)

    def notify(self, flat_url, price):
        requests.post(
            "http://ntfy.sh/flat-advertisments",
            json={"url": flat_url, "price": price[0:3]},
        )


def main():
    scraper = Scraper(
        base_url="https://www.ss.com/lv/real-estate/flats/riga/centre/hand_over/",
        flat_url="https://www.ss.com/msg/lv/real-estate/flats/riga/centre/",
    )

    for page_number in range(1, 10):
        scraper.scrape_page(page_number)


if __name__ == "__main__":
    main()
