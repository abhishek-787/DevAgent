from dataclasses import (
    dataclass,
)


MAX_TASK_MESSAGE_CHARS = 20_000

MAX_MEMORY_CONTEXT_CHARS = 8_000

MAX_TOOL_ROUNDS = 10

MAX_FAILED_TEST_RUNS = 3

MAX_CONVERSATION_CONTEXT_CHARS = (
    12_000
)


@dataclass(
    frozen=True
)
class GuardrailDecision:
    allowed: bool
    reason: str | None = None

def validate_task_message(
    message: str,
) -> str:

    cleaned_message = (
        message.strip()
    )

    if not cleaned_message:
        raise ValueError(
            "Task message cannot be empty."
        )

    if (
        len(cleaned_message)
        > MAX_TASK_MESSAGE_CHARS
    ):
        raise ValueError(
            "Task message is too large. "
            f"Maximum allowed size is "
            f"{MAX_TASK_MESSAGE_CHARS} "
            "characters."
        )

    return cleaned_message


def limit_memory_context(
    memory_context: str,
) -> str:

    cleaned_context = (
        memory_context.strip()
    )

    if (
        len(cleaned_context)
        <= MAX_MEMORY_CONTEXT_CHARS
    ):
        return cleaned_context

    return (
        cleaned_context[
            :MAX_MEMORY_CONTEXT_CHARS
        ]
        + "\n\n"
        "[Additional workspace memory "
        "was omitted by the context "
        "guardrail.]"
    )


def check_execution_limits(
    tool_rounds: int,
    failed_test_runs: int,
) -> GuardrailDecision:

    if (
        failed_test_runs
        >= MAX_FAILED_TEST_RUNS
    ):
        return GuardrailDecision(
            allowed=False,
            reason=(
                "The test suite has "
                "failed too many times "
                f"during this task "
                f"({failed_test_runs}/"
                f"{MAX_FAILED_TEST_RUNS})."
            ),
        )

    if (
        tool_rounds
        >= MAX_TOOL_ROUNDS
    ):
        return GuardrailDecision(
            allowed=False,
            reason=(
                "The maximum number of "
                "tool execution rounds "
                "has been reached "
                f"({tool_rounds}/"
                f"{MAX_TOOL_ROUNDS})."
            ),
        )

    return GuardrailDecision(
        allowed=True
    )


def limit_conversation_context(
    conversation_context: str,
) -> str:

    cleaned_context = (
        conversation_context.strip()
    )

    if (
        len(cleaned_context)
        <= MAX_CONVERSATION_CONTEXT_CHARS
    ):
        return cleaned_context

    return (
        cleaned_context[
            -MAX_CONVERSATION_CONTEXT_CHARS:
        ]
        + "\n\n"
        "[Older conversation context "
        "was omitted by the context "
        "guardrail.]"
    )