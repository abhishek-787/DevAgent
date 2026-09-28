import os
from pathlib import Path

from app.workspace.manager import workspace_manager


MAX_READ_FILE_SIZE = 1_000_000

MAX_WRITE_FILE_SIZE = 1_000_000

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

PROTECTED_DIRECTORIES = {
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

def _relative_path(
    path: Path,
    workspace: Path,
) -> str:
    return path.relative_to(workspace).as_posix()

def _ensure_writable_path(
        target:Path,
        workspace:Path
)->None:
    try:
        relative = target.relative_to(
            workspace
        )
    except ValueError as exc:
        raise ValueError(
            "Access outside the active workspace "
            "is not allowed."
        ) from exc

    for part in relative.parts:
        if part in PROTECTED_DIRECTORIES:
            raise ValueError(
                f"Writing inside '{part}' "
                "is not allowed."
            )


def _iter_project_files(
    start_path: Path,
    workspace: Path,
):
    if start_path.is_file():
        resolved = start_path.resolve()

        try:
            resolved.relative_to(workspace)
        except ValueError:
            return

        yield resolved
        return

    for root, directories, files in os.walk(
        start_path
    ):
        directories[:] = [
            directory
            for directory in directories
            if directory
            not in IGNORED_DIRECTORIES
        ]

        root_path = Path(root)

        for filename in files:
            candidate = (
                root_path / filename
            ).resolve()

            try:
                candidate.relative_to(workspace)
            except ValueError:
                continue

            yield candidate


def list_directory(
    relative_path: str = ".",
) -> dict:
    workspace = (
        workspace_manager.get_workspace()
    )

    target = (
        workspace_manager.resolve_path(
            relative_path
        )
    )

    if not target.exists():
        raise ValueError(
            "Directory does not exist."
        )

    if not target.is_dir():
        raise ValueError(
            "Path must point to a directory."
        )

    entries = []

    sorted_entries = sorted(
        target.iterdir(),
        key=lambda item: (
            0 if item.is_dir() else 1,
            item.name.lower(),
        ),
    )

    for entry in sorted_entries:
        if (
            entry.is_dir()
            and entry.name
            in IGNORED_DIRECTORIES
        ):
            continue

        if entry.is_symlink():
            entry_type = "symlink"
            size = None

        elif entry.is_dir():
            entry_type = "directory"
            size = None

        else:
            entry_type = "file"

            try:
                size = entry.stat().st_size
            except OSError:
                size = None

        entries.append(
            {
                "name": entry.name,
                "path": _relative_path(
                    entry,
                    workspace,
                ),
                "type": entry_type,
                "size": size,
            }
        )

    return {
        "path": _relative_path(
            target,
            workspace,
        )
        if target != workspace
        else ".",
        "entries": entries,
    }


def read_file(
    relative_path: str,
) -> dict:
    workspace = (
        workspace_manager.get_workspace()
    )

    target = (
        workspace_manager.resolve_path(
            relative_path
        )
    )

    if not target.exists():
        raise ValueError(
            "File does not exist."
        )

    if not target.is_file():
        raise ValueError(
            "Path must point to a file."
        )

    size = target.stat().st_size

    if size > MAX_READ_FILE_SIZE:
        raise ValueError(
            "File is too large to read."
        )

    try:
        content = target.read_text(
            encoding="utf-8"
        )
    except UnicodeDecodeError as exc:
        raise ValueError(
            "File is not a UTF-8 text file."
        ) from exc

    return {
        "path": _relative_path(
            target,
            workspace,
        ),
        "size": size,
        "content": content,
    }


def search_files(
    query: str,
    max_results: int = 50,
) -> dict:
    workspace = (
        workspace_manager.get_workspace()
    )

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError(
            "Search query cannot be empty."
        )

    query_lower = cleaned_query.lower()

    results = []

    for candidate in _iter_project_files(
        workspace,
        workspace,
    ):
        relative = _relative_path(
            candidate,
            workspace,
        )

        if (
            query_lower
            in candidate.name.lower()
            or query_lower
            in relative.lower()
        ):
            results.append(
                {
                    "name": candidate.name,
                    "path": relative,
                }
            )

        if len(results) >= max_results:
            break

    return {
        "query": cleaned_query,
        "count": len(results),
        "results": results,
    }


def search_text(
    query: str,
    relative_path: str = ".",
    max_results: int = 50,
) -> dict:
    workspace = (
        workspace_manager.get_workspace()
    )

    start_path = (
        workspace_manager.resolve_path(
            relative_path
        )
    )

    if not start_path.exists():
        raise ValueError(
            "Search path does not exist."
        )

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError(
            "Search query cannot be empty."
        )

    query_lower = cleaned_query.lower()

    results = []

    for candidate in _iter_project_files(
        start_path,
        workspace,
    ):
        try:
            if (
                candidate.stat().st_size
                > MAX_READ_FILE_SIZE
            ):
                continue
        except OSError:
            continue

        try:
            with candidate.open(
                "r",
                encoding="utf-8",
            ) as file:
                for (
                    line_number,
                    line,
                ) in enumerate(
                    file,
                    start=1,
                ):
                    if (
                        query_lower
                        not in line.lower()
                    ):
                        continue

                    results.append(
                        {
                            "path":
                                _relative_path(
                                    candidate,
                                    workspace,
                                ),
                            "line_number":
                                line_number,
                            "line":
                                line.strip()[
                                    :300
                                ],
                        }
                    )

                    if (
                        len(results)
                        >= max_results
                    ):
                        return {
                            "query":
                                cleaned_query,
                            "count":
                                len(results),
                            "results":
                                results,
                        }

        except (
            UnicodeDecodeError,
            PermissionError,
            OSError,
        ):
            continue

    return {
        "query": cleaned_query,
        "count": len(results),
        "results": results,
    }


def create_directory(
    relative_path: str,
) -> dict:
    workspace = (
        workspace_manager.get_workspace()
        )
    target = (workspace_manager.resolve_path(
            relative_path
    ))

    _ensure_writable_path(
        target,
        workspace
    )

    if target == workspace:
        raise ValueError(
            "Cannot create the workspace "
            "directory itself."
        )
    if target.exists():
        raise ValueError(
            "Directory or file already exists."
        )

    target.mkdir(
        parents=True,
        exist_ok=False,
    )

    return {
        "path": _relative_path(
            target,
            workspace,
        ),
        "created": True,
        "type": "directory",
    }

def create_file(
    relative_path: str,
    content: str,
) -> dict:
    workspace = (
        workspace_manager.get_workspace()
    )
    target = (
        workspace_manager.resolve_path(
            relative_path
        )
    )
    _ensure_writable_path(
        target,
        workspace,
    )
    if target.exists():
        raise ValueError(
            "File or directory already exists."
        )
    parent = target.parent

    if not parent.exists():
        raise ValueError(
            "Parent directory does not exist."
        )

    if not parent.is_dir():
        raise ValueError(
            "Parent path must be a directory."
        )

    content_size = len(
        content.encode("utf-8")
    )

    if (
        content_size>MAX_WRITE_FILE_SIZE
    ):
        raise ValueError(
            "File content is too large."
        )

    target.write_text(
        content,
        encoding="utf-8"
    )

    return {
        "path": _relative_path(
            target,
            workspace,
        ),
        "created": True,
        "size": content_size,
    }

def edit_file(
    relative_path: str,
    old_text: str,
    new_text: str,
) -> dict:
    workspace = (
        workspace_manager.get_workspace()
    )
    target = (
        workspace_manager.resolve_path(
            relative_path
        )
    )
    _ensure_writable_path(
        target,
        workspace,
    )

    if not target.exists():
        raise ValueError(
            "File does not exist."
        )

    if not target.is_file():
        raise ValueError(
            "Path must point to a file."
        )

    if not old_text:
        raise ValueError(
            "old_text cannot be empty."
        )

    size = target.stat().st_size

    if size > MAX_WRITE_FILE_SIZE:
        raise ValueError(
            "File is too large to edit."
        )

    try:
        content = target.read_text(
            encoding="utf-8"
        )
    except UnicodeDecodeError as exc:
        raise ValueError(
            "File is not a UTF-8 text file."
        ) from exc

    occurrence_count = content.count(
        old_text
    )

    if occurrence_count == 0:
        raise ValueError(
            "The requested text was not "
            "found in the file."
        )

    if occurrence_count > 1:
        raise ValueError(
            "The requested text appears "
            "multiple times. Provide a more "
            "specific section to edit."
        )

    updated_content = content.replace(
        old_text,
        new_text,
        1,
    )

    updated_size = len(
        updated_content.encode("utf-8")
    )

    if (
        updated_size > MAX_WRITE_FILE_SIZE
    ):
        raise ValueError(
            "Updated file would be too large."
        )

    target.write_text(
        updated_content,
        encoding="utf-8",
    )

    return {
        "path": _relative_path(
            target,
            workspace,
        ),
        "edited": True,
        "replacements": 1,
        "old_size": size,
        "new_size": updated_size,
    }