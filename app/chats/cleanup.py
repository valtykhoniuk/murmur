from sqlmodel import Session, select

from app.models.chat import Chat
from app.models.message import Message
from app.models.summary import Summary


def delete_chat(session: Session, chat: Chat) -> None:
    summaries = session.exec(
        select(Summary).where(Summary.chat_id == chat.id)
    ).all()
    for summary in summaries:
        session.delete(summary)

    messages = session.exec(
        select(Message).where(Message.chat_id == chat.id)
    ).all()
    for message in messages:
        session.delete(message)

    session.delete(chat)


def delete_character_chats(session: Session, character_id: int) -> None:
    chats = session.exec(
        select(Chat).where(Chat.character_id == character_id)
    ).all()
    for chat in chats:
        delete_chat(session, chat)
