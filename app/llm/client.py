import os

from langchain_openai import ChatOpenAI

REPLY_LENGTH_MAX_TOKENS = {
    "short": 120,
    "medium": 400,
    "long": 900,
}


def get_llm(
    temperature: float = 0.8,
    max_tokens: int | None = None,
) -> ChatOpenAI:
    kwargs: dict = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": temperature,
    }
    if max_tokens is not None:
        kwargs["max_tokens"] = max_tokens
    return ChatOpenAI(**kwargs)
