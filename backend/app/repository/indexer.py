from app.repository.chunker import (
    chunk_repository,
)
from app.repository.embeddings import (
    embed_pending_chunks,
    get_embedding_status,
)
from app.repository.scanner import (
    scan_repository,
)
from app.repository.storage import (
    remove_stale_chunks,
    store_chunks,
)


def index_repository() -> dict:

    files = scan_repository()

    chunks = chunk_repository(
        files
    )

    stored_count = store_chunks(
        chunks
    )

    stale_count = (
        remove_stale_chunks(
            chunks
        )
    )

    embedded_count = (
        embed_pending_chunks()
    )

    status = (
        get_embedding_status()
    )

    return {
        "files_scanned":
            len(files),

        "chunks_generated":
            len(chunks),

        "chunks_synced":
            stored_count,

        "stale_chunks_removed":
            stale_count,

        "embeddings_created":
            embedded_count,

        **status,
    }