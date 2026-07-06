from sqlmodel import Field, SQLModel
from app.utils import utc_now
from datetime import datetime

class Summary(SQLModel, table=True):
    __tablename__="summaries"
    id: int | None = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chats.id", index=True)
    summary: str
    up_to_message_id: int | None = Field(default=None, foreign_key="messages.id")
    created_at: datetime = Field(default_factory=utc_now)