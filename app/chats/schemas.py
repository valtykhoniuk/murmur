from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    character_id: int


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

class ChatSettings(BaseModel):
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    reply_length: Literal["short", "medium", "long"] = "medium"
    speech_style: Literal["talkative", "equal", "initiative"] = "equal"
    initiativity: Literal["rock", "medium", "long"] = "medium"
    max_messages: int = Field(default=20, ge=5, le=30)

class ChatUpdate(BaseModel):
    temperature: float = Field(ge=0.0, le=1.0)
    reply_length: Literal["short", "medium", "long"]
    speech_style: Literal["talkative", "equal", "initiative"]
    initiativity: Literal["rock", "medium", "long"]
    max_messages: int = Field(ge=5, le=30)

class ChatRead(BaseModel):
    id: int
    user_id: int
    character_id: int
    character_name: str
    created_at: datetime
    chat_settings: ChatSettings

