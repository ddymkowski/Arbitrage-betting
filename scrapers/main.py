from aio_pika import ExchangeType
from fastapi import FastAPI
from src.routes import router
from src.settings.settings import settings
from src.utils.rabbit import RabbitMQClient

EXCHANGE_NAME = settings.RABBIT_PUBLISHING_EXCHANGE_NAME
QUEUE_NAME = settings.RABBIT_PUBLISHING_QUEUE_NAME

app = FastAPI()
app.include_router(router=router)


@app.on_event("startup")
async def startup_event() -> None:
    app.state.mq = await RabbitMQClient.connect(
        settings.RABBIT_HOST,
        settings.RABBIT_PORT,
        settings.RABBIT_LOGIN,
        settings.RABBIT_PASSWORD,
    )

    exchange = await app.state.mq.channel.declare_exchange(
        EXCHANGE_NAME, ExchangeType.FANOUT
    )
    queue = await app.state.mq.channel.declare_queue(QUEUE_NAME)
    await queue.bind(exchange=exchange)

    app.state.exchange = exchange
    app.state.queue = queue


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await app.state.mq.disconnect()
