import argparse
import logging
import os

from .scraper import Scraper


def main():
    parser = argparse.ArgumentParser(description="SS.com scraper")
    parser.add_argument("--dry-run", action="store_true", help="Skip DB inserts")
    args = parser.parse_args()

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] - %(message)s",
    )

    scraper = Scraper(dry_run=args.dry_run)
    scraper.run()


if __name__ == "__main__":
    main()
