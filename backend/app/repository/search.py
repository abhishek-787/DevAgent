import math

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


def _cosine_similarity(
    first: list[float],
    second: list[float],
) -> float:

    if not first or not second:
        return 0.0

    if len(first) != len(second):
        return 0.0

    dot_product = sum(
        a * b
        for a, b
        in zip(
            first,
            second,
        )
    )

    first_norm = math.sqrt(
        sum(
            value * value
            for value
            in first
        )
    )

    second_norm = math.sqrt(
        sum(
            value * value
            for value
            in second
        )
    )

    if (
        first_norm == 0.0
        or second_norm == 0.0
    ):
        return 0.0

    similarity = (
        dot_product
        / (
            first_norm
            * second_norm
        )
    )

    # Floating-point operations can
    # occasionally produce something
    # slightly above 1 or below -1.
    return max(
        -1.0,
        min(
            1.0,
            similarity,
        ),
    )


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

    workspace = (
        workspace_manager
        .get_workspace()
        .as_posix()
    )

    query_embedding = (
        embedding_model
        .embed_query(
            query
        )
    )

    statement = (
        select(
            RepositoryChunk
        )
        .where(
            RepositoryChunk.workspace_path
            == workspace,

            RepositoryChunk.embedding
            .is_not(None),
        )
    )

    with get_session() as session:
        chunks = list(
            session.scalars(
                statement
            )
        )

    scored_chunks: list[
        tuple[
            RepositoryChunk,
            float,
        ]
    ] = []

    for chunk in chunks:

        vector = chunk.embedding

        if not vector:
            continue

        similarity = (
            _cosine_similarity(
                query_embedding,
                vector,
            )
        )

        scored_chunks.append(
            (
                chunk,
                similarity,
            )
        )

    scored_chunks.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    top_chunks = (
        scored_chunks[:limit]
    )

    results: list[
        CodeSearchResult
    ] = []

    for (
        chunk,
        similarity,
    ) in top_chunks:

        distance = (
            1.0
            - similarity
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
                distance=distance,
                similarity=similarity,
            )
        )

    return results