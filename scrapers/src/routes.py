from fastapi import APIRouter
from src.services.betclic import BetClicScrapper
from src.services.lvbet import LvBetScrapper

router = APIRouter()


@router.post("/betlic", tags=["Jobs"])
async def scrape_and_publish_betclic() -> dict[str, str]:
    service = BetClicScrapper()
    scraped_data = await service.scrape()
    print(f"Publishing {scraped_data}")
    return {"detail": "OK"}


@router.post("/lvbet", tags=['Jobs'])
async def scrape_and_publish_lvbet() -> dict[str, str]:
    service = LvBetScrapper()
    scraped_data = await service.scrape()
    print(f"Publishing {scraped_data}")
    return {"detail": "OK"}
