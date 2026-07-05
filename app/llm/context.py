from app.models.message import MessageRole

MAX_MESSAGES = 20


def trim_history(messages: list) -> list:
    return messages[-MAX_MESSAGES:]


def history_for_chain(messages: list) -> list:
    trimmed = trim_history(messages)
    if trimmed and trimmed[-1].role == MessageRole.user:
        return trimmed[:-1]
    return trimmed
