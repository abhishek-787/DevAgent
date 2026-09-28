from langchain_ollama import (
    OllamaEmbeddings,
)
from sqlalchemy import (
    func,
    select,
)

from app.core.config import (
    settings,
)
from app.repository.database import (
    get_session,
)
from app.repository.models import (
    RepositoryChunk,
)
from app.workspace.manager import (
    workspace_manager,
)


EMBEDDING_BATCH_SIZE = 16


embedding_model = OllamaEmbeddings(
    model=settings.embedding_model,
    base_url=settings.ollama_base_url,
)

def _build_embedding_text(
        chunk:RepositoryChunk,
)->str:
    symbol_name = (
        chunk.symbol_name
        or "None"
    )

    return (
        f"File: {chunk.file_path}\n"
        f"Language: {chunk.language}\n"
        f"Type: {chunk.chunk_type}\n"
        f"Symbol: {symbol_name}\n\n"
        f"{chunk.content}"
    )

def embed_pending_chunks(
    batch_size: int
    = EMBEDDING_BATCH_SIZE,
) -> int:

    embedded_count = 0

    workspace = (
    workspace_manager
    .get_workspace()
    .as_posix()
)

    while True:
        with get_session() as session:
            statement = (
                select(
                    RepositoryChunk
                ).where(
                RepositoryChunk
                .workspace_path
                == workspace,

                RepositoryChunk.embedding.is_(None),
                ).order_by(
                    RepositoryChunk.id
                )
                .limit(
                    batch_size
                )
            )

            pending_chunks = list(
                session.scalars(
                    statement
                )
            )

            if not pending_chunks:
                break

            pending_data = [
                (
                    chunk.id,
                    _build_embedding_text(
                        chunk
                    ),
                )
                for chunk
                in pending_chunks
            ]

        texts = [
            text
            for _, text
            in pending_data
        ]

        vectors = (
            embedding_model
            .embed_documents(
                texts
            )
        )

        if (
            len(vectors)
            != len(pending_data)
        ):
            raise RuntimeError(
                "Embedding count "
                "does not match "
                "chunk count."
            )

        with get_session() as session:
            for (
                chunk_id,
                _
            ), vector in zip(
                pending_data,
                vectors,
            ):
                chunk = session.get(
                    RepositoryChunk,
                    chunk_id,
                )

                if chunk is None:
                    continue

                if chunk.embedding is not None:
                    continue

                chunk.embedding = (
                    vector
                )

                embedded_count += 1

            session.commit()

    return embedded_count


def get_embedding_status() -> dict:
    workspace = (
        workspace_manager
        .get_workspace()
        .as_posix()
    )

    with get_session() as session:

        total_statement = (
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

        embedded_statement = (
            select(
                func.count()
            )
            .select_from(
                RepositoryChunk
            )
            .where(
                RepositoryChunk
                .workspace_path
                == workspace,
                RepositoryChunk
                .embedding
                .is_not(None),
            )
        )

        total = (
            session.scalar(
                total_statement
            )
            or 0
        )

        embedded = (
            session.scalar(
                embedded_statement
            )
            or 0
        )

    return {
        "total_chunks":
            int(total),

        "embedded_chunks":
            int(embedded),

        "pending_chunks":
            int(
                total
                - embedded
            ),
    }