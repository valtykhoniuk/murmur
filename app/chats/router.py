from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.deps import get_current_user
from app.chats.deps import get_current_chat
from app.chats.schemas import (
    ChatCreate,
    ChatRead,
    MessageCreate,
    MessageRead,
    SendMessageResponse,
)
from app.db import get_session
from app.models.character import Character
from app.models.chat import Chat
from app.models.message import Message, MessageRole
from app.models.user import User

router = APIRouter()


@router.get("", response_model=list[ChatRead])
def list_chats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    chats = session.exec(select(Chat).where(Chat.user_id == current_user.id)).all()
    return chats


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

    return chat


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
    user_message = Message(
        chat_id=chat.id,
        role=MessageRole.user,
        content=body.content,
    )
    session.add(user_message)
    session.flush()

    assistant_message = Message(
        chat_id=chat.id,
        role=MessageRole.character,
        content=f"Echo: {body.content}",
    )
    session.add(assistant_message)
    session.commit()
    session.refresh(user_message)
    session.refresh(assistant_message)

    return SendMessageResponse(
        user_message=user_message,
        assistant_message=assistant_message,
    )
