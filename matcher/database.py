from datetime import datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, create_engine
from sqlalchemy.orm import as_declarative, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sqlite.db"


engine = create_engine(f"sqlite:///{DB_PATH}")
SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@as_declarative()
class Base:
    id = Column(String, default=lambda x: str(uuid4()), primary_key=True, index=True)
    insertion_timestamp = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db(rebuild=False) -> None:
    if rebuild:
        Base.metadata.drop_all(engine)

    Base.metadata.create_all(engine)
