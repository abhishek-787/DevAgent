import os
from pathlib import Path

from app.workspace.manager import (
    workspace_manager,
)


IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    "coverage",
}


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".md",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".yaml",
    ".yml",
}


def scan_repository() -> list[Path]:
    workspace = (
        workspace_manager
        .get_workspace()
    )

    files: list[Path] = []

    for root, directories, filenames in os.walk(
        workspace
    ):
        directories[:] = [
            directory
            for directory in directories
            if directory
            not in IGNORED_DIRECTORIES
        ]

        root_path = Path(root)

        for filename in filenames:
            file_path = (
                root_path / filename
            ).resolve()

            try:
                file_path.relative_to(
                    workspace
                )
            except ValueError:
                continue

            if (
                file_path.suffix.lower()
                not in SUPPORTED_EXTENSIONS
            ):
                continue

            if not file_path.is_file():
                continue

            files.append(
                file_path
            )

    return sorted(files)