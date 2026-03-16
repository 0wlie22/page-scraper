import unittest
from unittest.mock import MagicMock
from typing import cast

from src.apartment import Appartment
from src.scraper import Scraper


class AppartmentValidationTests(unittest.TestCase):
    def test_valid_cost_in_range(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="")
        self.assertTrue(apartment.set_cost("Price 60000"))

    def test_valid_cost_below_min(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="")
        self.assertFalse(apartment.set_cost("Price 40000"))

    def test_valid_cost_above_max(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="")
        self.assertFalse(apartment.set_cost("Price 140000"))

    def test_valid_cost_bad_format(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="")
        self.assertFalse(apartment.set_cost("invalid"))

    def test_valid_floor_int_in_range(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertTrue(apartment.set_floor(["3", "5"]))

    def test_valid_floor_actual_below_min(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertFalse(apartment.set_floor(["2", "5"]))

    def test_valid_floor_max_below_min(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertFalse(apartment.set_floor(["3", "2"]))

    def test_valid_floor_actual_above_max(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertFalse(apartment.set_floor(["6", "5"]))

    def test_valid_floor_actual_equals_max(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertFalse(apartment.set_floor(["5", "5"]))

    def test_valid_floor_missing(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertFalse(apartment.set_floor([]))

    def test_valid_floor_bad_format(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertFalse(apartment.set_floor(["floor", "max"]))

    def test_floor_display_with_max(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        apartment.set_floor(["7", "9"])
        self.assertEqual(apartment.floor_display(), "7/9")

    def test_valid_rooms_match(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertTrue(apartment.set_rooms("3"))

    def test_valid_rooms_mismatch(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertFalse(apartment.set_rooms("2"))

    def test_valid_rooms_bad_format(self):
        apartment = Appartment(id="", index=1, url="", coordinates=("0", "0"), price="Price 60000")
        self.assertFalse(apartment.set_rooms("two"))


class ScraperValidationTests(unittest.TestCase):
    def test_valid_neighbourhood_inside_bad_polygon(self):
        scraper = Scraper.__new__(Scraper)
        polygon = MagicMock(spec=["contains"])
        polygon.contains.return_value = True
        scraper.bad_coordinates = cast(list, [polygon])
        self.assertFalse(scraper.validNeighbourhood(("1", "1")))
        polygon.contains.assert_called_once()


if __name__ == "__main__":
    unittest.main()
