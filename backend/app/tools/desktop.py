import os
import subprocess
import webbrowser
from pathlib import Path

from app.workspace.manager import (
    workspace_manager,
)

ALLOWED_URL_SCHEMES = {
    "http://",
    "https://",
}

def _validate_url(
        url:str,
) -> str:
    cleaned_url = url.strip()

    if not cleaned_url:
        raise ValueError(
            "URL cannot be empty."
        )

    if not any(
        cleaned_url.lower().startswith(scheme)
        for scheme in ALLOWED_URL_SCHEMES
    ):
        raise ValueError(
            "Only HTTP and HTTPS URLs "
            "are allowed."
        )

    return cleaned_url

def open_url(url:str)->dict:

    validated_url = (
        _validate_url(
            url
        )
    )

    opened = webbrowser.open(
        validated_url,
        new=2,
    )

    return {
        "ok": bool(opened),
        "url": validated_url,
    }

def _resolve_workspace_path(
        relative_path:str,
)->Path:
    path = (
        workspace_manager.resolve_path(
            relative_path
        )
    )

    if not path.exists():
        raise ValueError(
            "Path does not exist."
        )

    return path

def open_workspace_path(
    relative_path: str,
) -> dict:

    path = (
        _resolve_workspace_path(
            relative_path
        )
    )

    os.startfile(
        str(path)
    )

    return {
        "ok": True,
        "path": (
            path
            .relative_to(
                workspace_manager
                .get_workspace()
            )
            .as_posix()
        ),
        "type": (
            "directory"
            if path.is_dir()
            else "file"
        ),
    }


def reveal_in_explorer(
    relative_path: str,
) -> dict:
    path = (
        _resolve_workspace_path(
            relative_path
        )
    )

    if path.is_dir():
        subprocess.Popen(
            [
                "explorer.exe",
                str(path),
            ],
            shell=False,
        )

    else:
        subprocess.Popen(
            [
                "explorer.exe",
                "/select,",
                str(path),
            ],
            shell=False,
        )

    return {
        "ok": True,
        "path": (
            path
            .relative_to(
                workspace_manager
                .get_workspace()
            )
            .as_posix()
        ),
    }