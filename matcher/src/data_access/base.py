from sqlalchemy.orm import Session
from src.models.football_match import FootballMatchModel
from src.schemas.consumer_match import FootballMatch


class SyncSQLAlchemyDataAccess:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_distinct_bookmakers(self) -> list[str]:
        query = self._session.query(FootballMatchModel.source).distinct().all()
        return [bookmaker[0] for bookmaker in query]  # todo add enum from literal

    def get_bookmaker_newest_batch(self, bookmaker: str) -> list[FootballMatch]:
        latest_scrape = (
            self._session.query(FootballMatchModel)
            .filter(FootballMatchModel.source == bookmaker)
            .order_by(FootballMatchModel.insertion_timestamp.desc())
            .first()
        )

        if latest_scrape:
            latest_matches = (
                self._session.query(FootballMatchModel)
                .filter(FootballMatchModel.scrape_id == latest_scrape.scrape_id)
                .all()
            )
            return [
                FootballMatch.from_sqlalchemy_model(model) for model in latest_matches
            ]
        return []
