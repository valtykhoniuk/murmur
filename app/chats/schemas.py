from datetime import datetime

from pydantic import BaseModel


class ChatCreate(BaseModel):
    character_id: int


class ChatRead(BaseModel):
    id: int
    user_id: int
    character_id: int
    character_name: str
    created_at: datetime


class MessageCreate(BaseModel):
    content: str


class MessageRead(BaseModel):
    id: int
    chat_id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SendMessageResponse(BaseModel):
    user_message: MessageRead
    assistant_message: MessageRead
