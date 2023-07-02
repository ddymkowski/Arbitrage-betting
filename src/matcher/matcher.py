import logging

from src.enums import Bookmaker
from src.matcher.strategy.base import EntityMatcherModel
from src.matcher.strategy.naive import BaseEntityMatchingStrategy, NaiveMatchingStrategy
from src.scrapers.schemas.base import ScrapeResultModel, ScrapeResultModelEnriched
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
        strategy: BaseEntityMatchingStrategy = NaiveMatchingStrategy(),
    ) -> None:
        self._strategy = strategy
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

    def get_newest_batches(self) -> dict[Bookmaker, list[ScrapeResultModelEnriched]]:
        data = self._database.get_most_recent_bulks()
        bookmaker_data: dict[Bookmaker, list[ScrapeResultModelEnriched]] = {bookmaker: [] for bookmaker in Bookmaker}

        for datapoint in sorted(data, key=lambda x: x.scrape_end_timestamp):
            bookmaker_data[datapoint.source].append(datapoint)

        return {key: value for key, value in bookmaker_data.items() if value}

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

    @staticmethod
    def _find_match(
        match: ScrapeResultModelEnriched,
        potential_matches: list[ScrapeResultModelEnriched],
        matching_strategy: BaseEntityMatchingStrategy,
    ) -> tuple[ScrapeResultModel]:
        match = EntityMatcherModel(bookmaker=match.source, match_data=match)
        for _match in potential_matches:
            _match = EntityMatcherModel(bookmaker=_match.source, match_data=_match)
            if matching_strategy.match_entities(match, _match):
                return match, _match
        return None

    def match_entities(self):
        data: dict[Bookmaker, list[ScrapeResultModelEnriched]] = self.get_newest_batches()
        self._validate_timestamps_for_batches(data)

        smallest_bookmaker_dataset_key: str = min(data, key=lambda k: len(data[k]))
        bookmaker_data = data.pop(smallest_bookmaker_dataset_key)

        results = []
        for match_data in bookmaker_data:
            for list_of_matches in data.values():
                if (matched_data := self._find_match(match_data, list_of_matches, self._strategy)) is not None:
                    results.append(matched_data)

        matched_count = len(results)
        main_count = sum(len(lst) for lst in data.values())
        self._logger.info(
            "%s matched %s out of %s entries (%s%%)",
            self._strategy.__class__.__name__,
            matched_count,
            main_count,
            round(matched_count / main_count * 100, 2),
        )


if __name__ == "__main__":
    matcher = MatchMatcher()
    matcher.match_entities()
