from dataclasses import dataclass

from src.schemas.consumer_match import FootballMatch


@dataclass
class Batch:
    count: int
    matches: list[FootballMatch]
