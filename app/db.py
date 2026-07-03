from sqlmodel import Session, SQLModel, create_engine

from app.config import DATABASE_URL
from app.models.user import User  # noqa: F401 — register model for create_all
from app.models.character import Character # noqa: F401 — register model for create_all

engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SQLModel.metadata.create_all(engine)
