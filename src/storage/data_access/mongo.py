from src.scrapers.schemas.base import ParsedDatasetModel
from src.storage.data_access.base import BaseRepository


# TODO
class MongoDbRepository(BaseRepository):
    def insert_bulk(self, data: ParsedDatasetModel):
        pass

    def get_bulk_by_insertion_timestamp(self):
        pass

    def delete_bulk(self):
        pass
