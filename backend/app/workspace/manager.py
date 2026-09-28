from pathlib import Path


class WorkspaceManager:
    def __init__(self):
        self._workspace: Path | None = None

    def set_workspace(self, path: str) -> Path:
        workspace = Path(path).expanduser().resolve()

        if not workspace.exists():
            raise ValueError("Workspace path does not exist.")

        if not workspace.is_dir():
            raise ValueError("Workspace path must be a directory.")

        self._workspace = workspace

        return workspace

    def get_workspace(self) -> Path:
        if self._workspace is None:
            raise RuntimeError("No workspace is currently selected.")

        return self._workspace

    def get_workspace_info(self) -> dict:
        if self._workspace is None:
            return {
                "active": False,
                "name": None,
                "path": None,
            }

        return {
            "active": True,
            "name": self._workspace.name,
            "path": str(self._workspace),
        }

    def resolve_path(self, relative_path: str) -> Path:
        workspace = self.get_workspace()

        target = (workspace / relative_path).resolve()

        try:
            target.relative_to(workspace)
        except ValueError as exc:
            raise ValueError(
                "Access outside the active workspace is not allowed."
            ) from exc

        return target


workspace_manager = WorkspaceManager()