import logging

from scraper import Scraper


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [INFO] - %(message)s",
    )

    scraper = Scraper()


if __name__ == "__main__":
    main()
