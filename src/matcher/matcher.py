import logging

from src.enums import Bookmaker
from src.matcher.strategy.event import (
    BaseEventMatchingStrategy,
    NaiveEventMatchingStrategy,
)
from src.matcher.strategy.entity import (
    BaseEntityMatchingStrategy,
    NaiveEntityMatchingStrategy,
)
from src.scrapers.schemas.base import ScrapeResultModelEnriched
from src.storage.data_access.base import BaseRepository
from src.storage.data_access.sqlite import SqliteRepository

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)

ALLOWED_SCRAPE_TIMEDELTA_SECONDS = 60


class MatchMatcher:
    def __init__(
        self,
        database: BaseRepository = SqliteRepository(),
        entity_matching_strategy: BaseEntityMatchingStrategy = NaiveEntityMatchingStrategy(),
        event_matching_strategy: BaseEventMatchingStrategy = NaiveEventMatchingStrategy(),
    ) -> None:
        self._entity_matching_strategy = entity_matching_strategy
        self._event_matching_strategy = event_matching_strategy
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self._database = database

    def _check_timedelta(self, timestamps: list[dict[str, str]]) -> None:
        sorted_datetimes = sorted(timestamps, key=lambda entry: entry["scrape_end_timestamp"])
        time_deltas = [
            (
                sorted_datetimes[i + 1]["scrape_end_timestamp"] - sorted_datetimes[i]["scrape_end_timestamp"],
                sorted_datetimes[i]["scrape_id"],
                sorted_datetimes[i + 1]["scrape_id"],
            )
            for i in range(len(sorted_datetimes) - 1)
        ]

        biggest_delta, id1, id2 = max(time_deltas, key=lambda timedelta_id: timedelta_id[0])

        self._logger.info("Biggest time delta: %s", {biggest_delta})
        self._logger.info("IDs with the biggest gap: %s %s", {id1}, {id2})

        if biggest_delta.total_seconds() > ALLOWED_SCRAPE_TIMEDELTA_SECONDS:
            self._logger.warning(
                "Delta between scrapes is bigger than %s seconds, skipping.",
                {ALLOWED_SCRAPE_TIMEDELTA_SECONDS},
            )
            # TODO add some handling
            print("marking event as cancelled")

    @staticmethod
    def _split_and_sort_data_by_bookmaker(
        database_data: list[ScrapeResultModelEnriched],
    ) -> dict[Bookmaker, list[ScrapeResultModelEnriched]]:
        bookmaker_data: dict[Bookmaker, list[ScrapeResultModelEnriched]] = {bookmaker: [] for bookmaker in Bookmaker}

        for datapoint in sorted(database_data, key=lambda x: x.scrape_end_timestamp):
            bookmaker_data[datapoint.source].append(datapoint)

        return {key: value for key, value in bookmaker_data.items() if value}

    def _get_newest_batches(self) -> dict[Bookmaker, list[ScrapeResultModelEnriched]]:
        database_data: list[ScrapeResultModelEnriched] = self._database.get_most_recent_bulks()
        preprocessed_data = self._split_and_sort_data_by_bookmaker(database_data)
        self._logger.info(
            "Received bookmakers: %s, their datasets lengths: %s",
            preprocessed_data.keys(),
            [len(data) for data in preprocessed_data.values()],
        )
        return preprocessed_data

    def _validate_timestamps_for_batches(self, bookmaker_data):
        bookmaker_scrape_end = {bookmaker: None for bookmaker in Bookmaker}
        for key, value in bookmaker_data.items():
            try:
                bookmaker_scrape_end[key] = {
                    "scrape_id": value[-1].scrape_id,
                    "scrape_end_timestamp": value[-1].scrape_end_timestamp,
                }
            except IndexError:
                pass  # Do nothing for bookmakers that are in Enum but are not scrapped or failed to scrap

        self._check_timedelta(
            [timestamp_id for timestamp_id in bookmaker_scrape_end.values() if timestamp_id is not None]
        )

    def match_entities(self):
        data: dict[Bookmaker, list[ScrapeResultModelEnriched]] = self._get_newest_batches()
        self._validate_timestamps_for_batches(data)  # TODO I dont like this function

        results = []
        for match, _match in self._event_matching_strategy.match_events(data):
            if self._entity_matching_strategy.match_entities(match, _match):
                results.append((match, _match))

        matched_count = len(results)
        main_count = sum(len(lst) for lst in data.values())
        self._logger.info(
            "%s & %s matched %s out of %s entries (%s%%)",
            self._event_matching_strategy.__class__.__qualname__,
            self._entity_matching_strategy.__class__.__qualname__,
            matched_count,
            main_count,
            round(matched_count / main_count * 100, 2),
        )


if __name__ == "__main__":
    matcher = MatchMatcher()
    matcher.match_entities()
