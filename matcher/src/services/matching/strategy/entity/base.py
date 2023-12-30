from abc import ABC, abstractmethod

from src.schemas.consumer_match import FootballMatch


class BaseEntityMatchingStrategy(ABC):
    @abstractmethod
    def match_entities(
        self, first_entity: FootballMatch, second_entity: FootballMatch
    ) -> bool:
        pass
