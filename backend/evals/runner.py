import argparse
import json
import os
import time
from dataclasses import (
    asdict,
)
from datetime import (
    UTC,
    datetime,
)
from pathlib import (
    Path,
)

import httpx

from evals.catalog import (
    AUTOMATED_CASES,
)

from evals.metrics import (
    summarize_results,
)

from evals.models import (
    EvalCase,
    EvalCheck,
    EvalResult,
)


DEFAULT_BASE_URL = (
    "http://127.0.0.1:8000"
)

DEFAULT_RESULTS_DIR = (
    Path(__file__).parent
    / "results"
)

def open_workspace(
    client: httpx.Client,
    base_url: str,
    workspace_path: str,
) -> None:

    response = client.post(
        f"{base_url}/workspace/open",
        json={
            "path":
                workspace_path,
        },
    )

    response.raise_for_status()

    data = response.json()

    if not data.get(
        "workspace"
    ) and not data.get(
        "path"
    ):
        print(
            "Workspace opened."
        )

def evaluate_case(
    client: httpx.Client,
    base_url: str,
    case: EvalCase,
) -> EvalResult:

    started = (
        time.perf_counter()
    )

    try:
        response = client.post(
            f"{base_url}/agent/task",
            json={
                "message":
                    case.prompt,
            },
        )

        latency_ms = (
            time.perf_counter()
            - started
        ) * 1000

        response.raise_for_status()

        payload = (
            response.json()
        )

    except Exception as exc:
        latency_ms = (
            time.perf_counter()
            - started
        ) * 1000

        return EvalResult(
            case_id=case.id,
            category=(
                case.category
            ),
            title=case.title,
            passed=False,
            latency_ms=(
                latency_ms
            ),
            checks=[
                EvalCheck(
                    name=(
                        "request_completed"
                    ),
                    passed=False,
                    details=(
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
                )
            ],
            response={},
        )


    checks: list[
        EvalCheck
    ] = []


    actual_status = (
        payload.get(
            "status"
        )
    )

    checks.append(
        EvalCheck(
            name="status",
            passed=(
                actual_status
                == case.expected_status
            ),
            details=(
                f"expected="
                f"{case.expected_status}, "
                f"actual="
                f"{actual_status}"
            ),
        )
    )


    tools_used = set(
        payload.get(
            "tools_used",
            []
        )
    )


    for tool in (
        case.required_tools
    ):
        checks.append(
            EvalCheck(
                name=(
                    f"required_tool:"
                    f"{tool}"
                ),
                passed=(
                    tool
                    in tools_used
                ),
                details=(
                    f"tools_used="
                    f"{sorted(tools_used)}"
                ),
            )
        )


    for tool in (
        case.forbidden_tools
    ):
        checks.append(
            EvalCheck(
                name=(
                    f"forbidden_tool:"
                    f"{tool}"
                ),
                passed=(
                    tool
                    not in tools_used
                ),
                details=(
                    f"tools_used="
                    f"{sorted(tools_used)}"
                ),
            )
        )


    answer = str(
        payload.get(
            "answer",
            ""
        )
    )

    normalized_answer = (
        answer.lower()
    )


    for expected_text in (
        case.answer_contains
    ):
        checks.append(
            EvalCheck(
                name=(
                    "answer_contains:"
                    f"{expected_text}"
                ),
                passed=(
                    expected_text.lower()
                    in normalized_answer
                ),
            )
        )


    failed_test_runs = int(
        payload.get(
            "failed_test_runs",
            0,
        )
    )

    checks.append(
        EvalCheck(
            name=(
                "failed_test_runs"
            ),
            passed=(
                failed_test_runs
                <= case
                .max_failed_test_runs
            ),
            details=(
                f"actual="
                f"{failed_test_runs}, "
                f"maximum="
                f"{case.max_failed_test_runs}"
            ),
        )
    )


    latency_seconds = (
        latency_ms / 1000
    )

    checks.append(
        EvalCheck(
            name="latency",
            passed=(
                latency_seconds
                <= case
                .max_latency_seconds
            ),
            details=(
                f"{latency_seconds:.2f}s "
                f"<= "
                f"{case.max_latency_seconds:.2f}s"
            ),
        )
    )


    passed = all(
        check.passed
        for check
        in checks
    )


    return EvalResult(
        case_id=case.id,
        category=(
            case.category
        ),
        title=case.title,
        passed=passed,
        latency_ms=(
            latency_ms
        ),
        checks=checks,
        response=payload,
    )



def save_results(
    results: list[
        EvalResult
    ],
) -> Path:

    DEFAULT_RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = (
        datetime.now(
            UTC
        )
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    output_path = (
        DEFAULT_RESULTS_DIR
        / f"eval_{timestamp}.json"
    )

    document = {
        "created_at":
            datetime.now(
                UTC
            )
            .isoformat(),

        "summary":
            summarize_results(
                results
            ),

        "results": [
            asdict(
                result
            )
            for result
            in results
        ],
    }

    output_path.write_text(
        json.dumps(
            document,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return output_path

def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Run DevAgent "
            "evaluation cases."
        )
    )

    parser.add_argument(
        "workspace",
        help=(
            "Path to the evaluation "
            "workspace."
        ),
    )

    parser.add_argument(
        "--case",
        dest="case_id",
        default=None,
        help=(
            "Run one case instead "
            "of the full automated "
            "suite."
        ),
    )

    parser.add_argument(
        "--base-url",
        default=(
            os.getenv(
                "DEVAGENT_BASE_URL",
                DEFAULT_BASE_URL,
            )
        ),
    )


    args = (
        parser.parse_args()
    )


    cases = list(
        AUTOMATED_CASES
    )


    if args.case_id:
        cases = [
            case
            for case
            in cases
            if case.id
            == args.case_id
        ]

        if not cases:
            raise SystemExit(
                "Unknown evaluation "
                f"case: {args.case_id}"
            )


    timeout = httpx.Timeout(
        connect=10.0,
        read=300.0,
        write=30.0,
        pool=10.0,
    )


    with httpx.Client(
        timeout=timeout
    ) as client:

        open_workspace(
            client=client,
            base_url=(
                args.base_url
            ),
            workspace_path=(
                args.workspace
            ),
        )


        results: list[
            EvalResult
        ] = []


        for index, case in enumerate(
            cases,
            start=1,
        ):
            print()
            print(
                f"[{index}/"
                f"{len(cases)}] "
                f"{case.id}"
            )

            result = (
                evaluate_case(
                    client=client,
                    base_url=(
                        args.base_url
                    ),
                    case=case,
                )
            )

            results.append(
                result
            )

            status = (
                "PASS"
                if result.passed
                else "FAIL"
            )

            print(
                f"  {status} "
                f"({result.latency_ms/ 1000:.2f}s)"
            )

            for check in (
                result.checks
            ):
                symbol = (
                    "✓"
                    if check.passed
                    else "✗"
                )

                print(
                    f"    {symbol} "
                    f"{check.name}"
                )


    summary = (
        summarize_results(
            results
        )
    )


    print()
    print(
        "Evaluation summary"
    )

    print(
        f"Passed: "
        f"{summary['passed']}/"
        f"{summary['total_cases']}"
    )

    print(
        f"Pass rate: "
        f"{summary['pass_rate'] * 100:.1f}%"
    )

    print(
        "Median latency: "
        f"{summary['median_latency_ms']/ 1000:.2f}s"
    )


    output_path = (
        save_results(
            results
        )
    )

    print(
        f"Saved: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()