import tempfile
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import (
    BaseModel,
    Field,
)

from app.agents.agent_service import (
    run_coding_task,
)
from app.voice.speaker import (
    speak_text,
)
from app.voice.transcriber import (
    transcribe_audio,
)


router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)

ALLOWED_AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".flac",
    ".ogg",
    ".webm",
}


MAX_AUDIO_SIZE_BYTES = (
    25 * 1024 * 1024
)

class SpeakRequest(
    BaseModel
):
    text: str = Field(
        min_length=1,
        max_length=5000,
    )

async def _save_audio_upload(
    audio: UploadFile,
) -> Path:

    suffix = Path(
        audio.filename or ""
    ).suffix.lower()

    if (
        suffix
        not in ALLOWED_AUDIO_EXTENSIONS
    ):
        raise ValueError(
            "Unsupported audio format."
        )

    content = await audio.read()

    if not content:
        raise ValueError(
            "Audio file is empty."
        )

    if (
        len(content)
        > MAX_AUDIO_SIZE_BYTES
    ):
        raise ValueError(
            "Audio file is too large."
        )

    temporary_file = (
        tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        )
    )

    try:
        temporary_file.write(
            content
        )

    finally:
        temporary_file.close()

    return Path(
        temporary_file.name
    )


@router.post("/transcribe")
async def transcribe_voice(
    audio: UploadFile = File(...),
):
    audio_path: Path | None = None

    try:
        audio_path = (
            await _save_audio_upload(
                audio
            )
        )

        return transcribe_audio(
            audio_path
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

    finally:
        if (
            audio_path is not None
            and audio_path.exists()
        ):
            audio_path.unlink(
                missing_ok=True
            )

@router.post("/speak")
def speak_voice(
    request: SpeakRequest,
):
    try:
        return speak_text(
            request.text
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

@router.post("/agent")
async def voice_agent_task(
    audio: UploadFile = File(...),
    speak_response: bool = Form(
        default=True
    ),
):
    audio_path: Path | None = None

    try:
        audio_path = (
            await _save_audio_upload(
                audio
            )
        )

        transcription = (
            transcribe_audio(
                audio_path
            )
        )

        user_message = (
            transcription["text"]
        )

        agent_result = (
            run_coding_task(
                user_message
            )
        )

        answer = (
            agent_result.get(
                "answer",
                "",
            )
        )

        if (
            speak_response
            and answer.strip()
        ):
            speak_text(
                answer
            )

        return {
            "transcription":
                transcription,

            "agent":
                agent_result,

            "spoken":
                bool(
                    speak_response
                    and answer.strip()
                ),
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

    finally:
        if (
            audio_path is not None
            and audio_path.exists()
        ):
            audio_path.unlink(
                missing_ok=True
            )