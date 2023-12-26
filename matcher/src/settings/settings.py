from src.settings.rabbit import RabbitMQSettings
from src.settings.scrapers import ScrapersSettings


class Settings(RabbitMQSettings, ScrapersSettings):
    pass


settings = Settings()
