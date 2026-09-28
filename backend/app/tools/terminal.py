import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any

from app.workspace.manager import (
    workspace_manager,
)


DEFAULT_TIMEOUT_SECONDS = 30
MAX_TIMEOUT_SECONDS = 120

MAX_OUTPUT_CHARS = 50_000


ALLOWED_SYSTEM_EXECUTABLES = {
    "python",
    "python.exe",
    "py",
    "py.exe",
    "pytest",
    "pytest.exe",
    "git",
    "git.exe",
}


ALLOWED_WORKSPACE_EXECUTABLES = {
    ".venv/Scripts/python.exe",
    "venv/Scripts/python.exe",
    ".venv/bin/python",
    "venv/bin/python",
}


def _truncate_output(
    output: str,
) -> str:
    if len(output) <= MAX_OUTPUT_CHARS:
        return output

    return (
        output[:MAX_OUTPUT_CHARS]
        + "\n...[output truncated]..."
    )


def _normalize_output(
    output: Any,
) -> str:
    if output is None:
        return ""

    if isinstance(output, bytes):
        return output.decode(
            "utf-8",
            errors="replace",
        )

    return str(output)


def _resolve_executable(
    command: str,
    workspace: Path,
) -> str:
    cleaned_command = command.strip()

    if not cleaned_command:
        raise ValueError(
            "Command cannot be empty."
        )

    normalized_command = (
        cleaned_command
        .replace("\\", "/")
    )

    if (
        normalized_command
        in ALLOWED_WORKSPACE_EXECUTABLES
    ):
        executable = (
            workspace
            / normalized_command
        ).resolve()

        try:
            executable.relative_to(
                workspace
            )
        except ValueError as exc:
            raise ValueError(
                "Executable escapes the "
                "active workspace."
            ) from exc

        if not executable.exists():
            raise ValueError(
                "Workspace executable "
                "does not exist."
            )

        if not executable.is_file():
            raise ValueError(
                "Workspace executable "
                "must point to a file."
            )

        return str(executable)

    if (
        "/" in cleaned_command
        or "\\" in cleaned_command
    ):
        raise ValueError(
            "Executable path is not allowed."
        )

    executable_name = (
        cleaned_command.lower()
    )

    if (
        executable_name
        not in ALLOWED_SYSTEM_EXECUTABLES
    ):
        raise ValueError(
            f"Executable '{cleaned_command}' "
            "is not allowed."
        )

    executable = shutil.which(
        cleaned_command
    )

    if executable is None:
        raise ValueError(
            f"Executable '{cleaned_command}' "
            "was not found."
        )

    return executable


def run_command(
    command: str,
    args: list[str] | None = None,
    cwd: str = ".",
    timeout_seconds: int = (
        DEFAULT_TIMEOUT_SECONDS
    ),
) -> dict:
    if args is None:
        args = []

    if not (
        1
        <= timeout_seconds
        <= MAX_TIMEOUT_SECONDS
    ):
        raise ValueError(
            "Timeout must be between "
            "1 and 120 seconds."
        )

    if not all(
        isinstance(argument, str)
        for argument in args
    ):
        raise ValueError(
            "All command arguments "
            "must be strings."
        )

    if any(
        "\x00" in argument
        for argument in args
    ):
        raise ValueError(
            "Command arguments cannot "
            "contain null characters."
        )

    workspace = (
        workspace_manager
        .get_workspace()
    )

    working_directory = (
        workspace_manager
        .resolve_path(cwd)
    )

    if not (
        working_directory.exists()
        and working_directory.is_dir()
    ):
        raise ValueError(
            "Working directory must be "
            "an existing directory."
        )

    executable = _resolve_executable(
        command=command,
        workspace=workspace,
    )

    full_command = [
        executable,
        *args,
    ]

    creation_flags = 0

    if os.name == "nt":
        creation_flags = (
            subprocess.CREATE_NO_WINDOW
        )

    started_at = time.monotonic()

    try:
        completed = subprocess.run(
            full_command,
            cwd=str(
                working_directory
            ),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            shell=False,
            creationflags=creation_flags,
            check=False,
        )

        duration_ms = int(
            (
                time.monotonic()
                - started_at
            )
            * 1000
        )

        stdout = _truncate_output(
            completed.stdout
        )

        stderr = _truncate_output(
            completed.stderr
        )

        return {
            "ok":
                completed.returncode == 0,
            "command":
                cleaned_command_for_display(
                    command
                ),
            "args":
                args,
            "cwd":
                cwd,
            "exit_code":
                completed.returncode,
            "stdout":
                stdout,
            "stderr":
                stderr,
            "timed_out":
                False,
            "duration_ms":
                duration_ms,
        }

    except subprocess.TimeoutExpired as exc:
        duration_ms = int(
            (
                time.monotonic()
                - started_at
            )
            * 1000
        )

        stdout = _truncate_output(
            _normalize_output(
                exc.stdout
            )
        )

        stderr = _truncate_output(
            _normalize_output(
                exc.stderr
            )
        )

        return {
            "ok":
                False,
            "command":
                cleaned_command_for_display(
                    command
                ),
            "args":
                args,
            "cwd":
                cwd,
            "exit_code":
                None,
            "stdout":
                stdout,
            "stderr":
                stderr,
            "timed_out":
                True,
            "duration_ms":
                duration_ms,
        }


def cleaned_command_for_display(
    command: str,
) -> str:
    return command.strip()

def run_tests(
        test_path:str=".",
        timeout_seconds : int = 60
)-> dict:
    workspace =( workspace_manager.get_workspace())

    resolved_test_path = (
        workspace_manager.resolve_path(test_path)
    )

    if not resolved_test_path.exists():
        raise ValueError(
            "Test path does not exist."
        )

    relative_test_path = resolved_test_path.relative_to(workspace).as_posix()

    if relative_test_path == ".":
        pytest_target = "."
    else:
        pytest_target = (
            relative_test_path
        )

    python_candidates = [
        ".venv/Scripts/python.exe",
        "venv/Scripts/python.exe",
        ".venv/bin/python",
        "venv/bin/python",
    ]

    python_command = "python"

    for candidate in python_candidates:
        candidate_path = (
            workspace/candidate
        )

        if candidate_path.is_file():
            python_command = candidate
            break

    return run_command(
        command=python_command,
        args=[
            "-m",
            "pytest",
            "-q",
            "--color=no",
            pytest_target,
        ],
        cwd=".",
        timeout_seconds=timeout_seconds,
    )