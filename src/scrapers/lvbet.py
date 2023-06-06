from collections import defaultdict
from datetime import datetime, timedelta
from functools import partial
from typing import Any

import requests

from src.constants import LV_BET_DAYS_TO_SCRAPE
from src.engine.models import Odds
from src.enums import Bookmaker, FootballOutcome
from src.scrapers.base import BaseScrapper, T
from src.scrapers.schemas.base import ParsedDatasetModel, ScrapeResultModel


class LvBetScrapper(BaseScrapper):
    BASE_API_URL = "https://offer.lvbet.pl/client-api/v3/matches/competition-view/?lang=en&sports_groups_ids=1&sports_groups_ids=36530&sports_groups_ids=37609"
    BOOKMAKER_NAME = Bookmaker.LVBET

    @staticmethod
    def _get_request_timeframe(days_to_scrape: int = LV_BET_DAYS_TO_SCRAPE) -> str:
        now = datetime.utcnow()
        date_from = now - timedelta(hours=12)
        date_to = now + timedelta(days=days_to_scrape)

        s_date_from = date_from.strftime("%Y-%m-%d% 00:00")
        s_date_to = date_to.strftime("%Y-%m-%d 00:00")
        parameters = f"&date_from={s_date_from}&date_to={s_date_to}"
        return parameters

    async def acquire_data(self) -> T:
        date_parameters = self._get_request_timeframe()
        response = requests.get(
            self.BASE_API_URL + date_parameters
        )  # TODO use async client for consistency
        data = response.json()
        return data

    def transform_data(self, raw_data: T) -> ParsedDatasetModel:
        data_points = [
            entry
            for entry in raw_data["primary_column_markets"]
            if entry["name"] == "Match Result"
        ]

        matches_event_datetimes = [
            {"match_id": match["match_id"], "event_time": match["date"]}
            for match in raw_data["matches"]
        ]

        bet_info_with_event_time = defaultdict(dict)
        for match in data_points + matches_event_datetimes:
            bet_info_with_event_time[match["match_id"]].update(match)

        complete_data = list(bet_info_with_event_time.values())

        return super().transform_data(complete_data)

    def _parse_raw_datapoint(
        self, raw_match: dict[Any, Any]
    ) -> ScrapeResultModel:

        odds_with_last_update = partial(Odds, last_update=self.scrapping_start_timestamp)

        return ScrapeResultModel(
            event_time=raw_match["event_time"],
            team_a=raw_match["selections"][0]["label"],
            team_b=raw_match["selections"][2]["label"],
            bet_options={
                FootballOutcome.TEAM_A_WINS: odds_with_last_update(
                    odds=raw_match["selections"][0]["rate"]["decimal"],
                ),
                FootballOutcome.DRAW: odds_with_last_update(
                    odds=raw_match["selections"][1]["rate"]["decimal"],
                ),
                FootballOutcome.TEAM_B_WINS: odds_with_last_update(
                    odds=raw_match["selections"][2]["rate"]["decimal"],

                ),
            },
        )


async def main() -> None:
    lvbet = LvBetScrapper()
    await lvbet.scrape()


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
