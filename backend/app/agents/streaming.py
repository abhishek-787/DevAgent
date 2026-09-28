import json
from typing import Iterator

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
)

def _event(
    event_type: str,
    **data,
) -> str:
    payload = {
        "type": event_type,
        **data,
    }

    return (
        json.dumps(
            payload,
            ensure_ascii=False,
        )
        + "\n"
    )

def _tool_call_events(
    message: AIMessage,
) -> list[str]:

    events: list[str] = []

    for tool_call in (
        message.tool_calls
    ):
        events.append(
            _event(
                "tool_requested",
                tool=(
                    tool_call["name"]
                ),
                arguments=(
                    tool_call.get(
                        "args",
                        {},
                    )
                ),
                tool_call_id=(
                    tool_call.get(
                        "id"
                    )
                ),
            )
        )

    return events

def _tool_result_event(
    message: ToolMessage,
) -> str:

    content = (
        message.content
        if isinstance(
            message.content,
            str,
        )
        else str(
            message.content
        )
    )

    return _event(
        "tool_completed",
        tool=(
            message.name
            or "unknown"
        ),
        tool_call_id=(
            message.tool_call_id
        ),
        result_preview=(
            content[:1000]
        ),
    )

def _message_events(
    message,
) -> list[str]:

    if isinstance(
        message,
        AIMessage,
    ):
        if message.tool_calls:
            return (
                _tool_call_events(
                    message
                )
            )

        if (
            isinstance(
                message.content,
                str,
            )
            and message.content.strip()
        ):
            return [
                _event(
                    "agent_message",
                    content=(
                        message.content
                        .strip()
                    ),
                )
            ]

    if isinstance(
        message,
        ToolMessage,
    ):
        return [
            _tool_result_event(
                message
            )
        ]

    return []