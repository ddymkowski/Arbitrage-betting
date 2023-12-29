import random

from fastapi import APIRouter, Request
from src.enums import Bookmaker
from src.services.betclic import BetClicScrapingService
from src.services.lvbet import LvBetScrapingService

router = APIRouter()


@router.post("/betlic", tags=["Jobs"])
async def scrape_and_publish_betclic(request: Request) -> dict[str, str]:
    service = BetClicScrapingService()
    scraped_data = await service.scrape()

    queue = request.app.state.mq
    await queue.send_messages(
        messages=scraped_data,
        exchange=request.app.state.exchange,
        routing_key=service.bookmaker.value,
        scrape_id=service.scrape_id,
        bookmaker=service.bookmaker,
    )
    return {"detail": "Published Betclic data to rabbitmq."}


@router.post("/lvbet", tags=["Jobs"])
async def scrape_and_publish_lvbet(request: Request) -> dict[str, str]:
    service = LvBetScrapingService()
    scraped_data = await service.scrape()

    queue = request.app.state.mq
    await queue.send_messages(
        messages=scraped_data,
        exchange=request.app.state.exchange,
        routing_key=service.bookmaker.value,
        scrape_id=service.scrape_id,
        bookmaker=service.bookmaker,
    )
    return {"detail": "Published LVBet data to rabbitmq."}


@router.post("/fortuna", tags=["Jobs"])
async def scrape_and_publish_dummy_fortuna(request: Request) -> dict[str, str]:
    service = LvBetScrapingService()
    scraped_data = await service.scrape()

    sample_size = int(len(scraped_data) * 0.7)
    scraped_data = random.sample(scraped_data, sample_size)

    for data in scraped_data:
        data.source = Bookmaker.FORTUNA

    queue = request.app.state.mq
    await queue.send_messages(
        messages=scraped_data,
        exchange=request.app.state.exchange,
        routing_key=service.bookmaker.value,
        scrape_id=service.scrape_id,
        bookmaker=Bookmaker.FORTUNA,
    )
    return {"detail": "Published Fortuna data to rabbitmq."}
