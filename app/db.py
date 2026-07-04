from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL
from app.models.user import User  # noqa: F401
from app.models.character import Character  # noqa: F401
from app.models.chat import Chat  # noqa: F401
from app.models.message import Message  # noqa: F401

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SQLModel.metadata.create_all(engine)
