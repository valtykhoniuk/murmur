from sqlmodel import Session, select
from app.models.summary import Summary

def load_chat_summary(session: Session, chat_id: int) -> str:
    row = session.exec(
        select(Summary)
        .where(Summary.chat_id == chat_id)
        .order_by(Summary.created_at.desc())
    ).first()
    return row.summary if row else ""

def save_chat_summary(
    session: Session,
    *,
    chat_id: int,
    summary: str,
    up_to_message_id: int | None,
) -> None:
    session.add(
        Summary(
            chat_id=chat_id,
            summary=summary,
            up_to_message_id=up_to_message_id,
        )
    )
    session.commit()