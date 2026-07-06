from sqlmodel import Session, select

from app.chats.schemas import ChatRead, ChatSettings
from app.models.character import Character
from app.models.chat import Chat, DEFAULT_CHAT_SETTINGS
from app.models.message import Message


def parse_chat_settings(chat: Chat) -> ChatSettings:
    raw = chat.chat_settings or DEFAULT_CHAT_SETTINGS
    return ChatSettings.model_validate(raw)


def _preview_text(content: str, max_len: int = 100) -> str:
    text = " ".join(content.split())
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def chat_to_read(chat: Chat, session: Session) -> ChatRead:
    character = session.get(Character, chat.character_id)

    last_message = session.exec(
        select(Message)
        .where(Message.chat_id == chat.id)
        .order_by(Message.created_at.desc())
    ).first()

    message_count = len(
        session.exec(select(Message).where(Message.chat_id == chat.id)).all()
    )

    preview = _preview_text(last_message.content) if last_message else None

    return ChatRead(
        id=chat.id,
        user_id=chat.user_id,
        character_id=chat.character_id,
        character_name=character.name if character else f"Character #{chat.character_id}",
        character_avatar_url=character.avatar_url if character else "",
        created_at=chat.created_at,
        chat_settings=parse_chat_settings(chat),
        preview=preview,
        message_count=message_count,
    )
