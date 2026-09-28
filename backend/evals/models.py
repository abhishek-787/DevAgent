from dataclasses import (
    dataclass,
    field,
)


@dataclass(
    frozen=True
)
class EvalCase:
    id: str

    category: str

    title: str

    prompt: str

    expected_status: str = (
        "completed"
    )

    required_tools: tuple[
        str,
        ...
    ] = ()

    forbidden_tools: tuple[
        str,
        ...
    ] = ()

    answer_contains: tuple[
        str,
        ...
    ] = ()

    max_failed_test_runs: int = 0

    max_latency_seconds: float = (
        180.0
    )


@dataclass
class EvalCheck:
    name: str
    passed: bool
    details: str = ""


@dataclass
class EvalResult:
    case_id: str
    category: str
    title: str

    passed: bool

    latency_ms: float

    checks: list[
        EvalCheck
    ] = field(
        default_factory=list
    )

    response: dict = field(
        default_factory=dict
    )