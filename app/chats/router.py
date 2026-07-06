import os

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.auth.deps import get_current_user
from app.chats.cleanup import delete_chat
from app.chats.demo_limit import ensure_demo_can_send
from app.chats.deps import get_current_chat
from app.chats.helpers import chat_to_read, parse_chat_settings
from app.chats.schemas import (
    ChatCreate,
    ChatRead,
    ChatUpdate,
    MessageCreate,
    MessageRead,
    SendMessageResponse,
)
from app.db import get_session
from app.llm.chat_service import run_chat_graph
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
    chats = session.exec(
        select(Chat)
        .where(Chat.user_id == current_user.id)
        .order_by(Chat.created_at.desc())
    ).all()
    return [chat_to_read(chat, session) for chat in chats]


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

    return chat_to_read(chat, session)


@router.get("/{chat_id}", response_model=ChatRead)
def get_chat(
    chat: Chat = Depends(get_current_chat),
    session: Session = Depends(get_session),
):
    return chat_to_read(chat, session)


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
    return chat_to_read(chat, session)


@router.delete("/{chat_id}", status_code=204)
def delete_chat_endpoint(
    chat: Chat = Depends(get_current_chat),
    session: Session = Depends(get_session),
):
    delete_chat(session, chat)
    session.commit()


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
    current_user: User = Depends(get_current_user),
):
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY is not configured")

    ensure_demo_can_send(session, current_user)

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

    settings = parse_chat_settings(chat)
    assistant_content = run_chat_graph(
        session=session,
        chat_id=chat.id,
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
