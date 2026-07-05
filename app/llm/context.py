from app.models.message import MessageRole

DEFAULT_MAX_MESSAGES = 20
MIN_MAX_MESSAGES = 5
MAX_MAX_MESSAGES = 30


def trim_history(messages: list, max_messages: int = DEFAULT_MAX_MESSAGES) -> list:
    limit = max(MIN_MAX_MESSAGES, min(max_messages, MAX_MAX_MESSAGES))
    return messages[-limit:]


def history_for_chain(
    messages: list,
    max_messages: int = DEFAULT_MAX_MESSAGES,
) -> list:
    trimmed = trim_history(messages, max_messages)
    if trimmed and trimmed[-1].role == MessageRole.user:
        return trimmed[:-1]
    return trimmed
