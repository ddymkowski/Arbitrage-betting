import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from pprint import pformat
from typing import Any, Generic, TypeVar
from uuid import uuid4

from pydantic import ValidationError

from src.scrapers.schemas.base import ParsedDatasetModel, ScrapeResultModel
from src.storage.data_access.base import BaseRepository
from src.storage.data_access.sqlite import SqliteRepository

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)

T = TypeVar("T")


class BaseScrapper(ABC, Generic[T]):
    def __init__(self, database: BaseRepository = SqliteRepository()):
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self._database = database
        self.scrape_id = uuid4()
        self.scrapping_start_timestamp = datetime.utcnow()

        self._logger.info(
            f"Starting {self.__class__.__qualname__} job with id: {self.scrape_id}"
        )

    @abstractmethod
    async def acquire_data(self) -> T:
        pass

    def transform_data(self, raw_data: T) -> ParsedDatasetModel:
        standardized_api_data: list[ScrapeResultModel] = self._standardize_api_data(
            raw_data
        )

        data_dump = ParsedDatasetModel(
            data=standardized_api_data,
            scrape_id=self.scrape_id,
            source=self.BOOKMAKER_NAME,
            scrape_start_timestamp=self.scrapping_start_timestamp,
            scrape_end_timestamp=datetime.utcnow(),
        )
        return data_dump

    def save_data(self, transformed_data: ParsedDatasetModel) -> None:
        self._logger.info(
            f"ID: {transformed_data.scrape_id} Saving: {len(transformed_data.data)} data points."
        )
        self._database.insert_bulk(transformed_data)

    @abstractmethod
    def _parse_raw_datapoint(self) -> ScrapeResultModel:
        pass

    def _standardize_api_data(
        self, raw_data: list[dict[Any, Any]]
    ) -> list[ScrapeResultModel]:
        standardized_data = []
        validation_errors = 0
        exceptions = []

        for raw_match_data in raw_data:
            try:
                standardized_data.append(
                    self._parse_raw_datapoint(
                        raw_match=raw_match_data,
                        scrape_timestamp=self.scrapping_start_timestamp,
                    )
                )
            except (ValidationError, IndexError, KeyError):
                validation_errors += 1
                exceptions.append(traceback.format_exc())

        self._logger.warning(f"Validation errors count: {validation_errors}.\n")
        self._logger.info(f"Successfully parsed: {len(standardized_data)} matches.\n")

        if validation_errors > 0.5 * len(raw_data):
            self._logger.error(
                "More than 50% of raw data could not be parsed properly check logs."
            )
            self._logger.error(f"{'---' * 20} \n {pformat(exceptions)} {'---' * 20} \n")

        return standardized_data

    async def scrape(self):
        raw_data = await self.acquire_data()
        transformed_data = self.transform_data(raw_data)
        self.save_data(transformed_data)
