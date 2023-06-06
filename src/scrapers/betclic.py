import asyncio
import traceback
from datetime import datetime
from pprint import pformat
from typing import Any
from uuid import UUID

from aiohttp import ClientSession
from pydantic import ValidationError

from src.constants import BETCLIC_API_LIMIT, BETCLIC_PAGES
from src.enums import Bookmaker, FootballOutcome
from src.engine.models import Odds
from src.scrapers.base import BaseScrapper
from src.scrapers.schemas.base import MatchModel, ParsedDatasetModel
from src.storage.data_access import SqliteRepository


class BetClicScrapper(BaseScrapper):
    # language pl = pa
    BASE_API_URL = f"https://offer.cdn.begmedia.com/api/pub/v4/sports/1?application=2048&countrycode=pl\
    &hasSwitchMtc=true&language=en&markettypeId=1365&sitecode=plpa&sortBy=ByLiveRankingPreliveDate"
    BOOKMAKER_NAME = Bookmaker.BETCLIC

    async def fetch_page(
        self,
        matches: list[dict[str, Any]],
        session: ClientSession,
        url: str,
        scrape_id: UUID,
    ) -> None:
        async with session.get(url) as response:
            json_response = await response.json()

            if response.status == 200:
                matches.extend(json_response["matches"])
                return

            self._logger.warning(
                f"ID: {scrape_id} - {url}:{response.status} - {json_response}\n"
            )

    async def get_raw_api_data(
        self, pages: int, scrape_id: UUID, limit: int = BETCLIC_API_LIMIT
    ):
        tasks = []
        offsets = [page * limit for page in range(pages)]

        matches = []

        async with ClientSession() as session:
            for offset in offsets:
                request_url = self.BASE_API_URL + f"&offset={offset}&limit={limit}"
                task = asyncio.create_task(
                    self.fetch_page(matches, session, request_url, scrape_id)
                )
                tasks.append(task)

            await asyncio.gather(*tasks)
        return matches

    @staticmethod
    def parse_raw_datapoint(
        raw_match: dict[Any, Any],
        scrape_timestamp: datetime,
    ) -> MatchModel:
        odds_section = raw_match["grouped_markets"][0]["markets"][0]["selections"]
        return MatchModel(
            event_time=raw_match["date"],
            team_a=raw_match["contestants"][0]["name"],
            team_b=raw_match["contestants"][1]["name"],
            bet_options={
                FootballOutcome.TEAM_A_WINS: Odds(
                    odds=odds_section[0][0]["odds"], last_update=scrape_timestamp
                ),
                FootballOutcome.DRAW: Odds(
                    odds=odds_section[1][0]["odds"], last_update=scrape_timestamp
                ),
                FootballOutcome.TEAM_B_WINS: Odds(
                    odds=odds_section[2][0]["odds"], last_update=scrape_timestamp
                ),
            },
        )

    def normalize_api_data(
        self, raw_data: list[dict[Any, Any]], scrapping_start_timestamp: datetime
    ) -> list[MatchModel]:
        normalized_data = []
        validation_errors = 0
        exceptions = []

        for raw_match_data in raw_data:
            try:
                normalized_data.append(
                    self.parse_raw_datapoint(
                        raw_match=raw_match_data,
                        scrape_timestamp=scrapping_start_timestamp,
                    )
                )
            except (ValidationError, IndexError, KeyError):
                validation_errors += 1
                exceptions.append(traceback.format_exc())

        self._logger.warning(f"Validation errors count: {validation_errors}.\n")
        self._logger.info(f"Successfully parsed: {len(normalized_data)} matches.\n")

        if validation_errors > 0.5 * len(raw_data):
            self._logger.error(
                f"More than 50% of raw data could not be parsed properly check logs."
            )
            self._logger.error(f"{'---' * 20} \n {pformat(exceptions)} {'---' * 20} \n")

        return normalized_data

    def save_data_to_database(self, data: ParsedDatasetModel) -> None:
        self._logger.info(f"ID: {data.scrape_id} Saving: {len(data.data)} data points.")
        db = SqliteRepository()
        db.add(data)

    async def scrape(self, pages: int = BETCLIC_PAGES):
        raw_data = await self.get_raw_api_data(pages=pages, scrape_id=self.scrape_id)

        normalized_data = self.normalize_api_data(raw_data, self.scrapping_start_timestamp)
        if not normalized_data:
            self._logger.error(f"ID: {self.scrape_id}: No data was saved - check logs.\n")

        data_dump = ParsedDatasetModel(
            data=normalized_data,
            scrape_id=self.scrape_id,
            source=self.BOOKMAKER_NAME,
            scrape_start_timestamp=self.scrapping_start_timestamp,
            scrape_end_timestamp=datetime.utcnow(),
        )
        self.save_data_to_database(data=data_dump)


async def main() -> None:
    betclic = BetClicScrapper()
    await betclic.scrape()
