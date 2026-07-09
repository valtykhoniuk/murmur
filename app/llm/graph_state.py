from typing import TypedDict


class ChatGraphState(TypedDict, total=False):
    # inputs
    chat_id: int
    persona: str
    character_name: str
    history: list
    user_input: str
    settings: dict
    summary: str

    # built in build_context
    system_prompt: str
    judge_pass: bool
    judge_response: str
    retry_count: int

    # output
    assistant_content: str
    new_summary: str
    up_to_message_id: int | None
