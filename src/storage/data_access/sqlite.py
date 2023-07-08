from sqlalchemy.sql.expression import func

from src.database import get_database
from src.scrapers.schemas.base import ScrapeResultModelEnriched
from src.storage.data_access.base import BaseRepository
from src.storage.models import Scrape


class SqliteRepository(BaseRepository):
    def __init__(self) -> None:
        self._session = get_database()

    def insert_bulk(self, data: list[ScrapeResultModelEnriched]):
        models = [
            Scrape(
                scrape_id=result.scrape_id.hex,
                source=result.source,
                scrape_start_timestamp=result.scrape_start_timestamp,
                scrape_end_timestamp=result.scrape_end_timestamp,
                team_a=result.team_a,
                team_b=result.team_b,
                event_time=result.event_time,
                bet_options=result.bet_options,
            )
            for result in data
        ]

        self._session.bulk_save_objects(models)
        try:
            self._session.commit()
        except Exception as err:  # noqa
            self._session.rollback()
            raise err

    def get_most_recent_bulks(self) -> list[ScrapeResultModelEnriched]:
        subquery = (
            self._session.query(Scrape.source, func.max(Scrape.insertion_timestamp).label("max_date"))
            .group_by(Scrape.source)
            .subquery()
        )

        ids_subquery = (
            self._session.query(Scrape.scrape_id)
            .join(
                subquery,
                (Scrape.insertion_timestamp == subquery.c.max_date) & (Scrape.source == subquery.c.source),
            )
            .subquery()
        )

        query = self._session.query(Scrape).filter(Scrape.scrape_id.in_(ids_subquery.select()))

        return [ScrapeResultModelEnriched.from_orm(model) for model in query.all()]

    def delete_bulk(self) -> None:
        pass
