from datetime import datetime, timezone
from enum import StrEnum

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MessageRole(StrEnum):
    user = "user"
    character = "character"
    scene = "scene"


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chats.id", index=True)
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=utc_now)
