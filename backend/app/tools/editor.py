import os
import shutil
import subprocess
from pathlib import Path

from app.workspace.manager import workspace_manager


def _find_vscode() -> str:
    possible_paths: list[Path] = []

    local_app_data = os.getenv(
        "LOCALAPPDATA"
    )

    program_files = os.getenv(
        "PROGRAMFILES"
    )

    program_files_x86 = os.getenv(
        "PROGRAMFILES(X86)"
    )

    if local_app_data:
        possible_paths.append(
            Path(local_app_data)
            / "Programs"
            / "Microsoft VS Code"
            / "Code.exe"
        )

    if program_files:
        possible_paths.append(
            Path(program_files)
            / "Microsoft VS Code"
            / "Code.exe"
        )

    if program_files_x86:
        possible_paths.append(
            Path(program_files_x86)
            / "Microsoft VS Code"
            / "Code.exe"
        )

    # Prefer the real Windows executable.
    for path in possible_paths:
        if path.exists():
            return str(path)

    # Fallback to the VS Code CLI.
    command = shutil.which("code")

    if command:
        return command

    raise ValueError(
        "VS Code was not found. "
        "Make sure Visual Studio Code is installed."
    )


def open_in_vscode() -> dict:
    workspace = (
        workspace_manager.get_workspace()
    )

    vscode = _find_vscode()

    try:
        if vscode.lower().endswith(
            (".cmd", ".bat")
        ):
            command = (
                f'"{vscode}" '
                f'--new-window '
                f'"{workspace}"'
            )

            subprocess.Popen(
                command,
                cwd=str(workspace),
                shell=True,
            )

            launch_method = "VS Code CLI"

        else:
            subprocess.Popen(
                [
                    vscode,
                    "--new-window",
                    str(workspace),
                ],
                cwd=str(workspace),
            )

            launch_method = "Code.exe"

    except OSError as exc:
        raise ValueError(
            "Failed to open VS Code."
        ) from exc

    return {
        "opened": True,
        "editor": "Visual Studio Code",
        "workspace": str(workspace),
        "executable": vscode,
        "launch_method": launch_method,
    }