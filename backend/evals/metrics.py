from statistics import (
    median,
)

from evals.models import (
    EvalResult,
)


def summarize_results(
    results: list[
        EvalResult
    ],
) -> dict:

    total = len(
        results
    )

    passed = sum(
        1
        for result
        in results
        if result.passed
    )

    failed = (
        total - passed
    )

    latencies = [
        result.latency_ms
        for result
        in results
    ]

    pass_rate = (
        passed / total
        if total
        else 0.0
    )

    median_latency = (
        median(
            latencies
        )
        if latencies
        else 0.0
    )

    return {
        "total_cases":
            total,

        "passed":
            passed,

        "failed":
            failed,

        "pass_rate":
            round(
                pass_rate,
                4,
            ),

        "median_latency_ms":
            round(
                median_latency,
                2,
            ),
    }