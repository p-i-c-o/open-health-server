from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.app.settings import get_settings


class Base(DeclarativeBase):
    pass


def make_engine(database_url: str | None = None) -> Engine:
    settings = get_settings()
    return create_engine(database_url or settings.database_url, pool_pre_ping=True)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db_session() -> Generator[Session]:
    with SessionLocal() as session:
        yield session


def check_database_connection(db_engine: Engine | None = None) -> bool:
    active_engine = db_engine or engine
    with active_engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True
