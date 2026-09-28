from sqlalchemy import (
    select,
)

from app.repository.database import (
    get_session,
)
from app.repository.embeddings import (
    embedding_model,
)
from app.repository.models import (
    RepositoryChunk,
)
from app.repository.schemas import (
    CodeSearchResult,
)
from app.workspace.manager import (
    workspace_manager,
)


DEFAULT_SEARCH_LIMIT = 5
MAX_SEARCH_LIMIT = 20

def semantic_code_search(
    query: str,
    limit: int = DEFAULT_SEARCH_LIMIT,
) -> list[CodeSearchResult]:

    query = query.strip()

    if not query:
        raise ValueError(
            "Search query cannot be empty."
        )

    if (
        limit < 1
        or limit > MAX_SEARCH_LIMIT
    ):
        raise ValueError(
            "Search limit must be "
            f"between 1 and "
            f"{MAX_SEARCH_LIMIT}."
        )

    workspace = workspace_manager.get_workspace().as_posix()

    query_embedding = (
        embedding_model.embed_query(
            query
        )
    )

    distance = (RepositoryChunk.embedding.cosine_distance(
            query_embedding
    )
    )

    statement = (
        select(
            RepositoryChunk,
            distance.label(
                "distance"
            ),
        ).where(
            RepositoryChunk.workspace_path == workspace,
            RepositoryChunk.embedding.is_not(None),
        ).order_by(
            distance
        ).limit(
            limit
        )
    )

    with get_session() as session:
        rows = (
            session.execute(
                statement
            ).all()
        )

    results: list[CodeSearchResult] = []

    for chunk, chunk_distance in rows:
        distance_value = float(
            chunk_distance
        )

        similarity = (
            1.0 - distance_value
        )

        results.append(
            CodeSearchResult(
                id=chunk.id,
                path=chunk.file_path,
                language=chunk.language,
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
                content=chunk.content,
                distance=(
                    distance_value
                ),
                similarity=(
                    similarity
                ),
            )
        )
    return results


