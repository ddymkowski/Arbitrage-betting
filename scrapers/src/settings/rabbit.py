from pydantic import BaseSettings


class RabbitMQSettings(BaseSettings):
    RABBIT_HOST: str = "localhost"
    RABBIT_PORT: int = 5672
    RABBIT_LOGIN: str = "user"
    RABBIT_PASSWORD: str = "pass"

    RABBIT_PUBLISHING_EXCHANGE_NAME: str = "scraper-pub"
    RABBIT_PUBLISHING_QUEUE_NAME: str = "scraper_queue"
