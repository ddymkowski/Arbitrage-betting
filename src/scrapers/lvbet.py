from datetime import datetime, timedelta
from typing import Any

import requests

from src.constants import LV_BET_DAYS_TO_SCRAPE
from src.engine.models import Odds
from src.enums import Bookmaker, FootballOutcome
from src.scrapers.base import BaseScrapper
from src.scrapers.schemas.base import ScrapeResultModel


class LvBetScrapper(BaseScrapper):
    BASE_API_URL = "https://offer.lvbet.pl/client-api/v3/matches/competition-view/?lang=en&sports_groups_ids=1&sports_groups_ids=36530&sports_groups_ids=37609"
    BOOKMAKER_NAME = Bookmaker.LVBET

    @staticmethod
    def _get_request_timeframe(days_to_scrape: int = LV_BET_DAYS_TO_SCRAPE):
        now = datetime.utcnow()
        date_from = now - timedelta(hours=12)
        date_to = now + timedelta(days=days_to_scrape)

        s_date_from = date_from.strftime("%Y-%m-%d% 00:00")
        s_date_to = date_to.strftime("%Y-%m-%d 00:00")
        parameters = f"&date_from={s_date_from}&date_to={s_date_to}"
        return parameters

    async def get_raw_api_data(self):
        date_parameters = self._get_request_timeframe()
        response = requests.get(
            self.BASE_API_URL + date_parameters
        )  # TODO use async client for consistency
        data = response.json()
        data_points = [
            entry
            for entry in data["primary_column_markets"]
            if entry["name"] == "Match Result"
        ]
        return data_points

    @staticmethod
    def parse_raw_datapoint(
        raw_match: dict[Any, Any],
        scrape_timestamp: datetime,
    ) -> ScrapeResultModel:
        # TODO find endpoint with match event time
        PLACEHOLDER = datetime.utcnow()
        return ScrapeResultModel(
            event_time=PLACEHOLDER,
            team_a=raw_match["selections"][0]["label"],
            team_b=raw_match["selections"][2]["label"],
            bet_options={
                FootballOutcome.TEAM_A_WINS: Odds(
                    odds=raw_match["selections"][0]["rate"]["decimal"],
                    last_update=scrape_timestamp,
                ),
                FootballOutcome.DRAW: Odds(
                    odds=raw_match["selections"][1]["rate"]["decimal"],
                    last_update=scrape_timestamp,
                ),
                FootballOutcome.TEAM_B_WINS: Odds(
                    odds=raw_match["selections"][2]["rate"]["decimal"],
                    last_update=scrape_timestamp,
                ),
            },
        )


async def main() -> None:
    lvbet = LvBetScrapper()
    await lvbet.scrape()
