from enum import Enum


class Bookmaker(str, Enum):
    BETCLIC = "BETCLIC"
    LVBET = "LVBET"
    FORTUNA = "FORTUNA"
