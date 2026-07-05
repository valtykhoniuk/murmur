from sqlmodel import Field, SQLModel
from app.utils import utc_now
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

DEFAULT_CHAT_SETTINGS = {
    "temperature": 0.7,
    "reply_length": "medium",
    "speech_style": "equal",
    "initiativity": "medium",
}

class Chat(SQLModel, table=True):
    __tablename__ = "chats"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    character_id: int = Field(foreign_key="characters.id", index=True)
    created_at: datetime = Field(default_factory=utc_now)
    chat_settings: dict = Field(
        default_factory=lambda: DEFAULT_CHAT_SETTINGS.copy(),
        sa_column=Column(JSON),
    )
