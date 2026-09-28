from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.tools.filesystem import (
    create_directory,
    create_file,
    edit_file,
    list_directory,
    read_file,
    search_files,
    search_text,
)

from pydantic import BaseModel

class CreateDirectoryRequest(
    BaseModel
):
    path: str


class CreateFileRequest(
    BaseModel
):
    path: str
    content: str


class EditFileRequest(
    BaseModel
):
    path: str
    old_text: str
    new_text: str

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


@router.get("/list")
def list_files_endpoint(
    path: str = ".",
):
    try:
        return list_directory(path)
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/read")
def read_file_endpoint(
    path: str,
):
    try:
        return read_file(path)
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/search-files")
def search_files_endpoint(
    query: str,
    max_results: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):
    try:
        return search_files(
            query=query,
            max_results=max_results,
        )
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/search-text")
def search_text_endpoint(
    query: str,
    path: str = ".",
    max_results: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
):
    try:
        return search_text(
            query=query,
            relative_path=path,
            max_results=max_results,
        )
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.post("/create-directory")
def create_directory_endpoint(
    request: CreateDirectoryRequest,
):
    try:
        return create_directory(
            request.path
        )
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/create")
def create_file_endpoint(
    request: CreateFileRequest,
):
    try:
        return create_file(
            relative_path=request.path,
            content=request.content,
        )
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.patch("/edit")
def edit_file_endpoint(
    request: EditFileRequest,
):
    try:
        return edit_file(
            relative_path=request.path,
            old_text=request.old_text,
            new_text=request.new_text,
        )
    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc