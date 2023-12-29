from abc import ABC, abstractmethod
from typing import Generator

from src.schemas.consumer_match import FootballMatch
from src.services.matching.data import Batch


class BaseEventMatchingStrategy(ABC):
    @abstractmethod
    def match_events(
        self, datasets: dict[str, Batch]
    ) -> Generator[tuple[FootballMatch, FootballMatch], None, None]:
        pass
