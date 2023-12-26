import asyncio

from database import init_db
from fastapi import FastAPI
from src.rabbit import RabbitMQClient
from src.settings.settings import settings

EXCHANGE_NAME = settings.RABBIT_PUBLISHING_EXCHANGE_NAME
QUEUE_NAME = settings.RABBIT_PUBLISHING_QUEUE_NAME

init_db()
app = FastAPI()


@app.on_event("startup")
async def startup_event() -> None:
    app.state.mq = await RabbitMQClient.connect(
        settings.RABBIT_HOST,
        settings.RABBIT_PORT,
        settings.RABBIT_LOGIN,
        settings.RABBIT_PASSWORD,
    )

    queue = await app.state.mq.channel.declare_queue(QUEUE_NAME)
    loop = asyncio.get_running_loop()
    app.state.queue = queue
    task = loop.create_task(app.state.mq.consume(queue))
    await task


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await app.state.mq.disconnect()
