import asyncio

import uvicorn
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from database import init_db
from matcher.src.services.matching.strategy.entity.levenshtein import \
    LevenshteinDistanceEntityComparisonStrategy
from src.data_access.base import SyncSQLAlchemyDataAccess
from src.deps import get_database
from src.models.football_match import FootballMatchModel
from src.rabbit import RabbitMQClient
from src.schemas.consumer_match import FootballMatch
from src.services.matching.matching import FootballEventMatchingService
from src.settings.settings import settings

EXCHANGE_NAME = settings.RABBIT_PUBLISHING_EXCHANGE_NAME
QUEUE_NAME = settings.RABBIT_PUBLISHING_QUEUE_NAME

init_db()
app = FastAPI()


# @app.on_event("startup")
# async def startup_event() -> None:
#     app.state.mq = await RabbitMQClient.connect(
#         settings.RABBIT_HOST,
#         settings.RABBIT_PORT,
#         settings.RABBIT_LOGIN,
#         settings.RABBIT_PASSWORD,
#     )
#
#     queue = await app.state.mq.channel.declare_queue(QUEUE_NAME)
#     loop = asyncio.get_running_loop()
#     app.state.queue = queue
#     task = loop.create_task(app.state.mq.consume(queue))
#     await task
#
#
# @app.on_event("shutdown")
# async def shutdown_event() -> None:
#     await app.state.mq.disconnect()


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
