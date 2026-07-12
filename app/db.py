import os
import time

from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL
from app.models.user import User  # noqa: F401
from app.models.character import Character  # noqa: F401
from app.models.chat import Chat  # noqa: F401
from app.models.message import Message  # noqa: F401
from app.models.summary import Summary  # noqa: F401

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "").lower() in {"1", "true", "yes"},
)


def get_session():
    with Session(engine) as session:
        yield session


def init_db(max_retries: int = 5, retry_delay_seconds: float = 1.0) -> None:
    """Create tables, retrying while Postgres (e.g. Neon) wakes from sleep."""
    for attempt in range(max_retries):
        try:
            SQLModel.metadata.create_all(engine)
            return
        except OperationalError:
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay_seconds)
