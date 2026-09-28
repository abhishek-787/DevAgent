from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.agents.model import coding_model


CODING_SYSTEM_PROMPT = """
You are DevAgent, a local AI coding assistant.

Your role is to help with software development tasks.

For now, you do not have access to filesystem or terminal tools.
Do not pretend that you have opened, read, created, or modified files.

When answering coding questions:
- Be concise.
- Produce correct code.
- Explain important implementation decisions when useful.
"""
def ask_coding_model(
    message: str,
) -> str:

    cleaned_message = message.strip()

    if not cleaned_message:
        raise ValueError(
            "Message cannot be empty."
        )

    response = coding_model.invoke(
        [
            SystemMessage(
                content=CODING_SYSTEM_PROMPT
            ),
            HumanMessage(
                content=cleaned_message
            ),
        ]
    )

    if not isinstance(
        response.content,
        str,
    ):
        return str(response.content)

    return response.content