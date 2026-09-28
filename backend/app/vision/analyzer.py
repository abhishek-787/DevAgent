import base64

import httpx

from app.core.config import (
    settings,
)
from app.vision.screen import (
    capture_primary_screen,
)


VISION_TIMEOUT = httpx.Timeout(
    connect=10.0,
    read=300.0,
    write=60.0,
    pool=10.0,
)


VISION_SYSTEM_PROMPT = """
You are the visual fallback system for DevAgent,
a software-development agent.

Analyze only information visibly present in the screenshot.

Do not assume hidden application state.
Do not claim that you clicked, typed, opened, or changed anything.

If text is unreadable, say that it is unreadable.

Focus on software-development information such as:
- visible errors
- dialogs
- application state
- editor UI
- terminal output
- browser UI
- buttons or controls
- other information that cannot be obtained directly
  through normal system tools.

Answer only the user's visual question.
""".strip()

def analyze_current_screen(
    prompt: str,
) -> dict:

    cleaned_prompt = (
        prompt.strip()
    )

    if not cleaned_prompt:
        raise ValueError(
            "Vision prompt cannot be empty."
        )

    capture = (
        capture_primary_screen()
    )

    encoded_image = (
        base64.b64encode(
            capture.image_bytes
        )
        .decode("ascii")
    )

    url = (
        settings.ollama_base_url.rstrip("/")+"/api/chat"
    )

    payload = {
        "model":
            settings.vision_model,

        "stream":
            False,

        "messages": [
            {
                "role": "system",
                "content":
                    VISION_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content":
                    cleaned_prompt,
                "images": [
                    encoded_image
                ],
            },
        ],

        "options": {
            "temperature": 0,
        },
    }

    with httpx.Client(
        timeout=VISION_TIMEOUT
    ) as client:

        response = client.post(
            url,
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

    message = data.get(
        "message"
    )

    if not isinstance(
        message,
        dict,
    ):
        raise RuntimeError(
            "Vision model returned "
            "an invalid response."
        )

    content = message.get(
        "content"
    )

    if (
        not isinstance(
            content,
            str,
        )
        or not content.strip()
    ):
        raise RuntimeError(
            "Vision model returned "
            "an empty response."
        )

    return {
        "answer":
            content.strip(),

        "model":
            settings.vision_model,

        "screenshot_width":
            capture.width,

        "screenshot_height":
            capture.height,
    }

        
