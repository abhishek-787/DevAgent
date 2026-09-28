import uuid

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from langgraph.types import (
    Command,
)

from app.agents.coding_agent import (
    coding_agent_graph,
)

from app.memory.service import (
    build_recent_conversation_context,
    build_workspace_memory_context,
    create_agent_task,
    record_audit_event,
    update_agent_task,
)

from app.security.guardrails import (
    validate_task_message,
)

from typing import Iterator

from app.agents.streaming import (
    _event,
    _message_events,
)

def _persist_response(
    response: dict,
) -> dict:

    thread_id = (
        response["thread_id"]
    )

    update_agent_task(
        thread_id=thread_id,
        status=response["status"],
        answer=response["answer"],
        tools_used=(
            response["tools_used"]
        ),
        tool_rounds=(
            response["tool_rounds"]
        ),
        failed_test_runs=(
            response[
                "failed_test_runs"
            ]
        ),
    )

    if (
        response["status"]
        == "approval_required"
    ):
        record_audit_event(
            thread_id=thread_id,
            event_type=(
                "approval_requested"
            ),
            details={
                "approval":
                    response[
                        "approval"
                    ],

                "tools_requested":
                    response[
                        "tools_used"
                    ],
            },
        )

    elif (
        response["status"]
        == "completed"
    ):
        record_audit_event(
            thread_id=thread_id,
            event_type=(
                "task_completed"
            ),
            details={
                "answer":
                    response["answer"],

                "tools_used":
                    response[
                        "tools_used"
                    ],

                "tool_rounds":
                    response[
                        "tool_rounds"
                    ],

                "failed_test_runs":
                    response[
                        "failed_test_runs"
                    ],
            },
        )

    return response

def _graph_config(
    thread_id: str,
) -> dict:
    return {
        "configurable": {
            "thread_id": thread_id,
        },
        "recursion_limit": 40,
    }


def _extract_final_answer(
    messages: list,
) -> str:
    for message in reversed(
        messages
    ):
        if not isinstance(
            message,
            AIMessage,
        ):
            continue

        if not isinstance(
            message.content,
            str,
        ):
            continue

        content = (
            message.content.strip()
        )

        if content:
            return content

    return ""


def _extract_tools_used(
    messages: list,
) -> list[str]:
    tools_used: list[str] = []

    for message in messages:
        if not isinstance(
            message,
            AIMessage,
        ):
            continue

        for tool_call in (
            message.tool_calls
        ):
            tool_name = (
                tool_call.get(
                    "name"
                )
            )

            if isinstance(
                tool_name,
                str,
            ):
                tools_used.append(
                    tool_name
                )

    return tools_used


def _get_interrupt_payload(
    result: dict,
) -> dict | None:
    interrupts = result.get(
        "__interrupt__"
    )

    if not interrupts:
        return None

    first_interrupt = (
        interrupts[0]
    )

    value = getattr(
        first_interrupt,
        "value",
        None,
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    return {
        "message": str(value)
    }


def _build_response(
    result: dict,
    thread_id: str,
) -> dict:
    messages = result.get(
        "messages",
        [],
    )

    approval = (
        _get_interrupt_payload(
            result
        )
    )

    if approval is not None:
        return {
            "status":
                "approval_required",

            "thread_id":
                thread_id,

            "approval":
                approval,

            "answer":
                "",

            "tools_used":
                _extract_tools_used(
                    messages
                ),

            "tool_rounds":
                result.get(
                    "tool_rounds",
                    0,
                ),

            "failed_test_runs":
                result.get(
                    "failed_test_runs",
                    0,
                ),

            "tests_status":
                result.get(
                    "tests_status",
                    "not_run",
                ),
        }

    return {
        "status":
            "completed",

        "thread_id":
            thread_id,

        "answer":
            _extract_final_answer(
                messages
            ),

        "tools_used":
            _extract_tools_used(
                messages
            ),

        "tool_rounds":
            result.get(
                "tool_rounds",
                0,
            ),

        "failed_test_runs":
            result.get(
                "failed_test_runs",
                0,
            ),

        "tests_status":
            result.get(
                "tests_status",
                "not_run",
            ),
    }


def run_coding_task(
    message: str,
) -> dict:

    cleaned_message = (
        validate_task_message(
            message
        )
    )

    if not cleaned_message:
        raise ValueError(
            "Task message cannot be empty."
        )

    thread_id = (
        uuid.uuid4().hex
    )

    create_agent_task(
    thread_id=thread_id,
    user_message=cleaned_message,
)
    record_audit_event(
    thread_id=thread_id,
    event_type="task_started",
    details={
        "message":
            cleaned_message,
    },
)

    memory_context = (
        build_workspace_memory_context()
    )

    config = _graph_config(
        thread_id
    )

    conversation_context = (
    build_recent_conversation_context()
)

    initial_state = {
        "messages": [
            HumanMessage(
                content=cleaned_message
            )
        ],

        "tool_rounds":
            0,

        "failed_test_runs":
            0,

        "tests_status":
            "not_run",

        "memory_context":memory_context,
        "conversation_context": conversation_context,
    }

    result = (
        coding_agent_graph.invoke(
            initial_state,
            config=config,
        )
    )

    response = _build_response(
    result=result,
    thread_id=thread_id,
    )

    update_agent_task(
    thread_id=thread_id,
    status=response["status"],
    answer=response["answer"],
    tools_used=response[
        "tools_used"
    ],
    tool_rounds=response[
        "tool_rounds"
    ],
    failed_test_runs=response[
        "failed_test_runs"
    ],
    )
    

    return _persist_response(
    _build_response(
        result=result,
        thread_id=thread_id,
    )
)


def resume_coding_task(
    thread_id: str,
    approved: bool,
) -> dict:
    cleaned_thread_id = (
        thread_id.strip()
    )

    if not cleaned_thread_id:
        raise ValueError(
            "Thread ID is required."
        )

    config = _graph_config(
        cleaned_thread_id
    )

    snapshot = (
        coding_agent_graph
        .get_state(
            config
        )
    )

    if (
        "approval"
        not in snapshot.next
    ):
        raise ValueError(
            "This task is not waiting "
            "for approval."
        )

    record_audit_event(
    thread_id=(
        cleaned_thread_id
    ),
    event_type=(
        "approval_approved"
        if approved
        else "approval_rejected"
    ),
    details={
        "approved":
            approved,
    },
)

    result = (
        coding_agent_graph.invoke(
            Command(
                resume={
                    "approved":
                        approved,
                }
            ),
            config=config,
        )
    )

    response = _build_response(
    result=result,
    thread_id=thread_id,
    )

    update_agent_task(
        thread_id=thread_id,
        status=response["status"],
        answer=response["answer"],
        tools_used=response[
            "tools_used"
        ],
        tool_rounds=response[
            "tool_rounds"
        ],
        failed_test_runs=response[
            "failed_test_runs"
        ],
    )

    return _persist_response(
    _build_response(
        result=result,
        thread_id=(
            cleaned_thread_id
        ),
    )
)

def get_task_recovery_status(
    thread_id: str,
) -> dict:

    cleaned_thread_id = (
        thread_id.strip()
    )

    if not cleaned_thread_id:
        raise ValueError(
            "Thread ID is required."
        )

    config = _graph_config(
        cleaned_thread_id
    )

    snapshot = (
        coding_agent_graph
        .get_state(
            config
        )
    )

    next_nodes = list(
        snapshot.next
    )

    return {
        "thread_id":
            cleaned_thread_id,

        "resumable":
            bool(next_nodes),

        "next_nodes":
            next_nodes,

        "waiting_for_approval":
            (
                "approval"
                in next_nodes
            ),
    }


def _stream_graph_result(
    graph_input,
    config: dict,
    thread_id: str,
) -> Iterator[str]:

    seen_message_ids: set[str] = (
        set()
    )

    latest_state: dict = {}

    try:
        for state_update in (
            coding_agent_graph.stream(
                graph_input,
                config=config,
                stream_mode="values",
            )
        ):
            latest_state = (
                state_update
            )

            messages = (
                state_update.get(
                    "messages",
                    [],
                )
            )

            for message in messages:
                message_id = getattr(
                    message,
                    "id",
                    None,
                )

                if (
                    message_id
                    and message_id
                    in seen_message_ids
                ):
                    continue

                if message_id:
                    seen_message_ids.add(
                        message_id
                    )

                for event in (
                    _message_events(
                        message
                    )
                ):
                    yield event

        approval = (
            _get_interrupt_payload(
                latest_state
            )
        )

        if approval is not None:
            response = (
                _build_response(
                    result=latest_state,
                    thread_id=(
                        thread_id
                    ),
                )
            )

            _persist_response(
                response
            )

            yield _event(
                "approval_required",
                thread_id=(
                    thread_id
                ),
                approval=approval,
            )

            return

        response = _build_response(
            result=latest_state,
            thread_id=thread_id,
        )

        _persist_response(
            response
        )

        yield _event(
            "task_completed",
            thread_id=(
                thread_id
            ),
            answer=(
                response["answer"]
            ),
            tools_used=(
                response["tools_used"]
            ),
            tool_rounds=(
                response["tool_rounds"]
            ),
            failed_test_runs=(
                response[
                    "failed_test_runs"
                ]
            ),
        )

    except Exception as exc:
        yield _event(
            "error",
            thread_id=thread_id,
            error_type=(
                type(exc).__name__
            ),
            message=str(exc),
        )

def stream_coding_task(
    message: str,
) -> Iterator[str]:

    cleaned_message = (
        validate_task_message(
            message
        )
    )

    thread_id = (
        uuid.uuid4().hex
    )

    create_agent_task(
        thread_id=thread_id,
        user_message=(
            cleaned_message
        ),
    )

    record_audit_event(
        thread_id=thread_id,
        event_type=(
            "task_started"
        ),
        details={
            "message":
                cleaned_message,
        },
    )

    memory_context = (
        build_workspace_memory_context()
    )

    conversation_context = (
    build_recent_conversation_context()
)

    initial_state = {
        "messages": [
            HumanMessage(
                content=(
                    cleaned_message
                )
            )
        ],

        "tool_rounds":
            0,

        "failed_test_runs":
            0,

        "tests_status":
            "not_run",

        "memory_context":memory_context,
        "conversation_context": conversation_context,
    }

    config = _graph_config(
        thread_id
    )

    yield _event(
        "task_started",
        thread_id=thread_id,
        message=cleaned_message,
    )

    yield from _stream_graph_result(
        graph_input=(
            initial_state
        ),
        config=config,
        thread_id=thread_id,
    )

def stream_resume_coding_task(
    thread_id: str,
    approved: bool,
) -> Iterator[str]:

    cleaned_thread_id = (
        thread_id.strip()
    )

    if not cleaned_thread_id:
        raise ValueError(
            "Thread ID is required."
        )

    config = _graph_config(
        cleaned_thread_id
    )

    snapshot = (
        coding_agent_graph
        .get_state(
            config
        )
    )

    if (
        "approval"
        not in snapshot.next
    ):
        raise ValueError(
            "This task is not "
            "waiting for approval."
        )

    record_audit_event(
        thread_id=(
            cleaned_thread_id
        ),
        event_type=(
            "approval_approved"
            if approved
            else "approval_rejected"
        ),
        details={
            "approved":
                approved
        },
    )

    yield _event(
        "approval_decision",
        thread_id=(
            cleaned_thread_id
        ),
        approved=approved,
    )

    yield from _stream_graph_result(
        graph_input=Command(
            resume={
                "approved":
                    approved,
            }
        ),
        config=config,
        thread_id=(
            cleaned_thread_id
        ),
    )