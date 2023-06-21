from abc import ABC, abstractmethod

from src.scrapers.schemas.base import ParsedDatasetModel


class BaseRepository(ABC):
    @abstractmethod
    def insert_bulk(self, data: ParsedDatasetModel) -> None:
        pass

    @abstractmethod
    def get_most_recent_bulks(self):
        pass

    @abstractmethod
    def delete_bulk(self) -> None:
        pass
