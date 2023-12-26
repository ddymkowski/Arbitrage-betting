from __future__ import annotations

import json
import logging
from typing import Any

from aio_pika import Message, RobustExchange, connect_robust
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from src.enums import Bookmaker
from src.utils.utils import FootballMatchDTOJSONEncoder

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)


class RabbitMQClient:
    @classmethod
    async def connect(
        cls,
        host: str,
        port: int,
        login: str,
        password: str,
    ) -> RabbitMQClient:
        connection = await connect_robust(
            host=host, port=port, login=login, password=password
        )

        channel = await connection.channel(publisher_confirms=False)
        return cls(connection, channel)

    def __init__(
        self,
        connection: AbstractRobustConnection,
        channel: AbstractChannel,
    ) -> None:
        self.connection: AbstractRobustConnection = connection
        self.channel: AbstractChannel = channel
        self._logger = logging.getLogger(self.__class__.__qualname__)

    async def disconnect(self) -> None:
        if not self.channel.is_closed:
            await self.channel.close()
        if not self.connection.is_closed:
            await self.connection.close()

    async def send_messages(
        self,
        messages: list[dict[str, Any]] | dict[str, Any],
        exchange: RobustExchange,
        routing_key: str,
        scrape_id: str,
        bookmaker: Bookmaker,
    ) -> None:
        messages_count = len(messages)

        if isinstance(messages, dict):
            messages = [messages]

        async with self.channel.transaction():
            self._logger.info(
                f"Starting publishing {messages_count} messages [scrape_id: {scrape_id}, bookmaker: {bookmaker.value}]"
            )
            for raw_message in messages:
                message = Message(
                    body=json.dumps(
                        raw_message, cls=FootballMatchDTOJSONEncoder
                    ).encode()
                )

                await exchange.publish(
                    message,
                    routing_key=routing_key,
                )
            self._logger.info(
                f"Finished publishing {messages_count} messages [scrape_id: {scrape_id}, bookmaker: {bookmaker.value}]"
            )
