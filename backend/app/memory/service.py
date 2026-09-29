from sqlalchemy import (
    select,
)

from app.memory.models import (
    AgentAuditEvent,
    AgentTask,
    WorkspaceMemory,
)
from app.memory.database import (
    get_session,
)
from app.workspace.manager import (
    workspace_manager,
)


def _workspace_path() -> str:
    return (
        workspace_manager
        .get_workspace()
        .as_posix()
    )

def upsert_memory(
    key: str,
    value: str,
) -> WorkspaceMemory:

    cleaned_key = key.strip()
    cleaned_value = value.strip()

    if not cleaned_key:
        raise ValueError(
            "Memory key cannot be empty."
        )

    if not cleaned_value:
        raise ValueError(
            "Memory value cannot be empty."
        )

    workspace = (
        _workspace_path()
    )

    with get_session() as session:

        statement = (
            select(
                WorkspaceMemory
            )
            .where(
                WorkspaceMemory.workspace_path
                == workspace,

                WorkspaceMemory.memory_key
                == cleaned_key,
            )
        )

        memory = session.scalar(
            statement
        )

        if memory is None:
            memory = WorkspaceMemory(
                workspace_path=workspace,
                memory_key=cleaned_key,
                memory_value=cleaned_value,
            )

            session.add(
                memory
            )

        else:
            memory.memory_value = (
                cleaned_value
            )

        session.commit()

        return memory


def list_workspace_memories(
) -> list[WorkspaceMemory]:

    workspace = (
        _workspace_path()
    )

    with get_session() as session:

        statement = (
            select(
                WorkspaceMemory
            )
            .where(
                WorkspaceMemory.workspace_path
                == workspace
            )
            .order_by(
                WorkspaceMemory.memory_key
            )
        )

        memories = list(
            session.scalars(
                statement
            )
        )

    return memories


def delete_memory(
    key: str,
) -> bool:

    cleaned_key = key.strip()

    if not cleaned_key:
        raise ValueError(
            "Memory key cannot be empty."
        )

    workspace = (
        _workspace_path()
    )

    with get_session() as session:

        statement = (
            select(
                WorkspaceMemory
            )
            .where(
                WorkspaceMemory.workspace_path
                == workspace,

                WorkspaceMemory.memory_key
                == cleaned_key,
            )
        )

        memory = session.scalar(
            statement
        )

        if memory is None:
            return False

        session.delete(
            memory
        )

        session.commit()

    return True


def build_workspace_memory_context(
) -> str:

    memories = (
        list_workspace_memories()
    )

    if not memories:
        return ""

    lines = [
        (
            f"- {memory.memory_key}: "
            f"{memory.memory_value}"
        )
        for memory
        in memories
    ]

    return "\n".join(
        lines
    )


def create_agent_task(
    thread_id: str,
    user_message: str,
) -> None:

    workspace = (
        _workspace_path()
    )

    with get_session() as session:

        task = AgentTask(
            thread_id=thread_id,
            workspace_path=workspace,
            user_message=user_message,
            status="running",
            answer=None,
            tools_used=[],
            tool_rounds=0,
            failed_test_runs=0,
        )

        session.add(
            task
        )

        session.commit()

def update_agent_task(
    thread_id: str,
    status: str,
    answer: str,
    tools_used: list[str],
    tool_rounds: int,
    failed_test_runs: int,
) -> None:

    with get_session() as session:

        statement = (
            select(
                AgentTask
            )
            .where(
                AgentTask.thread_id
                == thread_id
            )
        )

        task = session.scalar(
            statement
        )

        if task is None:
            raise ValueError(
                "Agent task was not found."
            )

        task.status = status
        task.answer = answer
        task.tools_used = tools_used
        task.tool_rounds = (
            tool_rounds
        )
        task.failed_test_runs = (
            failed_test_runs
        )

        session.commit()


def list_recent_tasks(
    limit: int = 20,
) -> list[AgentTask]:

    if (
        limit < 1
        or limit > 100
    ):
        raise ValueError(
            "Task history limit must "
            "be between 1 and 100."
        )

    workspace = (
        _workspace_path()
    )

    with get_session() as session:

        statement = (
            select(
                AgentTask
            )
            .where(
                AgentTask.workspace_path
                == workspace
            )
            .order_by(
                AgentTask.created_at.desc()
            )
            .limit(limit)
        )

        tasks = list(
            session.scalars(
                statement
            )
        )

    return tasks


def record_audit_event(
    thread_id: str,
    event_type: str,
    details: dict | None = None,
) -> None:

    cleaned_thread_id = (
        thread_id.strip()
    )

    cleaned_event_type = (
        event_type.strip()
    )

    if not cleaned_thread_id:
        raise ValueError(
            "Thread ID is required."
        )

    if not cleaned_event_type:
        raise ValueError(
            "Audit event type "
            "cannot be empty."
        )

    workspace = (
        _workspace_path()
    )

    with get_session() as session:

        event = AgentAuditEvent(
            thread_id=(
                cleaned_thread_id
            ),
            workspace_path=workspace,
            event_type=(
                cleaned_event_type
            ),
            details=(
                details or {}
            ),
        )

        session.add(
            event
        )

        session.commit()

def list_audit_events(
    thread_id: str,
) -> list[AgentAuditEvent]:

    cleaned_thread_id = (
        thread_id.strip()
    )

    if not cleaned_thread_id:
        raise ValueError(
            "Thread ID is required."
        )

    workspace = (
        _workspace_path()
    )

    with get_session() as session:

        statement = (
            select(
                AgentAuditEvent
            )
            .where(
                AgentAuditEvent.thread_id
                == cleaned_thread_id,

                AgentAuditEvent.workspace_path
                == workspace,
            )
            .order_by(
                AgentAuditEvent.id
            )
        )

        events = list(
            session.scalars(
                statement
            )
        )

    return events


def list_conversation_tasks(
    limit: int = 20,
) -> list[AgentTask]:

    if (
        limit < 1
        or limit > 100
    ):
        raise ValueError(
            "Conversation history limit "
            "must be between 1 and 100."
        )

    workspace = (
        _workspace_path()
    )

    with get_session() as session:

        statement = (
            select(
                AgentTask
            )
            .where(
                AgentTask.workspace_path
                == workspace,

                AgentTask.status
                == "completed",

                AgentTask.answer
                .is_not(None),
            )
            .order_by(
                AgentTask.created_at.desc()
            )
            .limit(limit)
        )

        tasks = list(
            session.scalars(
                statement
            )
        )

    tasks.reverse()

    return tasks


def build_recent_conversation_context(
    limit: int = 8,
) -> str:

    tasks = (
        list_conversation_tasks(
            limit=limit
        )
    )

    if not tasks:
        return ""

    sections: list[str] = []

    for task in tasks:

        answer = (
            task.answer
            or ""
        ).strip()

        if not answer:
            continue

        sections.append(
            "\n".join(
                [
                    "USER:",
                    task.user_message,
                    "",
                    "DEVAGENT:",
                    answer,
                ]
            )
        )

    return "\n\n---\n\n".join(
        sections
    )