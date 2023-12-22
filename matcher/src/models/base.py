from uuid import uuid4
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    id = Column(String, default=lambda x: str(uuid4()), primary_key=True, index=True)
    insertion_timestamp = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"