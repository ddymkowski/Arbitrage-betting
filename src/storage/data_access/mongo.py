from src.scrapers.schemas.base import ScrapeResultModelEnriched
from src.storage.data_access.base import BaseRepository


# TODO
class MongoDbRepository(BaseRepository):
    def insert_bulk(self, data: list[ScrapeResultModelEnriched]):
        pass

    def get_most_recent_bulks(self):
        pass

    def delete_bulk(self):
        pass
