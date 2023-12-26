from database import Base
from sqlalchemy import JSON, Column, DateTime, String


class FootballMatchModel(Base):
    __tablename__ = "football_matches"

    event_time = Column(DateTime())
    team_a = Column(String())
    team_b = Column(String())
    team_a_standardized = Column(String(), default="")
    team_b_standardized = Column(String(), default="")
    bet_options = Column(JSON())
    scrape_id = Column(String())
    source = Column(String())
    scrape_start_timestamp = Column(DateTime())
    scrape_end_timestamp = Column(DateTime())
