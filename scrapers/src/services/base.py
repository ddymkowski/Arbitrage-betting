import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from pprint import pformat
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import ValidationError
from src.enums import Bookmaker
from src.schemas.base import FootballMatchData, FootballMatchDataDTO

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)

RD = TypeVar("RD", bound=Any)
Serializable = dict[str, Any]


class BaseScrapingService(ABC, Generic[RD]):
    @property
    @abstractmethod
    def bookmaker(self) -> Bookmaker:
        pass

    def __init__(
        self,
    ):
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self._scrape_id = uuid4()
        self._scrapping_start_timestamp = datetime.utcnow()

        self._logger.info(
            "Starting %s job with id: %s",
            {self.__class__.__qualname__},
            {self._scrape_id},
        )

    @property
    def scrape_id(self) -> UUID:
        return self._scrape_id

    @abstractmethod
    async def acquire_raw_data(self) -> RD:
        pass

    @abstractmethod
    def preprocess_raw_data(self, raw_data: RD) -> list[Serializable]:
        pass

    @abstractmethod
    def serialize_datapoint(self, raw_datapoint: Serializable) -> FootballMatchData:
        pass

    def _enrich_data_with_scrape_metadata(
        self, serialized_data: list[FootballMatchData]
    ) -> list[FootballMatchDataDTO]:
        scrape_end_timestamp = datetime.utcnow()
        enriched_db_ready_data = [
            FootballMatchDataDTO(
                event_time=scrape_result.event_time,
                team_a=scrape_result.team_a,
                team_b=scrape_result.team_b,
                bet_options=scrape_result.bet_options,
                scrape_id=self._scrape_id,
                source=self.bookmaker,
                scrape_start_timestamp=self._scrapping_start_timestamp,
                scrape_end_timestamp=scrape_end_timestamp,
            )
            for scrape_result in serialized_data
        ]
        return enriched_db_ready_data

    def _serialize_data(
        self, serializable_data: list[Serializable]
    ) -> list[FootballMatchData]:
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
        self._logger.info(
            "Successfully parsed: %s matches.\n", {len(standardized_data)}
        )

        if exceptions_count > (0.5 * len(serializable_data)):
            self._logger.error(
                "More than 50% of raw data could not be parsed properly check logs."
            )
            self._logger.error({pformat(exceptions)})

        return standardized_data

    async def scrape(self) -> list[FootballMatchDataDTO]:
        raw_data: RD = await self.acquire_raw_data()
        serializable_data: list[Serializable] = self.preprocess_raw_data(raw_data)
        serialized_data: list[FootballMatchData] = self._serialize_data(
            serializable_data
        )
        enriched_serialized_data: list[
            FootballMatchDataDTO
        ] = self._enrich_data_with_scrape_metadata(serialized_data)
        return enriched_serialized_data
