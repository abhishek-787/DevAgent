from fastapi import APIRouter, HTTPException

from app.workspace.manager import workspace_manager
from app.workspace.schemas import (
    OpenWorkspaceRequest,
    WorkspaceInfo,
)

from app.tools.editor import (
    open_in_vscode,
)

router = APIRouter(
    prefix="/workspace",
    tags=["Workspace"],
)

@router.post("/open",response_model=WorkspaceInfo)
def open_workspace(request:OpenWorkspaceRequest):
    try:
        workspace_manager.set_workspace(
            request.path
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    return workspace_manager.get_workspace_info()

@router.get(
    "/current",
    response_model=WorkspaceInfo,
)
def current_workspace():
    return workspace_manager.get_workspace_info()

@router.post("/open-vscode")
def open_workspace_in_vscode():
    try:
        return open_in_vscode()

    except (
        ValueError,
        RuntimeError,
        OSError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc