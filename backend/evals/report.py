import json
from datetime import (
    UTC,
    datetime,
)
from pathlib import (
    Path,
)


EVAL_DIR = Path(
    __file__
).parent

RESULTS_DIR = (
    EVAL_DIR
    / "results"
)

MANUAL_RESULTS_PATH = (
    EVAL_DIR
    / "manual_results.json"
)

REPORT_PATH = (
    EVAL_DIR
    / "final_report.md"
)


def get_latest_automated_result(
) -> Path:

    result_files = sorted(
        RESULTS_DIR.glob(
            "eval_*.json"
        )
    )

    if not result_files:
        raise RuntimeError(
            "No automated "
            "evaluation results found."
        )

    return result_files[-1]


def load_json(
    path: Path,
) -> dict:

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def manual_summary(
    cases: list[dict],
) -> dict:

    counts = {
        "PASS": 0,
        "FAIL": 0,
        "BLOCKED": 0,
        "NOT_RUN": 0,
    }

    for case in cases:
        status = (
            case.get(
                "status",
                "NOT_RUN",
            )
            .upper()
        )

        if status not in counts:
            status = "NOT_RUN"

        counts[status] += 1

    executed = (
        counts["PASS"]
        + counts["FAIL"]
    )

    pass_rate = (
        counts["PASS"]
        / executed
        if executed
        else 0.0
    )

    return {
        **counts,
        "executed":
            executed,

        "pass_rate":
            pass_rate,
    }


def build_report() -> str:

    automated_path = (
        get_latest_automated_result()
    )

    automated = load_json(
        automated_path
    )

    manual = load_json(
        MANUAL_RESULTS_PATH
    )

    automated_summary = (
        automated["summary"]
    )

    manual_cases = (
        manual["cases"]
    )

    manual_stats = (
        manual_summary(
            manual_cases
        )
    )


    lines: list[str] = [
        "# DevAgent Evaluation Report",
        "",
        (
            "Generated: "
            + datetime.now(
                UTC
            ).isoformat()
        ),
        "",
        "## Automated Evaluation",
        "",
        (
            f"- Cases: "
            f"{automated_summary['total_cases']}"
        ),
        (
            f"- Passed: "
            f"{automated_summary['passed']}"
        ),
        (
            f"- Failed: "
            f"{automated_summary['failed']}"
        ),
        (
            f"- Pass rate: "
            f"{automated_summary['pass_rate'] * 100:.1f}%"
        ),
        (
            f"- Median latency: "
            f"{automated_summary['median_latency_ms'] / 1000:.2f}s"
        ),
        "",
        "### Automated Cases",
        "",
    ]


    for result in automated[
        "results"
    ]:

        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        lines.extend(
            [
                (
                    f"#### {result['case_id']} "
                    f"— {status}"
                ),
                "",
                result["title"],
                "",
                (
                    "Latency: "
                    f"{result['latency_ms'] / 1000:.2f}s"
                ),
                "",
            ]
        )

        for check in result[
            "checks"
        ]:

            symbol = (
                "✓"
                if check["passed"]
                else "✗"
            )

            details = (
                check.get(
                    "details"
                )
                or ""
            )

            line = (
                f"- {symbol} "
                f"{check['name']}"
            )

            if details:
                line += (
                    f" — {details}"
                )

            lines.append(
                line
            )

        lines.append("")


    lines.extend(
        [
            "## Manual Evaluation",
            "",
            (
                f"- Passed: "
                f"{manual_stats['PASS']}"
            ),
            (
                f"- Failed: "
                f"{manual_stats['FAIL']}"
            ),
            (
                f"- Blocked: "
                f"{manual_stats['BLOCKED']}"
            ),
            (
                f"- Not run: "
                f"{manual_stats['NOT_RUN']}"
            ),
            (
                f"- Executed pass rate: "
                f"{manual_stats['pass_rate'] * 100:.1f}%"
            ),
            "",
            "### Manual Cases",
            "",
        ]
    )


    for case in manual_cases:

        lines.extend(
            [
                (
                    f"#### {case['id']} "
                    f"— {case['status']}"
                ),
                "",
                case["title"],
                "",
                (
                    case.get(
                        "evidence"
                    )
                    or "No evidence recorded."
                ),
                "",
            ]
        )


    lines.extend(
        [
            "## Evaluation Scope",
            "",
            (
                "Automated evaluation covers "
                "repository understanding, "
                "retrieval behavior, tool "
                "selection, test execution, "
                "tool avoidance, and latency."
            ),
            "",
            (
                "Manual evaluation covers "
                "human approval, rejection, "
                "autonomous debugging, restart "
                "recovery, conversation "
                "persistence, guardrails, "
                "vision, desktop actions, "
                "voice input, and Git diff UI."
            ),
            "",
            (
                "Results represent the tested "
                "DevAgent configuration and "
                "evaluation workspace. They "
                "should not be interpreted as "
                "guarantees for arbitrary "
                "repositories or tasks."
            ),
        ]
    )


    return "\n".join(
        lines
    )


def main() -> None:

    report = (
        build_report()
    )

    REPORT_PATH.write_text(
        report,
        encoding="utf-8",
    )

    print(
        f"Report saved to: "
        f"{REPORT_PATH}"
    )


if __name__ == "__main__":
    main()