from fastapi import (
    APIRouter,
    HTTPException,
)
from pydantic import (
    BaseModel,
)

from app.tools.desktop import (
    open_url,
    open_workspace_path,
    reveal_in_explorer,
)


router = APIRouter(
    prefix="/desktop",
    tags=["Desktop"],
)


class UrlRequest(
    BaseModel
):
    url: str


class WorkspacePathRequest(
    BaseModel
):
    path: str

@router.post("/open-url")
def desktop_open_url(
    request: UrlRequest,
):
    try:
        return open_url(
            request.url
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

@router.post("/open-path")
def desktop_open_path(
    request: WorkspacePathRequest,
):
    try:
        return (
            open_workspace_path(
                request.path
            )
        )

    except (
        ValueError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/reveal")
def desktop_reveal_path(
    request: WorkspacePathRequest,
):
    try:
        return reveal_in_explorer(
            request.path
        )

    except (
        ValueError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

