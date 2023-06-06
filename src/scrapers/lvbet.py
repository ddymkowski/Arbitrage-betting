import requests

from src.scrapers.base import BaseScrapper
from src.enums import Bookmaker
from datetime import datetime, timedelta
from src.constants import LV_BET_DAYS_TO_SCRAPE
from src.scrapers.schemas.base import ParsedDatasetModel
from typing import Any


class LvBetScrapper(BaseScrapper):
    BASE_API_URL = f"https://offer.lvbet.pl/client-api/v3/matches/competition-view/?lang=en&sports_groups_ids=1&sports_groups_ids=36530&sports_groups_ids=37609"
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

    @staticmethod
    def fetch_relevant_data(response: requests.models.Response):
        data_points = []
        data = response.json()
        print(data['primary_column_markets'][0])
        return [entry for entry in data['primary_column_markets'] if 'Match Result' in entry]

    def scrape(self):
        date_parameters = self._get_request_timeframe()
        url = self.BASE_API_URL + date_parameters

        response = requests.get(url)

        if response.status_code == 200:
            data = self.fetch_relevant_data(response)
            print(data)



        # for i in data['primary_column_markets']:
        #     if i['match_id'] == 'bc:22384587' and i['name'] == 'Match Result':
        #         print(i)
        #         print('~~~~~~~~~~~~~~~~~~~~')


    def save_data_to_database(self, data: ParsedDatasetModel, database: Any) -> None:
        pass



z = LvBetScrapper()

z.scrape()