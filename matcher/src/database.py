from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "sqlite.db"
REBUILD_TABLES = False


engine = create_engine(f"sqlite:///{DB_PATH}")

SessionFactory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_database():
    with SessionFactory() as session:
        return session
