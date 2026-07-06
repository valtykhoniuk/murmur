import os

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.chat import Chat
from app.models.message import Message, MessageRole
from app.models.user import User

DEMO_MESSAGE_LIMIT = int(os.getenv("DEMO_MESSAGE_LIMIT", "20"))


def count_user_messages(session: Session, user_id: int) -> int:
    messages = session.exec(
        select(Message)
        .join(Chat, Message.chat_id == Chat.id)
        .where(Chat.user_id == user_id, Message.role == MessageRole.user)
    ).all()
    return len(messages)


def ensure_demo_can_send(session: Session, user: User) -> None:
    if user.role != "public":
        return

    used = count_user_messages(session, user.id)
    if used >= DEMO_MESSAGE_LIMIT:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Demo limit reached ({DEMO_MESSAGE_LIMIT} messages). "
                "Sign in with a full account to continue."
            ),
        )
