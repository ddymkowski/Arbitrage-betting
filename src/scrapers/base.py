import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from pprint import pformat
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import ValidationError

from src.enums import Bookmaker
from src.scrapers.schemas.base import ScrapeResultModel, ScrapeResultModelEnriched
from src.storage.data_access.base import BaseRepository
from src.storage.data_access.sqlite import SqliteRepository

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)

RD = TypeVar("RD", bound=Any)
Serializable = dict[str, Any]


class BaseScrapper(ABC, Generic[RD]):
    BOOKMAKER: Bookmaker

    @classmethod
    def __init_subclass__(cls, *args, **kwargs):
        var = "BOOKMAKER"
        if not hasattr(cls, var):
            raise NotImplementedError(f"Class {cls} lacks required `{var}` class attribute of type src.enums.Bookmaker")

    def __init__(self, database: BaseRepository = SqliteRepository()):
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self._database = database
        self.scrape_id = uuid4()
        self.scrapping_start_timestamp = datetime.utcnow()

        self._logger.info(
            "Starting %s job with id: %s",
            {self.__class__.__qualname__},
            {self.scrape_id},
        )

    @abstractmethod
    async def acquire_raw_data(self) -> RD:
        pass

    @abstractmethod
    def preprocess_raw_data(self, raw_data: RD) -> list[Serializable]:
        pass

    @abstractmethod
    def serialize_datapoint(self, raw_datapoint: Serializable) -> ScrapeResultModel:
        pass

    def _enrich_data_with_scrape_metadata(
        self, serialized_data: list[ScrapeResultModel]
    ) -> list[ScrapeResultModelEnriched]:
        scrape_end_timestamp = datetime.utcnow()
        enriched_db_ready_data = [
            ScrapeResultModelEnriched(
                event_time=scrape_result.event_time,
                team_a=scrape_result.team_a,
                team_b=scrape_result.team_b,
                bet_options=scrape_result.bet_options,
                scrape_id=self.scrape_id,
                source=self.BOOKMAKER_NAME,  # pylint: disable=no-member
                scrape_start_timestamp=self.scrapping_start_timestamp,
                scrape_end_timestamp=scrape_end_timestamp,
            )
            for scrape_result in serialized_data
        ]
        return enriched_db_ready_data

    def _serialize_data(self, serializable_data: list[Serializable]) -> list[ScrapeResultModel]:
        standardized_data = []
        exceptions = []

        for match_data in serializable_data:
            try:
                standardized_data.append(
                    self.serialize_datapoint(
                        raw_datapoint=match_data,
                    )
                )
            except (ValidationError, IndexError, KeyError):
                exceptions.append(traceback.format_exc())

        exceptions_count = len(exceptions)
        self._logger.warning("Validation errors count: %s\n", {exceptions_count})
        self._logger.info("Successfully parsed: %s matches.\n", {len(standardized_data)})

        if exceptions_count > (0.5 * len(serializable_data)):
            self._logger.error("More than 50% of raw data could not be parsed properly check logs.")
            self._logger.error({pformat(exceptions)})

        return standardized_data

    def save_data(self, transformed_data: list[ScrapeResultModelEnriched]) -> None:
        self._database.insert_bulk(transformed_data)

    async def scrape(self) -> None:
        raw_data: RD = await self.acquire_raw_data()
        serializable_data: list[Serializable] = self.preprocess_raw_data(raw_data)
        db_serialized_data: list[ScrapeResultModel] = self._serialize_data(serializable_data)
        enriched_db_serialized_data: list[ScrapeResultModelEnriched] = self._enrich_data_with_scrape_metadata(
            db_serialized_data
        )
        self.save_data(enriched_db_serialized_data)
