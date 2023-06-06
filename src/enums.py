from enum import Enum


class Bookmaker(str, Enum):
    BETCLIC = "BETCLIC"
    LVBET = "LVBET"
    STS = "STS"


class FootballOutcome(str, Enum):
    TEAM_A_WINS = "TEAM_A_WINS"
    DRAW = "DRAW"
    TEAM_B_WINS = "TEAM_B_WINS"


class PotentialBetState(str, Enum):
    RAW = "RAW"
    MASKED = "MASKED"
