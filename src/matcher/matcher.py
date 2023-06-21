import logging

from src.matcher.strategy.base import EntityMatcherModel
from src.matcher.strategy.naive import BaseEntityMatchingStrategy, NaiveMatchingStrategy
from src.scrapers.schemas.base import ParsedDatasetModel, ScrapeResultModel
from src.storage.data_access.base import BaseRepository
from src.storage.data_access.sqlite import SqliteRepository

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)

ALLOWED_SCRAPE_TIMEDELTA_SECONDS = 60


class MatchMatcher:
    def __init__(self, database: BaseRepository = SqliteRepository()) -> None:
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self._database = database

    def _validate_batches_timestamps(self, timestamps: list[dict[str, str]]) -> list[str]:
        sorted_datetimes = sorted(timestamps, key=lambda entry: entry["scrape_end_time"])
        time_deltas = [
            (
                sorted_datetimes[i + 1]["scrape_end_time"] - sorted_datetimes[i]["scrape_end_time"],
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
            return []
        return [entry["scrape_id"] for entry in timestamps]

    def filter_and_sort_newest_batches(self) -> list[ParsedDatasetModel]:
        data = self._database.get_most_recent_bulks()
        scrape_id_timestamp = [
            {
                "scrape_id": model.scrape_id,
                "scrape_end_time": model.scrape_end_timestamp,
            }
            for model in data
        ]
        ids_to_use = self._validate_batches_timestamps(scrape_id_timestamp)

        return sorted(filter(lambda d: d.scrape_id in ids_to_use, data), key=lambda x: len(x.data))

    @staticmethod
    def _find_match(
        match: ScrapeResultModel,
        other_scrape_results: list[ParsedDatasetModel],
        matching_strategy: BaseEntityMatchingStrategy,
    ) -> tuple[ScrapeResultModel]:
        for result in other_scrape_results:
            for _match in result.data:
                _match = EntityMatcherModel(bookmaker=result.source, match_data=_match)
                if matching_strategy.match_entities(match, _match):
                    return match, _match
        return None

        return 0

    def match_entities(self):
        matching_strategy = NaiveMatchingStrategy()

        packed_data = self.filter_and_sort_newest_batches()

        main, others = packed_data[0], packed_data[1:]  # naive take the shortest list and map others to it

        for entry in main.data:
            compare_entity = EntityMatcherModel(bookmaker=main.source, match_data=entry)
            if result := self._find_match(compare_entity, others, matching_strategy):
                results.append(result)

        # TODO fix this retarded scrape data model, split entries. [just json instead of list[json]]
        matched_count = len(results)
        main_count = len(main.data)
        self._logger.info(
            "%s matched %s out of %s entries (%s%%)",
            matching_strategy.__class__.__name__,
            matched_count,
            main_count,
            round(matched_count / main_count * 100, 2),
        )

if __name__ == "__main__":
    matcher = MatchMatcher()
    matcher.match_entities()
