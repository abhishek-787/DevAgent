from fastapi import (
    APIRouter,
    HTTPException,
)
from pydantic import (
    BaseModel,
    Field,
)

from app.tools.terminal import (
    run_command,
)


router = APIRouter(
    prefix="/terminal",
    tags=["Terminal"],
)


class RunCommandRequest(
    BaseModel
):
    command: str

    args: list[str] = Field(
        default_factory=list
    )

    cwd: str = "."

    timeout_seconds: int = Field(
        default=30,
        ge=1,
        le=120,
    )


@router.post("/run")
def run_terminal_command(
    request: RunCommandRequest,
):
    try:
        return run_command(
            command=request.command,
            args=request.args,
            cwd=request.cwd,
            timeout_seconds=(
                request.timeout_seconds
            ),
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

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Terminal command failed."
            ),
        ) from exc