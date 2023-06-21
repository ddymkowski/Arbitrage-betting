from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.engine.models import Odds
from src.enums import Bookmaker, FootballOutcome


class ScrapeResultModel(BaseModel):
    event_time: datetime
    team_a: str
    team_b: str
    bet_options: dict[FootballOutcome, Odds]


class ParsedDatasetModel(BaseModel):
    scrape_id: UUID
    source: Bookmaker
    scrape_start_timestamp: datetime
    scrape_end_timestamp: datetime
    data: list[ScrapeResultModel]

    class Config:
        orm_mode = True
