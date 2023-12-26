from __future__ import annotations

import logging
from functools import partial

from aio_pika import Message, RobustQueue, connect_robust
from aio_pika.abc import AbstractChannel, AbstractRobustConnection
from sqlalchemy.orm import Session
from src.deps import get_database
from src.schemas.consumer_match import FootballMatch
from src.services.name_standardization import \
    FootballClubNameStandardizationService

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

    async def _process_rabbitmq_message(
        self,
        message: Message,
        standardization_service: FootballClubNameStandardizationService,
        db_session: Session,
    ) -> None:
        async with message.process():
            self._logger.info(f"Processing: {message.body}")

            queue_match = FootballMatch.from_bytes(message.body)

            standardized_match = standardization_service.standardize_club_names(
                queue_match
            )

            db_model = standardized_match.to_sqlalchemy_model()
            db_session.add(db_model)
            db_session.commit()

    async def consume(self, queue: RobustQueue):
        db_session = get_database()
        service = FootballClubNameStandardizationService()
        callback = partial(
            self._process_rabbitmq_message,
            standardization_service=service,
            db_session=db_session,
        )

        await queue.consume(callback, no_ack=False)
