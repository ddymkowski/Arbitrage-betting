from src.database import get_database
from src.scrapers.schemas.base import ParsedDatasetModel
from src.storage.data_access.base import BaseRepository
from src.storage.models import Scrape


class SqliteRepository(BaseRepository):
    def __init__(self):
        self.db = get_database()

    def insert_bulk(self, data: ParsedDatasetModel):
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

    def get_bulk_by_insertion_timestamp(self):
        pass

    def delete_bulk(self):
        pass
