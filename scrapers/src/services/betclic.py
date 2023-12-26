import asyncio
from typing import Any, Final
from uuid import UUID

from aiohttp import ClientSession
from src.enums import Bookmaker, FootballOutcome
from src.schemas.base import FootballMatchData
from src.services.base import RD, BaseScrapingService
from src.settings.settings import settings

BETCLIC_API_LIMIT: Final[int] = settings.BETCLIC_API_LIMIT
BETCLIC_PAGES: Final[int] = settings.BETCLIC_PAGES

Serializable = dict[str, Any]


class BetClicScrapingService(BaseScrapingService[list[Serializable]]):
    # language pl = pa
    BASE_API_URL = (
        "https://offer.cdn.begmedia.com/api/pub/v4/sports/1?application=2048&countrycode=pl"
        "&hasSwitchMtc=true&language=en&markettypeId=1365&sitecode=plpa&sortBy=ByLiveRankingPreliveDate"
    )

    @property
    def bookmaker(self):
        return Bookmaker.BETCLIC

    async def acquire_raw_data(
        self, limit: int = BETCLIC_API_LIMIT, pages: int = BETCLIC_PAGES
    ) -> list[Serializable]:
        tasks = []
        offsets = [page * limit for page in range(pages)]

        matches: list[Any] = []

        async with ClientSession() as session:
            for offset in offsets:
                params = {"offset": offset, "limit": limit}
                task = asyncio.create_task(
                    self._fetch_page(
                        matches, params, session, self.BASE_API_URL, self._scrape_id
                    )
                )
                tasks.append(task)

            await asyncio.gather(*tasks)
        return matches

    def preprocess_raw_data(self, raw_data: list[Serializable]) -> list[Serializable]:
        return raw_data

    def serialize_datapoint(self, raw_datapoint: Serializable) -> FootballMatchData:
        odds_section = raw_datapoint["grouped_markets"][0]["markets"][0]["selections"]

        return FootballMatchData(
            event_time=raw_datapoint["date"],
            team_a=raw_datapoint["contestants"][0]["name"],
            team_b=raw_datapoint["contestants"][1]["name"],
            bet_options={
                FootballOutcome.TEAM_A_WINS: odds_section[0][0]["odds"],
                FootballOutcome.DRAW: odds_section[1][0]["odds"],
                FootballOutcome.TEAM_B_WINS: odds_section[2][0]["odds"],
            },
        )

    async def _fetch_page(
        self,
        matches: RD,
        params: dict[str, Any],
        session: ClientSession,
        url: str,
        scrape_id: UUID,
    ) -> None:
        async with session.get(url, params=params) as response:
            json_response = await response.json()

            if response.status == 200:
                matches.extend(json_response["matches"])
                return

            self._logger.warning(
                f"ID: {scrape_id} - {url}:{response.status} - {json_response}\n"
            )
