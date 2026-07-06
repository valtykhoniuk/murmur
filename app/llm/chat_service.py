import logging
import os

from fastapi import HTTPException
from sqlmodel import Session

from app.chats.schemas import ChatSettings
from app.llm.graph import build_chat_graph
from app.llm.memory import load_chat_summary, save_chat_summary

logger = logging.getLogger(__name__)


def _ensure_openai_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured",
        )


def run_chat_graph(
    *,
    session: Session,
    chat_id: int,
    persona: str,
    character_name: str,
    history: list,
    user_input: str,
    settings: ChatSettings,
) -> str:
    _ensure_openai_key()

    summary = load_chat_summary(session, chat_id)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    initial_state = {
        "chat_id": chat_id,
        "persona": persona,
        "character_name": character_name,
        "history": history,
        "user_input": user_input,
        "settings": settings.model_dump(),
        "summary": summary,
    }

    logger.info(
        "LangGraph chat_id=%s character=%s history_count=%s summary_len=%s model=%s",
        chat_id,
        character_name,
        len(history),
        len(summary),
        model,
    )

    graph = build_chat_graph()
    try:
        final_state = graph.invoke(initial_state)
    except Exception:
        logger.exception("LangGraph failed chat_id=%s character=%s", chat_id, character_name)
        raise HTTPException(status_code=503, detail="Model temporarily unavailable")

    content = final_state.get("assistant_content", "")
    if not isinstance(content, str) or not content.strip():
        raise HTTPException(status_code=503, detail="Model returned an empty response")

    new_summary = final_state.get("new_summary")
    if new_summary:
        save_chat_summary(
            session,
            chat_id=chat_id,
            summary=new_summary,
            up_to_message_id=final_state.get("up_to_message_id"),
        )

    return content.strip()
