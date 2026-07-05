import os

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.deps import get_current_user
from app.chats.deps import get_current_chat
from app.chats.schemas import (
    ChatCreate,
    ChatRead,
    ChatSettings,
    ChatUpdate,
    MessageCreate,
    MessageRead,
    SendMessageResponse,
)
from app.db import get_session
from app.llm.chat_service import generate_reply
from app.models.character import Character
from app.models.chat import Chat, DEFAULT_CHAT_SETTINGS
from app.models.message import Message, MessageRole
from app.models.user import User

router = APIRouter()


def _parse_chat_settings(chat: Chat) -> ChatSettings:
    raw = chat.chat_settings or DEFAULT_CHAT_SETTINGS
    return ChatSettings.model_validate(raw)


def _chat_to_read(chat: Chat, session: Session) -> ChatRead:
    character = session.get(Character, chat.character_id)
    return ChatRead(
        id=chat.id,
        user_id=chat.user_id,
        character_id=chat.character_id,
        character_name=character.name if character else f"Character #{chat.character_id}",
        created_at=chat.created_at,
        chat_settings=_parse_chat_settings(chat),
    )


@router.get("", response_model=list[ChatRead])
def list_chats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    chats = session.exec(select(Chat).where(Chat.user_id == current_user.id)).all()
    return [_chat_to_read(chat, session) for chat in chats]


@router.post("", response_model=ChatRead)
def create_chat(
    body: ChatCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    character = session.get(Character, body.character_id)
    if not character or character.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Character not found")

    chat = Chat(user_id=current_user.id, character_id=body.character_id)
    session.add(chat)
    session.commit()
    session.refresh(chat)

    if character.start_message:
        greeting = Message(
            chat_id=chat.id,
            role=MessageRole.character,
            content=character.start_message,
        )
        session.add(greeting)
        session.commit()

    return _chat_to_read(chat, session)


@router.get("/{chat_id}", response_model=ChatRead)
def get_chat(
    chat: Chat = Depends(get_current_chat),
    session: Session = Depends(get_session),
):
    return _chat_to_read(chat, session)


@router.patch("/{chat_id}", response_model=ChatRead)
def update_chat(
    body: ChatUpdate,
    chat: Chat = Depends(get_current_chat),
    session: Session = Depends(get_session),
):
    chat.chat_settings = body.model_dump()
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return _chat_to_read(chat, session)


@router.get("/{chat_id}/messages", response_model=list[MessageRead])
def list_messages(
    chat: Chat = Depends(get_current_chat),
    session: Session = Depends(get_session),
):
    messages = session.exec(
        select(Message)
        .where(Message.chat_id == chat.id)
        .order_by(Message.created_at)
    ).all()
    return messages


@router.post("/{chat_id}/message", response_model=SendMessageResponse)
def send_message(
    body: MessageCreate,
    chat: Chat = Depends(get_current_chat),
    session: Session = Depends(get_session),
):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")

    user_message = Message(
        chat_id=chat.id,
        role=MessageRole.user,
        content=body.content,
    )
    session.add(user_message)
    session.commit()
    session.refresh(user_message)

    character = session.get(Character, chat.character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    history = session.exec(
        select(Message)
        .where(Message.chat_id == chat.id)
        .order_by(Message.created_at)
    ).all()

    settings = _parse_chat_settings(chat)
    assistant_content = generate_reply(
        persona=character.persona,
        character_name=character.name,
        history=history,
        user_input=body.content,
        settings=settings,
    )

    assistant_message = Message(
        chat_id=chat.id,
        role=MessageRole.character,
        content=assistant_content,
    )
    session.add(assistant_message)
    session.commit()
    session.refresh(assistant_message)

    return SendMessageResponse(
        user_message=user_message,
        assistant_message=assistant_message,
    )
