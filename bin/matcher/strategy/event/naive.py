from typing import Generator

from src.enums import Bookmaker
from src.matcher.strategy.entity import EntityMatcherModel
from src.matcher.strategy.event.base import (
    BaseEventMatchingStrategy,
    BookmakersDatasets,
)
from scrapers.src.schemas import ScrapeResultModelEnriched


class NaiveEventMatchingStrategy(BaseEventMatchingStrategy):
    """Pick the shortest list check each element vs the rest ~~stupid."""

    @staticmethod
    def _separate_smallest_bookmaker_dataset(
        data: BookmakersDatasets,
    ) -> tuple[list[ScrapeResultModelEnriched], BookmakersDatasets]:
        _data = data.copy()
        smallest_bookmaker_dataset_key: Bookmaker = min(_data, key=lambda k: len(data[k]))
        bookmaker_data = _data.pop(smallest_bookmaker_dataset_key)
        return bookmaker_data, _data

    def match_events(
        self, datasets: BookmakersDatasets
    ) -> Generator[tuple[EntityMatcherModel, EntityMatcherModel], None, None]:
        (
            smallest_bookmaker_dataset,
            rest_of_bookmakers_dataset,
        ) = self._separate_smallest_bookmaker_dataset(datasets)

        for event_data in smallest_bookmaker_dataset:
            event = EntityMatcherModel(bookmaker=event_data.source, match_data=event_data)
            for list_of_events in rest_of_bookmakers_dataset.values():
                for _event_data in list_of_events:
                    _event = EntityMatcherModel(bookmaker=_event_data.source, match_data=_event_data)
                    yield event, _event
