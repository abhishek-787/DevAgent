from pydantic import BaseModel

class OpenWorkspaceRequest(BaseModel):
    path: str

class WorkspaceInfo(BaseModel):
    active:bool
    name:str | None = None
    path:str | None = None

