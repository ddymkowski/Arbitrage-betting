from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.enums import Bookmaker, FootballOutcome
from src.engine.models import Odds


class MatchModel(BaseModel):
    event_time: datetime
    team_a: str
    team_b: str
    bet_options: dict[FootballOutcome, Odds]

    # class Config:
    #     json_encoders = {datetime: lambda o: o.isoformat()}


class ParsedDatasetModel(BaseModel):
    scrape_id: UUID
    source: Bookmaker
    scrape_start_timestamp: datetime
    scrape_end_timestamp: datetime
    data: list[MatchModel]

    # class Config:
    #     json_encoders = {datetime: lambda o: o.isoformat()}
    #
