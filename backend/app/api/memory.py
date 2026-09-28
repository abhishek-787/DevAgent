from fastapi import (
    APIRouter,
    HTTPException,
)
from pydantic import (
    BaseModel,
    Field,
)

from app.memory.service import (
    delete_memory,
    list_recent_tasks,
    list_workspace_memories,
    upsert_memory,
)

from app.memory.service import (
    delete_memory,
    list_conversation_tasks,
    list_recent_tasks,
    list_workspace_memories,
    upsert_memory,
)


router = APIRouter(
    prefix="/memory",
    tags=["Memory"],
)


class MemoryRequest(
    BaseModel
):
    key: str = Field(
        min_length=1,
        max_length=200,
    )

    value: str = Field(
        min_length=1,
        max_length=5000,
    )

@router.post("/entries")
def save_memory(
    request: MemoryRequest,
):
    try:
        memory = upsert_memory(
            key=request.key,
            value=request.value,
        )

        return {
            "key":
                memory.memory_key,

            "value":
                memory.memory_value,

            "saved": True,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/entries")
def get_memories():

    memories = (
        list_workspace_memories()
    )

    return {
        "count":
            len(memories),

        "memories": [
            {
                "key":
                    memory.memory_key,

                "value":
                    memory.memory_value,

                "updated_at":
                    memory.updated_at,
            }
            for memory
            in memories
        ],
    }

@router.delete(
    "/entries/{memory_key}"
)
def remove_memory(
    memory_key: str,
):
    try:
        deleted = delete_memory(
            memory_key
        )

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Memory was not found."
                ),
            )

        return {
            "deleted": True,
            "key": memory_key,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.get("/tasks")
def get_task_history(
    limit: int = 20,
):
    try:
        tasks = list_recent_tasks(
            limit=limit
        )

        return {
            "count": len(tasks),

            "tasks": [
                {
                    "thread_id":
                        task.thread_id,

                    "user_message":
                        task.user_message,

                    "status":
                        task.status,

                    "answer":
                        task.answer,

                    "tools_used":
                        task.tools_used,

                    "tool_rounds":
                        task.tool_rounds,

                    "failed_test_runs":
                        task.failed_test_runs,

                    "created_at":
                        task.created_at,

                    "updated_at":
                        task.updated_at,
                }
                for task
                in tasks
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/conversation"
)
def get_conversation_history(
    limit: int = 20,
):
    try:
        tasks = (
            list_conversation_tasks(
                limit=limit
            )
        )

        messages = []

        for task in tasks:

            messages.append(
                {
                    "id":
                        (
                            f"{task.thread_id}"
                            ":user"
                        ),

                    "thread_id":
                        task.thread_id,

                    "role":
                        "user",

                    "content":
                        task.user_message,

                    "created_at":
                        task.created_at,
                }
            )

            answer = (
                task.answer
                or ""
            ).strip()

            if answer:
                messages.append(
                    {
                        "id":
                            (
                                f"{task.thread_id}"
                                ":agent"
                            ),

                        "thread_id":
                            task.thread_id,

                        "role":
                            "agent",

                        "content":
                            answer,

                        "created_at":
                            task.updated_at,
                    }
                )

        return {
            "count":
                len(messages),

            "messages":
                messages,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc