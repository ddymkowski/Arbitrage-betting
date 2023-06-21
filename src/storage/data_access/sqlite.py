from sqlalchemy.sql.expression import func

from src.database import get_database
from src.scrapers.schemas.base import ParsedDatasetModel
from src.storage.data_access.base import BaseRepository
from src.storage.models import Scrape


class SqliteRepository(BaseRepository):
    def __init__(self):
        self.session = get_database()

    def insert_bulk(self, data: ParsedDatasetModel):
        model = Scrape(
            scrape_id=data.scrape_id.hex,
            source=data.source.value,
            scrape_start_timestamp=data.scrape_start_timestamp,
            scrape_end_timestamp=data.scrape_end_timestamp,
            data=data.data,
        )
        self.session.add(model)
        try:
            self.session.commit()
        except Exception as err:  # noqa
            self.session.rollback()
            raise err

    def get_most_recent_bulks(self):
        subquery = (
            self.session.query(Scrape.source, func.max(Scrape.insertion_timestamp).label("max_date"))
            .group_by(Scrape.source)
            .subquery()
        )

        query = self.session.query(Scrape).join(
            subquery,
            (Scrape.source == subquery.c.source) & (Scrape.insertion_timestamp == subquery.c.max_date),
        )

        return [ParsedDatasetModel.from_orm(model) for model in query.all()]

    def delete_bulk(self):
        pass
