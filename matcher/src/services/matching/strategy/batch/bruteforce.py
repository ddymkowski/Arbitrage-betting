from itertools import combinations, product
from typing import Generator

from src.schemas.consumer_match import FootballMatch
from src.services.matching.data import Batch
from src.services.matching.strategy.batch.base import BaseEventMatchingStrategy


class BruteForceMatchingStrategy(BaseEventMatchingStrategy):
    def match_events(
        self, datasets: dict[str, Batch]
    ) -> Generator[tuple[FootballMatch, FootballMatch], None, None]:
        lists = []
        for batch in datasets.values():
            lists.append(batch.matches)

        list_combinations = list(combinations(lists, 2))
        result = []
        for list_pair in list_combinations:
            pairs = product(*list_pair)
            result.extend(pairs)

        for match_a, match_b in result:
            yield match_a, match_b
