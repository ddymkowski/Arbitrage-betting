from abc import ABC, abstractmethod

from src.schemas.consumer_match import FootballMatch
from src.services.matching.data import Batch


class BaseEventMatchingStrategy(ABC):
    @abstractmethod
    def match_events(
        self, bookmaker_batches: dict[str, Batch]
    ) -> list[list[FootballMatch]]:
        pass
