from datetime import datetime

from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.orm import as_declarative, declared_attr, sessionmaker

from src.constants import DB_PATH
from scrapers.src.utils.utils import custom_json_serializer, generate_uuid


@as_declarative()
class Base:
    id = Column(String, default=generate_uuid, primary_key=True, index=True)
    insertion_timestamp = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"


engine = create_engine(f"sqlite:///{DB_PATH}", json_serializer=custom_json_serializer)

SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_database():
    with SessionFactory() as session:
        return session
