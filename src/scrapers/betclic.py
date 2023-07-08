import asyncio
from functools import partial
from typing import Any
from uuid import UUID

from aiohttp import ClientSession

from src.constants import BETCLIC_API_LIMIT, BETCLIC_PAGES
from src.engine.models import Odds
from src.enums import Bookmaker, FootballOutcome
from src.scrapers.base import RD, BaseScrapper
from src.scrapers.schemas.base import ScrapeResultModel

Serializable = dict[str, Any]


class BetClicScrapper(BaseScrapper[list[Serializable]]):
    # language pl = pa
    BASE_API_URL = (
        "https://offer.cdn.begmedia.com/api/pub/v4/sports/1?application=2048&countrycode=pl"
        "&hasSwitchMtc=true&language=en&markettypeId=1365&sitecode=plpa&sortBy=ByLiveRankingPreliveDate"
    )
    BOOKMAKER_NAME = Bookmaker.BETCLIC

    async def acquire_raw_data(self, limit: int = BETCLIC_API_LIMIT, pages: int = BETCLIC_PAGES) -> list[Serializable]:
        tasks = []
        offsets = [page * limit for page in range(pages)]

        matches: list[Any] = []

        async with ClientSession() as session:
            for offset in offsets:
                request_url = self.BASE_API_URL + f"&offset={offset}&limit={limit}"
                task = asyncio.create_task(self._fetch_page(matches, session, request_url, self.scrape_id))
                tasks.append(task)

            await asyncio.gather(*tasks)
        return matches

    def preprocess_raw_data(self, raw_data: list[Serializable]) -> list[Serializable]:
        return raw_data

    def serialize_datapoint(self, raw_datapoint: Serializable) -> ScrapeResultModel:
        odds_section = raw_datapoint["grouped_markets"][0]["markets"][0]["selections"]

        odds_with_last_update = partial(Odds, last_update=self.scrapping_start_timestamp)

        return ScrapeResultModel(
            event_time=raw_datapoint["date"],
            team_a=raw_datapoint["contestants"][0]["name"],
            team_b=raw_datapoint["contestants"][1]["name"],
            bet_options={
                FootballOutcome.TEAM_A_WINS: odds_with_last_update(odds=odds_section[0][0]["odds"]),
                FootballOutcome.DRAW: odds_with_last_update(odds=odds_section[1][0]["odds"]),
                FootballOutcome.TEAM_B_WINS: odds_with_last_update(odds=odds_section[2][0]["odds"]),
            },
        )

    async def _fetch_page(
        self,
        matches: RD,
        session: ClientSession,
        url: str,
        scrape_id: UUID,
    ) -> None:
        async with session.get(url) as response:
            json_response = await response.json()

            if response.status == 200:
                matches.extend(json_response["matches"])
                return

            self._logger.warning(f"ID: {scrape_id} - {url}:{response.status} - {json_response}\n")


async def main() -> None:
    betclic = BetClicScrapper()
    await betclic.scrape()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
