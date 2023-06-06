import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import uuid4

from src.scrapers.schemas.base import ParsedDatasetModel

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)


class BaseScrapper(ABC):
    def __init__(self,):
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self.scrape_id = uuid4()
        self.scrapping_start_timestamp = datetime.utcnow()

        self._logger.info(f'Starting {self.__class__.__qualname__} job with id: {self.scrape_id}')

    @abstractmethod
    def scrape(self):
        ...

    @abstractmethod
    def save_data_to_database(self, data: ParsedDatasetModel, database: Any) -> None:
        ...
