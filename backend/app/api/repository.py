from fastapi import (
    APIRouter,
    HTTPException,
)

from app.repository.chunker import (
    chunk_repository,
)
from app.repository.scanner import (
    scan_repository,
)

from app.repository.database import (
    initialize_database,
)

from app.repository.storage import (
    get_chunk_count,
    get_stored_chunks,
    store_chunks,
)

from app.repository.embeddings import (
    get_embedding_status,
)
from app.repository.indexer import (
    index_repository,
)

from pydantic import (
    BaseModel,
    Field,
)

from app.repository.search import (
    semantic_code_search,
)

router = APIRouter(
    prefix="/repository",
    tags=["Repository"],
)

class SemanticSearchRequest(
    BaseModel
):
    query: str

    limit: int = Field(
        default=5,
        ge=1,
        le=20,
    )


@router.get("/scan")
def scan_project_repository():
    try:
        files = scan_repository()

        return {
            "count": len(files),
            "files": [
                str(
                    file_path.name
                )
                for file_path
                in files
            ],
        }

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/chunks")
def get_repository_chunks():
    try:
        files = scan_repository()

        chunks = chunk_repository(
            files
        )

        return {
            "file_count":
                len(files),
            "chunk_count":
                len(chunks),
            "chunks": [
                {
                    "path":
                        chunk.path,
                    "language":
                        chunk.language,
                    "chunk_type":
                        chunk.chunk_type,
                    "symbol_name":
                        chunk.symbol_name,
                    "start_line":
                        chunk.start_line,
                    "end_line":
                        chunk.end_line,
                    "preview":
                        chunk.content[:300],
                }
                for chunk
                in chunks
            ],
        }

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/initialize")
def initialize_repository_database():
    try:
        initialize_database()

        return {
            "initialized": True
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

@router.post("/store")
def store_repository_chunks():
    try:
        files = scan_repository()

        chunks = chunk_repository(
            files
        )

        stored_count = store_chunks(
            chunks
        )

        database_count = (
            get_chunk_count()
        )

        return {
            "files_scanned":
                len(files),

            "chunks_generated":
                len(chunks),

            "chunks_stored":
                stored_count,

            "database_chunk_count":
                database_count,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get("/stored")
def get_repository_storage():
    try:
        chunks = (
            get_stored_chunks()
        )

        return {
            "count": len(chunks),
            "chunks": [
                {
                    "id":
                        chunk.id,

                    "file_path":
                        chunk.file_path,

                    "language":
                        chunk.language,

                    "chunk_type":
                        chunk.chunk_type,

                    "symbol_name":
                        chunk.symbol_name,

                    "start_line":
                        chunk.start_line,

                    "end_line":
                        chunk.end_line,

                    "embedding_ready":
                        (
                            chunk.embedding
                            is not None
                        ),
                }
                for chunk in chunks
            ],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

@router.post("/index")
def index_project_repository():
    try:
        return index_repository()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

@router.get("/index-status")
def repository_index_status():
    try:
        return get_embedding_status()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

@router.post("/search")
def search_repository(
    request: SemanticSearchRequest,
):
    try:
        results = (
            semantic_code_search(
                query=request.query,
                limit=request.limit,
            )
        )

        return {
            "query":
                request.query,

            "count":
                len(results),

            "results": [
                {
                    "id":
                        result.id,

                    "path":
                        result.path,

                    "language":
                        result.language,

                    "chunk_type":
                        result.chunk_type,

                    "symbol_name":
                        result.symbol_name,

                    "start_line":
                        result.start_line,

                    "end_line":
                        result.end_line,

                    "similarity":
                        round(
                            result.similarity,
                            4,
                        ),

                    "distance":
                        round(
                            result.distance,
                            4,
                        ),

                    "content":
                        result.content,
                }
                for result
                in results
            ],
        }

    except (
        ValueError,
        RuntimeError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

