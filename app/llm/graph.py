from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from app.llm.chain import build_chain
from app.llm.client import REPLY_LENGTH_MAX_TOKENS, get_llm
from app.llm.context import history_for_chain
from app.llm.graph_state import ChatGraphState
from app.llm.history import to_langchain_messages
from app.llm.prompts import SUMMARIZE_PROMPT, SUMMARY_BLOCK, build_system_prompt
from app.models.message import MessageRole


def build_chat_graph():
    graph = StateGraph(ChatGraphState)

    graph.add_node("build_context", build_context_node)
    graph.add_node("generate", generate_node)
    graph.add_node("update_memory", update_memory_node)

    graph.set_entry_point("build_context")
    graph.add_edge("build_context", "generate")
    graph.add_edge("generate", "update_memory")
    graph.add_edge("update_memory", END)

    return graph.compile()


def build_context_node(state: ChatGraphState) -> dict:
    settings = state["settings"]
    summary = state.get("summary") or ""

    base_prompt = build_system_prompt(
        state["character_name"],
        state["persona"],
        reply_length=settings["reply_length"],
        speech_style=settings["speech_style"],
        initiativity=settings["initiativity"],
    )
    if summary.strip():
        system_prompt = SUMMARY_BLOCK.format(summary=summary) + base_prompt
    else:
        system_prompt = base_prompt

    return {"system_prompt": system_prompt}


def generate_node(state: ChatGraphState) -> dict:
    settings = state["settings"]
    recent_messages = history_for_chain(
        state["history"],
        max_messages=settings["max_messages"],
    )
    lc_history = to_langchain_messages(recent_messages)

    chain = build_chain(
        temperature=settings["temperature"],
        max_tokens=REPLY_LENGTH_MAX_TOKENS.get(settings["reply_length"]),
    )
    result = chain.invoke({
        "system_prompt": state["system_prompt"],
        "history": lc_history,
        "user_input": state["user_input"],
    })
    content = result.content if isinstance(result.content, str) else str(result.content)
    return {"assistant_content": content}


def _format_messages_for_summary(messages: list) -> str:
    lines = []
    for msg in messages:
        role = "User" if msg.role == MessageRole.user else "Character"
        lines.append(f"{role}: {msg.content}")
    return "\n\n".join(lines)


def update_memory_node(state: ChatGraphState) -> dict:
    settings = state["settings"]
    max_messages = settings["max_messages"]
    history = state["history"]

    if len(history) <= max_messages:
        return {}

    old_summary = state.get("summary") or ""
    messages_to_summarize = history[:-max_messages]
    if not messages_to_summarize:
        return {}

    messages_text = _format_messages_for_summary(messages_to_summarize)
    prompt = SUMMARIZE_PROMPT.format(
        old_summary=old_summary or "(none)",
        messages_text=messages_text,
    )

    llm = get_llm(temperature=0, max_tokens=400)
    result = llm.invoke([HumanMessage(content=prompt)])

    new_summary = result.content if isinstance(result.content, str) else str(result.content)
    last_id = messages_to_summarize[-1].id
    return {
        "summary": new_summary.strip(),
        "new_summary": new_summary.strip(),
        "up_to_message_id": last_id,
    }
