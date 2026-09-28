import ast
from pathlib import Path

from app.repository.schemas import (
    CodeChunk,
)
from app.workspace.manager import (
    workspace_manager,
)

GENERIC_CHUNK_LINES = 80
GENERIC_CHUNK_OVERLAP = 10


LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".json": "json",
    ".md": "markdown",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
}

def _relative_path(
        file_path:Path,
)->str:
    workspace = (workspace_manager.get_workspace())

    return(
        file_path.relative_to(workspace).as_posix()
    )

def _chunk_python_file(
        file_path:Path,
        content:str,
)->list[CodeChunk]:
    try:
        tree = ast.parse(
            content
        )
    except SyntaxError:
        return []

    lines = content.splitlines()

    chunks: list[CodeChunk] = []

    relative_path = (
        _relative_path(
            file_path
        )
    )

    for node in tree.body:
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            start_line = (
                node.lineno
            )

            end_line = (
                node.end_lineno or node.lineno
            )

            chunk_content = "\n".join(
                lines[
                    start_line - 1:
                    end_line
                ]
            )

            if isinstance(
                node,
                ast.ClassDef,
            ):
                chunk_type = "class"
            else:
                chunk_type = (
                    "function"
                )

            chunks.append(
                CodeChunk(
                    path=relative_path,
                    language="python",
                    chunk_type=chunk_type,
                    symbol_name=node.name,
                    start_line=start_line,
                    end_line=end_line,
                    content=chunk_content,
                )
            )

    return chunks

    
def _chunk_generic_file(
        file_path:Path,
        content:str,
)->list[CodeChunk]:
    lines = content.splitlines()

    if not lines:
        return []

    relative_path = (
        _relative_path(
            file_path
        )
    )

    language = (
        LANGUAGE_BY_EXTENSION.get(
            file_path.suffix.lower(),
            "text",
        )
    )

    chunks: list[CodeChunk] = []

    start = 0

    while start < len(lines):
        end = min(
            start
            + GENERIC_CHUNK_LINES,
            len(lines),
        )

        chunk_content = "\n".join(
            lines[start:end]
        )
        chunks.append(
            CodeChunk(
                path=relative_path,
                language=language,
                chunk_type="text",
                symbol_name=None,
                start_line=start + 1,
                end_line=end,
                content=chunk_content,
            )
        )

        if end >= len(lines):
            break

        start = (
            end
            - GENERIC_CHUNK_OVERLAP
        )
    return chunks

def chunk_file(
    file_path: Path,
) -> list[CodeChunk]:
    try:
        content = file_path.read_text(
            encoding="utf-8"
        )
    except (
        UnicodeDecodeError,
        PermissionError,
        OSError,
    ):
        return []

    if not content.strip():
        return []

    if (
        file_path.suffix.lower()
        == ".py"
    ):
        python_chunks = (
            _chunk_python_file(
                file_path,
                content,
            )
        )

        if python_chunks:
            return python_chunks

    return _chunk_generic_file(
        file_path,
        content,
    )

def chunk_repository(
    files: list[Path],
) -> list[CodeChunk]:
    chunks: list[CodeChunk] = []

    for file_path in files:
        chunks.extend(
            chunk_file(
                file_path
            )
        )

    return chunks