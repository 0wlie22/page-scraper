from scraper import Scraper
import logging


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [INFO] - %(message)s",
    )

    scraper = Scraper(
        base_url="https://www.ss.com/lv/real-estate/flats/riga/centre/hand_over/",
        flat_url="https://www.m.ss.com/msg/lv/real-estate/flats/riga/centre/",
    )

    for page_number in range(1, 11):
        logging.info(f"Scraping page {page_number}")
        scraper.scrape_page(page_number)


if __name__ == "__main__":
    main()
