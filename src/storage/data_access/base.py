from abc import ABC, abstractmethod

from src.scrapers.schemas.base import ParsedDatasetModel


class BaseRepository(ABC):
    @abstractmethod
    def insert_bulk(self, data: ParsedDatasetModel) -> None:
        pass

    @abstractmethod
    def get_bulk_by_insertion_timestamp(self):
        pass

    @abstractmethod
    def delete_bulk(self) -> None:
        pass
