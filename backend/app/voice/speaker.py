import threading

import pyttsx3


_speech_lock = (
    threading.Lock()
)


def speak_text(
    text: str,
) -> dict:

    cleaned_text = (
        text.strip()
    )

    if not cleaned_text:
        raise ValueError(
            "Speech text cannot be empty."
        )

    with _speech_lock:
        engine = (
            pyttsx3.init()
        )

        engine.setProperty(
            "rate",
            180,
        )

        engine.say(
            cleaned_text
        )

        engine.runAndWait()

        engine.stop()

    return {
        "ok": True,
        "text": cleaned_text,
    }