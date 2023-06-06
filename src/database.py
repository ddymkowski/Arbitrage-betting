import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.orm import as_declarative, declared_attr, sessionmaker

from src.scrapers.utils import custom_json_serializer
from src.scrapers.utils import generate_uuid



@as_declarative()
class Base:
    id = Column(String, default=generate_uuid, primary_key=True, index=True)
    insertion_timestamp = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @declared_attr
    def __tablename__(cls):
        return f"{cls.__name__.lower()}s"


db_path = "../data.db"
engine = create_engine(
    f"sqlite:///{db_path}", json_serializer=custom_json_serializer
)

SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_database():
    with SessionFactory() as session:
        return session
