from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime

from src.enums import Bookmaker
from src.models.football_match import FootballMatchModel


@dataclass(slots=True)
class FootballMatch:
    event_time: datetime
    team_a: str
    team_b: str
    bet_options: dict[str, float]
    scrape_id: str
    source: Bookmaker
    scrape_start_timestamp: datetime
    scrape_end_timestamp: datetime

    team_a_standardized: str = field(default="")
    team_b_standardized: str = field(default="")

    @classmethod
    def from_bytes(cls, data: bytes) -> FootballMatch:
        decoded_data = data.decode("utf-8")
        match_data = json.loads(decoded_data)

        match_data["event_time"] = datetime.fromisoformat(match_data["event_time"])
        match_data["scrape_start_timestamp"] = datetime.fromisoformat(
            match_data["scrape_start_timestamp"]
        )
        match_data["scrape_end_timestamp"] = datetime.fromisoformat(
            match_data["scrape_end_timestamp"]
        )

        return cls(**match_data)

    def to_sqlalchemy_model(self) -> FootballMatchModel:
        match_dict = asdict(self)
        return FootballMatchModel(**match_dict)
