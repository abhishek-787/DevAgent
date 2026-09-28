from fastapi import (
    APIRouter,
)
from pydantic import (
    BaseModel,
    Field,
)

from app.security.guardrails import (
    MAX_FAILED_TEST_RUNS,
    MAX_MEMORY_CONTEXT_CHARS,
    MAX_TASK_MESSAGE_CHARS,
    MAX_TOOL_ROUNDS,
    MAX_CONVERSATION_CONTEXT_CHARS,
    check_execution_limits,
)



router = APIRouter(
    prefix="/guardrails",
    tags=["Guardrails"],
)


class GuardrailCheckRequest(
    BaseModel
):
    tool_rounds: int = Field(
        ge=0
    )

    failed_test_runs: int = Field(
        ge=0
    )

@router.get("/status")
def get_guardrail_status():
    return {
        "max_task_message_chars":
            MAX_TASK_MESSAGE_CHARS,

        "max_memory_context_chars":
            MAX_MEMORY_CONTEXT_CHARS,

        "max_tool_rounds":
            MAX_TOOL_ROUNDS,

        "max_failed_test_runs":
            MAX_FAILED_TEST_RUNS,
        "max_conversation_context_chars":
        MAX_CONVERSATION_CONTEXT_CHARS,
    }

@router.post("/check")
def check_guardrails(
    request: GuardrailCheckRequest,
):
    decision = (
        check_execution_limits(
            tool_rounds=(
                request.tool_rounds
            ),
            failed_test_runs=(
                request.failed_test_runs
            ),
        )
    )

    return {
        "allowed":
            decision.allowed,

        "reason":
            decision.reason,
    }