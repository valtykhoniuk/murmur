from fastapi import Depends, HTTPException
from sqlmodel import Session

from app.auth.deps import get_current_user
from app.db import get_session
from app.models.chat import Chat
from app.models.user import User


def get_current_chat(
    chat_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Chat:
    chat = session.get(Chat, chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat
