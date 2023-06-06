from abc import ABC, abstractmethod
from datetime import datetime

from src.database import get_database
from src.scrapers.schemas.base import ParsedDatasetModel
from src.storage.models import Scrape


class BaseRepository(ABC):
    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def get(self):
        pass


class SqliteRepository(BaseRepository):
    def __init__(self):
        self.db = get_database()

    def add(self, data: ParsedDatasetModel):
        data = Scrape(
            scrape_id=data.scrape_id.hex,
            source=data.source.value,
            scrape_start_timestamp=data.scrape_start_timestamp,
            scrape_end_timestamp=data.scrape_end_timestamp,
            data=data.data,
        )
        self.db.add(data)
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def get(self, timestamp: datetime) -> ...:
        ...


class MongoDbRepository(BaseRepository):
    def add(self):
        ...

    def get(self):
        ...
