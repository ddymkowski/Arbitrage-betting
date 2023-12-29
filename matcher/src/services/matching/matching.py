from sqlalchemy.orm import Session
from src.data_access.base import SyncSQLAlchemyDataAccess
from src.schemas.consumer_match import FootballMatch
from src.services.matching.data import Batch
from src.services.matching.strategy.batch.base import BaseEventMatchingStrategy
from src.services.matching.strategy.batch.bruteforce import \
    BruteForceMatchingStrategy


class FootballEventMatchingService:
    def __init__(
        self,
        data_access: SyncSQLAlchemyDataAccess,
        batch_matching_strategy: BaseEventMatchingStrategy = None,
    ):
        self._data_access = data_access
        self._batch_matching_strategy = (
            batch_matching_strategy
            if batch_matching_strategy
            else BruteForceMatchingStrategy()
        )

    @classmethod
    def from_session(cls, session: Session) -> "FootballEventMatchingService":
        return cls(data_access=SyncSQLAlchemyDataAccess(session))

    def _get_data(self) -> dict[str, dict[str, list[FootballMatch] | int]]:
        all_bookmakers: list[str] = self._data_access.get_distinct_bookmakers()

        data = {}
        for bookmaker in all_bookmakers:
            matches = self._data_access.get_bookmaker_newest_batch(bookmaker)
            data[bookmaker] = Batch(count=len(matches), matches=matches)

        return data

    def run(self):
        data = self._get_data()

        for event_a, event_b in self._batch_matching_strategy.match_events(data):
            print(event_a, event_b)
