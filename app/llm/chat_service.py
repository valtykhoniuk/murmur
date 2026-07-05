import logging
import os

from fastapi import HTTPException

from app.llm.chain import build_chain
from app.llm.context import history_for_chain
from app.llm.history import to_langchain_messages
from app.llm.prompts import build_system_prompt

logger = logging.getLogger(__name__)


def generate_reply(
    *,
    persona: str,
    character_name: str,
    history: list,
    user_input: str,
) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured",
        )

    chain_history = history_for_chain(history)
    lc_history = to_langchain_messages(chain_history)
    system_prompt = build_system_prompt(character_name, persona)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    logger.info(
        "LLM call character=%s history_count=%s chain_history_count=%s model=%s",
        character_name,
        len(history),
        len(chain_history),
        model,
    )

    try:
        chain = build_chain()
        result = chain.invoke(
            {
                "system_prompt": system_prompt,
                "history": lc_history,
                "user_input": user_input,
            }
        )
    except Exception:
        logger.exception("LLM call failed character=%s", character_name)
        raise HTTPException(status_code=503, detail="Model temporarily unavailable")

    return result.content
