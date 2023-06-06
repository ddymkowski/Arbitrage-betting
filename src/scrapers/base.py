import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from pprint import pformat
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from src.scrapers.schemas.base import ParsedDatasetModel, ScrapeResultModel
from src.storage.data_access.sqlite import SqliteRepository

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)


class BaseScrapper(ABC):
    def __init__(
        self,
    ):
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self.scrape_id = uuid4()
        self.scrapping_start_timestamp = datetime.utcnow()

        self._logger.info(
            f"Starting {self.__class__.__qualname__} job with id: {self.scrape_id}"
        )

    @abstractmethod
    def parse_raw_datapoint(self) -> ParsedDatasetModel:
        ...

    @abstractmethod
    def get_raw_api_data(self) -> list[dict[Any, Any]]:
        ...

    def save_data_to_database(self, data: ParsedDatasetModel) -> None:
        self._logger.info(f"ID: {data.scrape_id} Saving: {len(data.data)} data points.")
        db = SqliteRepository()
        db.add_bulk(data)

    def _standardize_api_data(
        self, raw_data: list[dict[Any, Any]], scrapping_start_timestamp: datetime
    ) -> list[ScrapeResultModel]:
        normalized_data = []
        validation_errors = 0
        exceptions = []

        for raw_match_data in raw_data:
            try:
                normalized_data.append(
                    self.parse_raw_datapoint(
                        raw_match=raw_match_data,
                        scrape_timestamp=scrapping_start_timestamp,
                    )
                )
            except (ValidationError, IndexError, KeyError):
                validation_errors += 1
                exceptions.append(traceback.format_exc())

        self._logger.warning(f"Validation errors count: {validation_errors}.\n")
        self._logger.info(f"Successfully parsed: {len(normalized_data)} matches.\n")

        if validation_errors > 0.5 * len(raw_data):
            self._logger.error(
                "More than 50% of raw data could not be parsed properly check logs."
            )
            self._logger.error(f"{'---' * 20} \n {pformat(exceptions)} {'---' * 20} \n")

        return normalized_data

    async def scrape(self):
        raw_data = await self.get_raw_api_data()

        normalized_data = self._standardize_api_data(
            raw_data, self.scrapping_start_timestamp
        )
        if not normalized_data:
            self._logger.error(
                f"ID: {self.scrape_id}: No data was saved - check logs.\n"
            )

        data_dump = ParsedDatasetModel(
            data=normalized_data,
            scrape_id=self.scrape_id,
            source=self.BOOKMAKER_NAME,
            scrape_start_timestamp=self.scrapping_start_timestamp,
            scrape_end_timestamp=datetime.utcnow(),
        )
        self.save_data_to_database(data=data_dump)
