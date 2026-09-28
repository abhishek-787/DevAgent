import hashlib

from sqlalchemy import (
    func,
    select,
)

from app.repository.database import (
    get_session,
)
from app.repository.models import (
    RepositoryChunk,
)
from app.repository.schemas import (
    CodeChunk,
)
from app.workspace.manager import (
    workspace_manager,
)


def _content_hash(
    content: str,
) -> str:
    return hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

def store_chunks(
    chunks: list[CodeChunk],
) -> int:
    if not chunks:
        return 0

    workspace = (
        workspace_manager
        .get_workspace()
        .as_posix()
    )

    stored_count = 0

    with get_session() as session:

        for chunk in chunks:
            chunk_hash = (
                _content_hash(
                    chunk.content
                )
            )

            statement = (
                select(
                    RepositoryChunk
                )
                .where(
                    RepositoryChunk
                    .workspace_path
                    == workspace,

                    RepositoryChunk
                    .file_path
                    == chunk.path,

                    RepositoryChunk
                    .start_line
                    == chunk.start_line,

                    RepositoryChunk
                    .end_line
                    == chunk.end_line,
                )
            )

            existing_chunk = (
                session.scalar(
                    statement
                )
            )

            if existing_chunk is None:
                database_chunk = (
                    RepositoryChunk(
                        workspace_path=(
                            workspace
                        ),
                        file_path=(
                            chunk.path
                        ),
                        language=(
                            chunk.language
                        ),
                        chunk_type=(
                            chunk.chunk_type
                        ),
                        symbol_name=(
                            chunk.symbol_name
                        ),
                        start_line=(
                            chunk.start_line
                        ),
                        end_line=(
                            chunk.end_line
                        ),
                        content=(
                            chunk.content
                        ),
                        content_hash=(
                            chunk_hash
                        ),
                        embedding=None,
                    )
                )

                session.add(
                    database_chunk
                )

            else:
                content_changed = (
                    existing_chunk
                    .content_hash
                    != chunk_hash
                )

                existing_chunk.language = (
                    chunk.language
                )

                existing_chunk.chunk_type = (
                    chunk.chunk_type
                )

                existing_chunk.symbol_name = (
                    chunk.symbol_name
                )

                existing_chunk.content = (
                    chunk.content
                )

                existing_chunk.content_hash = (
                    chunk_hash
                )

                if content_changed:
                    existing_chunk.embedding = (
                        None
                    )

            stored_count += 1

        session.commit()

    return stored_count

def get_chunk_count() -> int:
    workspace = (
        workspace_manager
        .get_workspace()
        .as_posix()
    )

    with get_session() as session:
        statement = (
            select(
                func.count()
            )
            .select_from(
                RepositoryChunk
            )
            .where(
                RepositoryChunk
                .workspace_path
                == workspace
            )
        )

        count = session.scalar(
            statement
        )

    return int(
        count or 0
    )


def get_stored_chunks(
    limit: int = 20,
) -> list[RepositoryChunk]:
    workspace = (
        workspace_manager
        .get_workspace()
        .as_posix()
    )

    with get_session() as session:
        statement = (
            select(
                RepositoryChunk
            )
            .where(
                RepositoryChunk
                .workspace_path
                == workspace
            )
            .order_by(
                RepositoryChunk
                .file_path,
                RepositoryChunk
                .start_line,
            )
            .limit(limit)
        )

        chunks = list(
            session.scalars(
                statement
            )
        )

    return chunks

def remove_stale_chunks(
    current_chunks: list[CodeChunk],
) -> int:

    workspace = (
        workspace_manager
        .get_workspace()
        .as_posix()
    )

    active_keys = {
        (
            chunk.path,
            chunk.start_line,
            chunk.end_line,
        )
        for chunk
        in current_chunks
    }

    deleted_count = 0

    with get_session() as session:

        statement = (
            select(
                RepositoryChunk
            )
            .where(
                RepositoryChunk
                .workspace_path
                == workspace
            )
        )

        stored_chunks = list(
            session.scalars(
                statement
            )
        )

        for stored_chunk in (
            stored_chunks
        ):
            key = (
                stored_chunk.file_path,
                stored_chunk.start_line,
                stored_chunk.end_line,
            )

            if key in active_keys:
                continue

            session.delete(
                stored_chunk
            )

            deleted_count += 1

        session.commit()

    return deleted_count