from pydantic import BaseSettings


class ScrapersSettings(BaseSettings):
    BETCLIC_API_LIMIT: int = 250
    BETCLIC_PAGES: int = 5
    LV_BET_DAYS_TO_SCRAPE: int = 10
