from datetime import datetime

from pydantic import BaseModel

from src.engine.engine import ArbitrageEngine
from src.engine.models import BetOptions, FootballMatch, Odds
from src.enums import Bookmaker, FootballOutcome


class EntrypointDataModel(BaseModel):
    event_time: datetime
    team_a: str
    team_b: str
    bet_options: dict[FootballOutcome, BetOptions]


test_data = {
    "event_time": datetime.utcnow(),
    "team_a": "real",
    "team_b": "city",
    "bet_options": {
        FootballOutcome.TEAM_A_WINS: BetOptions(
            {
                Bookmaker.BETCLIC: Odds(1.60),
                Bookmaker.LVBET: Odds(1.80),
                Bookmaker.STS: Odds(1.90),
            }
        ),
        FootballOutcome.DRAW: BetOptions(
            {
                Bookmaker.BETCLIC: Odds(3.0),
                Bookmaker.LVBET: Odds(3.20),
                Bookmaker.STS: Odds(3.10),
            }
        ),
        FootballOutcome.TEAM_B_WINS: BetOptions(
            {
                Bookmaker.BETCLIC: Odds(8.00),
                Bookmaker.LVBET: Odds(5.0),
                Bookmaker.STS: Odds(4.0),
            }
        ),
    },
}

data = EntrypointDataModel(**test_data)

match = FootballMatch(**data.dict())
engine = ArbitrageEngine()

engine.process_event(match, 1000)
