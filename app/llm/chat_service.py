import logging
import os

from fastapi import HTTPException
from langchain_core.messages import AIMessage

from app.llm.chain import build_chain
from app.llm.context import history_for_chain
from app.llm.history import to_langchain_messages
from app.llm.prompts import build_system_prompt

logger = logging.getLogger(__name__)


def _ensure_openai_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured",
        )


def _prepare_chain_inputs(
    *,
    persona: str,
    character_name: str,
    history: list,
    user_input: str,
) -> dict:
    chain_history = history_for_chain(history)
    lc_history = to_langchain_messages(chain_history)
    system_prompt = build_system_prompt(character_name, persona)
    return {
        "system_prompt": system_prompt,
        "history": lc_history,
        "user_input": user_input,
    }


def generate_reply(
    *,
    persona: str,
    character_name: str,
    history: list,
    user_input: str,
) -> str:
    _ensure_openai_key()

    inputs = _prepare_chain_inputs(
        persona=persona,
        character_name=character_name,
        history=history,
        user_input=user_input,
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    logger.info(
        "LLM invoke character=%s history_count=%s model=%s",
        character_name,
        len(history),
        model,
    )

    chain = build_chain()
    try:
        result = chain.invoke(inputs)
    except Exception:
        logger.exception("LLM invoke failed character=%s", character_name)
        raise HTTPException(status_code=503, detail="Model temporarily unavailable")

    if not isinstance(result, AIMessage):
        raise HTTPException(status_code=503, detail="Model returned an invalid response")

    content = result.content
    if not isinstance(content, str) or not content.strip():
        raise HTTPException(status_code=503, detail="Model returned an empty response")

    return content
