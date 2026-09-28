from pathlib import Path

from faster_whisper import (
    WhisperModel,
)

from app.core.config import (
    settings,
)

_whisper_model:(
    WhisperModel | None
) = None

def _get_whisper_model() -> WhisperModel:
    global _whisper_model

    if _whisper_model is None:
        _whisper_model = WhisperModel(
            settings.stt_model,
            device="cpu",
            compute_type="int8",
        )
    return _whisper_model

def transcribe_audio(
    audio_path: Path,
) -> dict:

    if not audio_path.is_file():
        raise ValueError(
            "Audio file does not exist."
        )

    model = (
        _get_whisper_model()
    )

    segments, info = (
        model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=True,
        )
    )

    text_parts: list[str] = []

    for segment in segments:
        cleaned_text = (
            segment.text.strip()
        )

        if cleaned_text:
            text_parts.append(
                cleaned_text
            )

    text = " ".join(
        text_parts
    ).strip()

    if not text:
        raise RuntimeError(
            "No speech could be "
            "transcribed."
        )

    return {
        "text": text,
        "language": info.language,
        "language_probability": (
            float(
                info.language_probability
            )
        ),
    }