from fastapi import (
    APIRouter,
    HTTPException,
)
from pydantic import BaseModel

from app.agents.coding_service import (
    ask_coding_model,
)

from app.agents.coding_tools import (
    CODING_TOOLS,
)

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)

from app.agents.coding_agent import (
    coding_agent_graph,
)

from app.agents.agent_service import (
    run_coding_task,
)

from app.agents.agent_service import (
    resume_coding_task,
    run_coding_task,
)

from app.agents.agent_service import (
    get_task_recovery_status,
    resume_coding_task,
    run_coding_task,
)

from fastapi.responses import (
    StreamingResponse,
)

from app.agents.agent_service import (
    resume_coding_task,
    run_coding_task,
    stream_coding_task,
    stream_resume_coding_task,
)

router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


class ModelTestRequest(BaseModel):
    message: str

class ToolTestRequest(BaseModel):
    tool_name: str
    arguments: dict

class AgentGraphTestRequest(
    BaseModel
):
    message: str

class AgentTaskRequest(
    BaseModel
):
    message: str

class ApprovalRequest(
    BaseModel
):
    thread_id: str
    approved: bool


@router.post("/model-test")
def model_test(
    request: ModelTestRequest,
):
    try:
        answer = ask_coding_model(
            request.message
        )

        return {
            "model": "coding",
            "answer": answer,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Coding model request failed."
            ),
        ) from exc

@router.get("/tools")
def available_tools():
    return {
        "count": len(CODING_TOOLS),
        "tools": [
            {
                "name": coding_tool.name,
                "description":
                    coding_tool.description,
            }
            for coding_tool
            in CODING_TOOLS
        ],
    }

@router.post("/tool-test")
def tool_test(
    request: ToolTestRequest,
):
    tool_map = {
        coding_tool.name: coding_tool
        for coding_tool in CODING_TOOLS
    }

    selected_tool = tool_map.get(
        request.tool_name
    )

    if selected_tool is None:
        raise HTTPException(
            status_code=400,
            detail="Unknown coding tool.",
        )

    try:
        result = selected_tool.invoke(
            request.arguments
        )

        return {
            "tool": request.tool_name,
            "result": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"{type(exc).__name__}: "
                f"{str(exc)}"
            ),
        ) from exc

@router.post("/graph-test")
def graph_test(
    request: AgentGraphTestRequest,
):
    cleaned_message = (
        request.message.strip()
    )

    if not cleaned_message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:
        result = coding_agent_graph.invoke(
    {
        "messages": [
            HumanMessage(
                content=cleaned_message
            )
        ],
        "tool_rounds": 0,
        "failed_test_runs": 0,
    },
    config={
        "recursion_limit": 40
    },
)

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Coding agent execution "
                "failed."
            ),
        ) from exc

    messages = result["messages"]

    final_message = messages[-1]

    tool_calls = []
    tool_results = []

    for message in messages:

        if (
            isinstance(
                message,
                AIMessage,
            )
            and message.tool_calls
        ):
            for call in message.tool_calls:
                tool_calls.append(
                    {
                        "name":
                            call["name"],
                        "args":
                            call["args"],
                    }
                )

        if isinstance(
            message,
            ToolMessage,
        ):
            tool_results.append(
                {
                    "name":
                        message.name,
                    "content":
                        message.content,
                }
            )

    return {
    "answer":
        final_message.content,
    "tool_calls":
        tool_calls,
    "tool_results":
        tool_results,
    "tool_rounds":
        result.get(
            "tool_rounds",
            0,
        ),
    "message_count":
        len(messages),
}


@router.post("/task")
def agent_task(
    request: AgentTaskRequest,
):
    try:
        return run_coding_task(
            request.message
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
            f"{type(exc).__name__}: "
            f"{str(exc)}"
        ),
        ) from exc

@router.post("/approval")
def approve_agent_action(
    request: ApprovalRequest,
):
    try:
        return resume_coding_task(
            thread_id=(
                request.thread_id
            ),
            approved=(
                request.approved
            ),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.get(
    "/recovery/{thread_id}"
)
def get_agent_recovery(
    thread_id: str,
):
    try:
        return (
            get_task_recovery_status(
                thread_id
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.post("/stream")
def stream_agent_task(
    request: AgentTaskRequest,
):
    return StreamingResponse(
        stream_coding_task(
            request.message
        ),
        media_type=(
            "application/x-ndjson"
        ),
        headers={
            "Cache-Control":
                "no-cache",

            "X-Accel-Buffering":
                "no",
        },
    )

@router.post(
    "/approval/stream"
)
def stream_agent_approval(
    request: ApprovalRequest,
):
    return StreamingResponse(
        stream_resume_coding_task(
            thread_id=(
                request.thread_id
            ),
            approved=(
                request.approved
            ),
        ),
        media_type=(
            "application/x-ndjson"
        ),
        headers={
            "Cache-Control":
                "no-cache",

            "X-Accel-Buffering":
                "no",
        },
    )