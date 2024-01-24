import logging

from sqlalchemy.orm import Session
from src.data_access.base import SyncSQLAlchemyDataAccess
from src.schemas.consumer_match import FootballMatch
from src.services.matching.data import Batch
from src.services.matching.strategy.batch.base import BaseEventMatchingStrategy
from src.services.matching.strategy.batch.bruteforce import \
    BruteForceMatchingStrategy
from src.services.matching.strategy.entity.base import \
    BaseEntityMatchingStrategy
from src.services.matching.strategy.entity.exact import \
    ExactEntityComparisonStrategy


class FootballEventMatchingService:
    def __init__(
        self,
        data_access: SyncSQLAlchemyDataAccess,
        batch_matching_strategy: BaseEventMatchingStrategy = None,
        entity_matching_strategy: BaseEntityMatchingStrategy = None,
    ) -> None:
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self._data_access = data_access
        self._entity_matching_strategy = (
            entity_matching_strategy
            if entity_matching_strategy
            else ExactEntityComparisonStrategy()
        )
        self._batch_matching_strategy = (
            batch_matching_strategy
            if batch_matching_strategy
            else BruteForceMatchingStrategy(self._entity_matching_strategy)
        )

        self._logger.info(
            f"Using {self._batch_matching_strategy.__class__.__name__} and {self._entity_matching_strategy.__class__.__name__}."
        )

    @classmethod
    def from_session(cls, session: Session, **kwargs) -> "FootballEventMatchingService":
        return cls(data_access=SyncSQLAlchemyDataAccess(session), **kwargs)

    def _get_data(self) -> dict[str, dict[str, list[FootballMatch] | int]]:
        all_bookmakers: list[str] = self._data_access.get_distinct_bookmakers()

        data = {}
        for bookmaker in all_bookmakers:
            matches = self._data_access.get_bookmaker_newest_batch(bookmaker)
            data[bookmaker] = Batch(count=len(matches), matches=matches)
        return data

    def get_matches(self) -> list[list[FootballMatch]]:
        data = self._get_data()
        # TODO data validation (scrape timestamps deltas)
        return self._batch_matching_strategy.match_events(data)
