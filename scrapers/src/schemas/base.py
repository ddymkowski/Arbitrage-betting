from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, validator

from src.enums import Bookmaker, FootballOutcome


class FootballMatchData(BaseModel):
    event_time: datetime
    team_a: str
    team_b: str
    bet_options: dict[FootballOutcome, float]

    @validator('bet_options')
    def validate_positive_floats(cls, v: dict[FootballOutcome, float]) -> dict[FootballOutcome, float]:
        for key, value in v.items():
            if value <= 0:
                raise ValueError("Odds cannot be equal or less than 0.0")
        return v


class FootballMatchDataDTO(FootballMatchData):
    scrape_id: UUID
    source: Bookmaker
    scrape_start_timestamp: datetime
    scrape_end_timestamp: datetime

    class Config:
        orm_mode = True
