from abc import ABC, abstractmethod
from typing import Generator

from src.matcher.schemas import BookmakersDatasets, EntityMatcherModel


class BaseEventMatchingStrategy(ABC):
    @abstractmethod
    def match_events(
        self, datasets: BookmakersDatasets
    ) -> Generator[tuple[EntityMatcherModel, EntityMatcherModel], None, None]:
        pass
