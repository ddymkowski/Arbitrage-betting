from abc import ABC, abstractmethod

from src.matcher.schemas import EntityMatcherModel


class BaseEntityMatchingStrategy(ABC):
    @abstractmethod
    def match_entities(self, first_entity: EntityMatcherModel, second_entity: EntityMatcherModel) -> bool:
        pass
