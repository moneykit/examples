import contextlib
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from budgeting_app.settings import get_settings

settings = get_settings()


sync_engine = create_engine(
    settings.database_url.get_secret_value(),
    connect_args={"connect_timeout": 15},
    pool_pre_ping=True,
    pool_timeout=10,
    echo=settings.database_echo_sql,
)

SessionLocal = sessionmaker(sync_engine, autocommit=False, expire_on_commit=False)


@contextlib.contextmanager
def sync_db_session() -> Generator[Session, None, None]:
    sync_session = SessionLocal()
    try:
        yield sync_session
    finally:
        sync_session.close()


def get_db_session() -> Generator[Session, None, None]:
    with sync_db_session() as sync_session:
        yield sync_session
