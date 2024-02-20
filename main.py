from scraper import Scraper


def main():
    scraper = Scraper(
        base_url="https://www.ss.com/lv/real-estate/flats/riga/centre/hand_over/",
        flat_url="https://www.ss.com/msg/lv/real-estate/flats/riga/centre/",
    )

    for page_number in range(1, 10):
        scraper.scrape_page(page_number)


if __name__ == "__main__":
    main()
