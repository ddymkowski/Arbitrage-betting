from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.enums import Bookmaker
from src.scrapers.schemas.base import ScrapeResultModel


@dataclass
class EntityMatcherModel:
    bookmaker: Bookmaker
    match_data: ScrapeResultModel


class BaseEntityMatchingStrategy(ABC):
    @abstractmethod
    def match_entities(self, first_entity: EntityMatcherModel, second_entity: EntityMatcherModel) -> bool:
        pass
