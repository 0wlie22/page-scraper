import logging
from typing import List, Optional, Tuple

from config import MAX_COST, MIN_COST, MIN_FLOOR, ROOMS, MIN_ROOMS


class Appartment:
    def __init__(
        self, id: str, index: int, url: str, coordinates: Tuple[str, str], price: str
    ):
        self.id = id
        self.index = index
        self.coordinates = coordinates
        self.url = url
        self.price = price
        self.floor: Optional[List[str]] = None
        self.rooms: Optional[str] = None
        self.address: Optional[str] = None
        self.neighbourhood: Optional[str] = None

    def __str__(self):
        return f"Nr: {self.index}, URL: {self.url}, Price: {self.price}\n"

    def set_cost(self, price: str) -> bool:
        self.price = price
        try:
            amount = int(self.price.split(" ")[1].replace(",", ""))
            if amount <= MAX_COST and amount >= MIN_COST:
                return True
        except Exception:
            logging.debug("Invalid cost value: %s", self.price)
            return False
        logging.debug("Cost out of range: %s", self.price)
        return False

    def set_floor(self, floor: List[str]) -> bool:
        self.floor = floor
        if not self.floor:
            logging.debug("Invalid floor value: %s", self.floor)
            return False
        try:
            actual_floor = int(self.floor[0])
            max_floor = int(self.floor[1]) if len(self.floor) > 1 else None
        except ValueError:
            try:
                actual_floor = float(self.floor[0])
                max_floor = float(self.floor[1]) if len(self.floor) > 1 else None
            except ValueError:
                logging.debug("Invalid floor value: %s", self.floor)
                return False

        if max_floor is not None and max_floor < MIN_FLOOR:
            logging.debug("Floor max below minimum: %s", self.floor)
            return False

        if max_floor is not None and actual_floor >= max_floor:
            logging.debug("Floor is last or above max: %s", self.floor)
            return False

        if actual_floor >= MIN_FLOOR and (
            max_floor is None or actual_floor <= max_floor
        ):
            return True
        logging.debug("Floor below minimum: %s", self.floor)
        return False

    def set_rooms(self, rooms: str) -> bool:
        self.rooms = rooms
        if self.rooms is None:
            logging.debug("Invalid rooms value: %s", self.rooms)
            return False
        try:
            rooms_value = int(self.rooms)
        except ValueError:
            logging.debug("Invalid rooms value: %s", self.rooms)
            return False

        if rooms_value < MIN_ROOMS or rooms_value > ROOMS:
            logging.debug("Rooms count not matching: %s", self.rooms)
            return False
        return rooms_value == ROOMS

    def floor_display(self) -> str:
        if not self.floor:
            return ""
        if len(self.floor) > 1:
            return f"{self.floor[0]}/{self.floor[1]}"
        return self.floor[0]

    def print(self):
        print(
            " | ".join(
                [
                    self.neighbourhood or "",
                    self.address or "",
                    self.floor_display(),
                    self.price.split(" ")[1] if self.price else "",
                    self.url,
                ]
            )
        )
