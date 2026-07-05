from langchain_core.messages import AIMessage, HumanMessage

from app.models.message import MessageRole


def to_langchain_messages(db_messages: list) -> list:
    out = []
    for msg in db_messages:
        if msg.role == MessageRole.user:
            out.append(HumanMessage(content=msg.content))
        elif msg.role in (MessageRole.character, MessageRole.scene):
            out.append(AIMessage(content=msg.content))
    return out
