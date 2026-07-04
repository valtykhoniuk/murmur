from sqlmodel import Field, SQLModel
from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Chat(SQLModel, table=True):
    __tablename__ = "chats"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    character_id: int = Field(foreign_key="characters.id", index=True)
    created_at: datetime = Field(default_factory=utc_now)
