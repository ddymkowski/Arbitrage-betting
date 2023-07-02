from sqlalchemy import JSON, Column, DateTime, String

from src.constants import REBUILD_TABLES
from src.database import Base, engine


class Scrape(Base):
    scrape_id = Column(String)
    source = Column(String)
    scrape_start_timestamp = Column(DateTime)
    scrape_end_timestamp = Column(DateTime)
    team_a = Column(String)
    team_b = Column(String)
    event_time = Column(DateTime)
    bet_options = Column(JSON)


if REBUILD_TABLES:
    Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)
