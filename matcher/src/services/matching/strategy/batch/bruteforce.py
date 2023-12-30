from itertools import combinations, product
from typing import Generator

from src.schemas.consumer_match import FootballMatch
from src.services.matching.data import Batch
from src.services.matching.strategy.batch.base import BaseEventMatchingStrategy


class BruteForceMatchingStrategy(BaseEventMatchingStrategy):
    MINIMUM_CLUSTER_LENGTH = 3

    def __init__(self, entity_comparison_strategy):
        self._entity_comparison_strategy = entity_comparison_strategy

    def match_events(
        self, bookmaker_batches: dict[str, Batch]
    ) -> list[list[FootballMatch]]:
        """
        1. Pick the largest batch.
        2. Iterate over other batches (input minus largest batch).
        3. Try to match football event from "largest batch" and "current batch". If matched add it "club_cluster"
            (container for the same football events from different bookmakers) and delete it from "current batch" so it
            is not used in next iterations.
        4. After iterating over all entries from "other batches", if club_cluster contains more than 3 (number of
            football event outcomes) entries add it to final results.
        """

        data = bookmaker_batches.copy()

        bookmaker_name_with_most_listings: str = max(data, key=lambda x: data[x].count)
        longest_data: Batch = data.pop(bookmaker_name_with_most_listings)

        clusters: list[list[FootballMatch]] = []
        for match in longest_data.matches:
            club_cluster: list[FootballMatch] = [match]
            for bookmaker in data.keys():
                _matches = data[bookmaker].matches
                for _match in _matches:
                    if self._entity_comparison_strategy.match_entities(match, _match):
                        club_cluster.append(_match)
                        _matches.remove(_match)
                        continue

            if len(club_cluster) >= self.MINIMUM_CLUSTER_LENGTH:
                clusters.append(club_cluster)

        return clusters
