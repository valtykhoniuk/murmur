from enum import StrEnum
from app.utils import utc_now
from sqlmodel import Field, SQLModel
from datetime import datetime

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
