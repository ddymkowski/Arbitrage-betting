import asyncio

import uvicorn
from aio_pika import ExchangeType
from database import init_db
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from src.data_access.base import SyncSQLAlchemyDataAccess
from src.deps import get_database
from src.models.football_match import FootballMatchModel
from src.rabbit import RabbitMQClient
from src.schemas.consumer_match import FootballMatch
from src.services.matching.matching import FootballEventMatchingService
from src.services.matching.strategy.entity.levenshtein import \
    LevenshteinDistanceEntityComparisonStrategy
from src.settings.settings import settings

EXCHANGE_NAME = settings.RABBIT_PUBLISHING_EXCHANGE_NAME
QUEUE_NAME = settings.RABBIT_PUBLISHING_QUEUE_NAME

init_db()
app = FastAPI()


@app.on_event("startup")
async def startup_event() -> None:
    pass
    app.state.mq = await RabbitMQClient.connect(
        settings.RABBIT_HOST,
        settings.RABBIT_PORT,
        settings.RABBIT_LOGIN,
        settings.RABBIT_PASSWORD,
    )

    # Sub
    sub_queue = await app.state.mq.channel.declare_queue(QUEUE_NAME)
    loop = asyncio.get_running_loop()
    app.state.sub_queue = sub_queue
    task = loop.create_task(app.state.mq.consume(sub_queue))
    await task

    # Pub
    exchange = await app.state.mq.channel.declare_exchange(
        EXCHANGE_NAME, ExchangeType.FANOUT
    )
    pub_que = await app.state.mq.channel.declare_queue(QUEUE_NAME)
    await pub_que.bind(exchange=exchange)

    app.state.exchange = exchange
    app.state.pub_queue = pub_que


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await app.state.mq.disconnect()


@app.get("/")
async def create_matches_groups(
    session: Session = Depends(get_database),
) -> dict[str, str]:
    # service = FootballEventMatchingService.from_session(session)
    service = FootballEventMatchingService.from_session(
        session, entity_matching_strategy=LevenshteinDistanceEntityComparisonStrategy()
    )
    matches_groups = service.get_matches()
    print("________")
    print(len(matches_groups))

    for matches_cluster in matches_groups:
        print("******")
        for bookmaker_data in matches_cluster:
            print(bookmaker_data)
            print()

    # send data to queue
    return {"detail": "OK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6969, log_level="info")
