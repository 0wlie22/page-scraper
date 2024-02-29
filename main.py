from scraper import Scraper
import logging

class url:
    def __init__(self, hometown):
        self.base_url = f"https://www.ss.com/lv/real-estate/flats/riga/{hometown}/hand_over/"
        self.flat_url = f"https://www.ss.com/msg/lv/real-estate/flats/riga/{hometown}/"




def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [INFO] - %(message)s",
    )

    scraper = Scraper(
        base_url="https://www.ss.com/lv/real-estate/flats/riga/centre/hand_over/",
        flat_url="https://m.ss.com/msg/lv/real-estate/flats/riga/centre/",
    )

    for hometown in hometowns:
        logging.info(f"Scraping {hometown}")
        scraper = Scraper(url(hometown).base_url, url(hometown).flat_url)

        for page_number in range(1, 11):
            logging.info(f"Scraping page {page_number}")
            scraper.scrape_page(page_number)


if __name__ == "__main__":
    main()
