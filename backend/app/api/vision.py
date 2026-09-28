import httpx

from fastapi import (
    APIRouter,
    HTTPException,
    Response,
)
from pydantic import (
    BaseModel,
    Field,
)

from app.vision.analyzer import (
    analyze_current_screen,
)
from app.vision.screen import (
    capture_primary_screen,
)


router = APIRouter(
    prefix="/vision",
    tags=["Vision"],
)


class VisionRequest(
    BaseModel
):
    prompt: str = Field(
        min_length=1,
        max_length=2000,
    )


@router.get("/capture")
def capture_screen():
    try:
        capture = (
            capture_primary_screen()
        )

        return Response(
            content=(
                capture.image_bytes
            ),
            media_type="image/png",
            headers={
                "Cache-Control":
                    "no-store"
            },
        )

    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to capture "
                "the screen."
            ),
        ) from exc


@router.post("/analyze")
def analyze_screen(
    request: VisionRequest,
):
    try:
        return (
            analyze_current_screen(
                request.prompt
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
        status_code=502,
        detail=(
            f"Ollama returned "
            f"{exc.response.status_code}: "
            f"{exc.response.text[:1000]}"
        ),
    ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
        status_code=502,
        detail=(
            f"{type(exc).__name__}: "
            f"{str(exc)}"
        ),
    ) from exc