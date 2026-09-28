from app.tools.terminal import (
    run_command,
)
from app.workspace.manager import (
    workspace_manager,
)

GIT_TIMEOUT_SECONDS = 15

def _run_git(
    args: list[str],
    timeout_seconds: int = GIT_TIMEOUT_SECONDS,
)-> dict:
    return run_command(
        command="git",
        args=args,
        cwd=".",
        timeout_seconds=timeout_seconds
    )

def _ensure_git_repository() -> None:
    result = _run_git(
        [
            "rev-parse",
            "--is-inside-work-tree",
        ],
        timeout_seconds=10,
    )

    if (
        not result["ok"]
        or result["stdout"]
        .strip()
        .lower()
        != "true"
    ):
        raise ValueError(
            "The active workspace is not "
            "a Git repository."
        )

def git_status() -> dict:
    _ensure_git_repository()

    result = _run_git(
        [
            "status",
            "--short",
        ]
    )

    if not result["ok"]:
        raise RuntimeError(
            result["stderr"].strip()
            or "git status failed."
        )

    status_text = (
        result["stdout"].rstrip()
    )

    return {
        "clean": not bool(
            status_text
        ),
        "status": status_text,
        "duration_ms":
            result["duration_ms"],
    }

def git_diff() -> dict:
    _ensure_git_repository()

    unstaged_result = _run_git(
        [
            "--no-pager",
            "diff",
            "--no-color",
        ]
    )

    if not unstaged_result["ok"]:
        raise RuntimeError(
            unstaged_result[
                "stderr"
            ].strip()
            or "git diff failed."
        )

    staged_result = _run_git(
        [
            "--no-pager",
            "diff",
            "--cached",
            "--no-color",
        ]
    )

    if not staged_result["ok"]:
        raise RuntimeError(
            staged_result[
                "stderr"
            ].strip()
            or "git staged diff failed."
        )

    unstaged_diff = (
        unstaged_result[
            "stdout"
        ].rstrip()
    )

    staged_diff = (
        staged_result[
            "stdout"
        ].rstrip()
    )

    return {
        "has_changes": bool(
            unstaged_diff
            or staged_diff
        ),
        "unstaged": unstaged_diff,
        "staged": staged_diff,
    }


def git_diff_file(
    path: str,
) -> dict:
    _ensure_git_repository()

    workspace = (
        workspace_manager
        .get_workspace()
    )

    resolved_path = (
        workspace_manager
        .resolve_path(path)
    )

    relative_path = (
        resolved_path
        .relative_to(workspace)
        .as_posix()
    )

    if relative_path == ".":
        raise ValueError(
            "Path must point to a file "
            "inside the workspace."
        )

    unstaged_result = _run_git(
        [
            "--no-pager",
            "diff",
            "--no-color",
            "--",
            relative_path,
        ]
    )

    if not unstaged_result["ok"]:
        raise RuntimeError(
            unstaged_result[
                "stderr"
            ].strip()
            or "git file diff failed."
        )

    staged_result = _run_git(
        [
            "--no-pager",
            "diff",
            "--cached",
            "--no-color",
            "--",
            relative_path,
        ]
    )

    if not staged_result["ok"]:
        raise RuntimeError(
            staged_result[
                "stderr"
            ].strip()
            or "git staged file diff failed."
        )

    unstaged_diff = (
        unstaged_result[
            "stdout"
        ].rstrip()
    )

    staged_diff = (
        staged_result[
            "stdout"
        ].rstrip()
    )

    return {
        "path": relative_path,
        "has_changes": bool(
            unstaged_diff
            or staged_diff
        ),
        "unstaged": unstaged_diff,
        "staged": staged_diff,
    }