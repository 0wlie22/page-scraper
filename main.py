import logging

from scraper import Scraper


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [INFO] - %(message)s",
    )

    with open("bad_regions.geojson") as f:
        geojson = json.load(f)

    bad_polys = [shape(feature["geometry"]) for feature in geojson["features"]]


    scraper = Scraper()

    for page_number in range(1, 2):
        logging.info(f"Scraping page {page_number}")
        scraper.scrape_page(page_number)


if __name__ == "__main__":
    main()
