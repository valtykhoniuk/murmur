import logging
import os

from fastapi import HTTPException
from langchain_core.messages import AIMessage

from app.chats.schemas import ChatSettings
from app.llm.chain import build_chain
from app.llm.client import REPLY_LENGTH_MAX_TOKENS
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
    settings: ChatSettings,
) -> dict:
    chain_history = history_for_chain(history)
    lc_history = to_langchain_messages(chain_history)
    system_prompt = build_system_prompt(
        character_name,
        persona,
        reply_length=settings.reply_length,
        speech_style=settings.speech_style,
        initiativity=settings.initiativity,
    )
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
    settings: ChatSettings,
) -> str:
    _ensure_openai_key()

    inputs = _prepare_chain_inputs(
        persona=persona,
        character_name=character_name,
        history=history,
        user_input=user_input,
        settings=settings,
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_tokens = REPLY_LENGTH_MAX_TOKENS.get(settings.reply_length)

    logger.info(
        "LLM invoke character=%s history_count=%s model=%s "
        "temperature=%s reply_length=%s speech_style=%s initiativity=%s max_tokens=%s",
        character_name,
        len(history),
        model,
        settings.temperature,
        settings.reply_length,
        settings.speech_style,
        settings.initiativity,
        max_tokens,
    )

    chain = build_chain(
        temperature=settings.temperature,
        max_tokens=max_tokens,
    )
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
