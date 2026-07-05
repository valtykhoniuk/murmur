from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.llm.client import get_llm


def build_chain(*, temperature: float = 0.8, max_tokens: int | None = None):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            MessagesPlaceholder("history"),
            ("human", "{user_input}"),
        ]
    )
    return prompt | get_llm(temperature=temperature, max_tokens=max_tokens)
