from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, DefaultDict, Final

import aiohttp
from src.enums import Bookmaker, FootballOutcome
from src.schemas.base import FootballMatchData
from src.services.base import RD, BaseScrapingService, Serializable
from src.settings.settings import settings

LV_BET_DAYS_TO_SCRAPE: Final[int] = settings.LV_BET_DAYS_TO_SCRAPE


class LvBetScrapingService(BaseScrapingService[dict[Any, Any]]):
    BASE_API_URL = "https://offer.lvbet.pl/client-api/v4/matches/competition-view/?lang=en&sports_groups_ids=1&sports_groups_ids=36530&sports_groups_ids=37609"  # noqa #pylint: disable=line-too-long

    @property
    def bookmaker(self) -> Bookmaker:
        return Bookmaker.LVBET

    @staticmethod
    def _get_request_timeframe(
        days_to_scrape: int = LV_BET_DAYS_TO_SCRAPE,
    ) -> dict[str, str]:
        now = datetime.utcnow()
        date_from = now - timedelta(hours=12)
        date_to = now + timedelta(days=days_to_scrape)

        s_date_from = date_from.strftime(
            "%Y-%m-%d 00:00"
        )  # TODO move to params & partition into smaller chunks
        s_date_to = date_to.strftime("%Y-%m-%d 00:00")
        parameters = {"date_from": s_date_from, "date_to": s_date_to}
        return parameters

    async def acquire_raw_data(self) -> dict[Any, Any]:
        date_parameters = self._get_request_timeframe()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.BASE_API_URL, params=date_parameters
            ) as response:
                data: dict[Any, Any] = await response.json()
                return data

    def preprocess_raw_data(self, raw_data: RD) -> list[Serializable]:
        data_points: list[dict[str, Any]] = [
            entry
            for entry in raw_data["primary_column_markets"]
            if entry["name"] == "Match Result"
        ]

        matches_event_datetimes: list[dict[str, str]] = [
            {"match_id": match["match_id"], "event_time": match["date"]}
            for match in raw_data["matches"]
        ]

        bet_info_with_event_time: DefaultDict[str, Serializable] = defaultdict(dict)
        for match in data_points + matches_event_datetimes:
            bet_info_with_event_time[match["match_id"]].update(match)

        return list(bet_info_with_event_time.values())

    def serialize_datapoint(self, raw_datapoint: dict[Any, Any]) -> FootballMatchData:
        return FootballMatchData(
            event_time=raw_datapoint["event_time"],
            team_a=raw_datapoint["selections"][0]["label"],
            team_b=raw_datapoint["selections"][2]["label"],
            bet_options={
                FootballOutcome.TEAM_A_WINS: raw_datapoint["selections"][0]["rate"][
                    "decimal"
                ],
                FootballOutcome.DRAW: raw_datapoint["selections"][1]["rate"]["decimal"],
                FootballOutcome.TEAM_B_WINS: raw_datapoint["selections"][2]["rate"][
                    "decimal"
                ],
            },
        )


async def main() -> None:
    lvbet = LvBetScrapingService()
    await lvbet.scrape()


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
