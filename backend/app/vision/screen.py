from dataclasses import dataclass
from io import BytesIO

from PIL import (
    Image,
    ImageGrab,
)


MAX_SCREENSHOT_WIDTH = 1280
MAX_SCREENSHOT_HEIGHT = 720

@dataclass
class ScreenCapture:
    image_bytes: bytes
    width: int
    height: int

def capture_primary_screen()-> ScreenCapture:
    image = ImageGrab.grab(
        all_screens=False
    )

    scale = min(
        1.0,
        MAX_SCREENSHOT_WIDTH/image.width,
        MAX_SCREENSHOT_HEIGHT/image.height,
    )

    if scale < 1.0:
        new_width = int(
            image.width * scale
        )

        new_height = int(
            image.height * scale
        )
        image = image.resize(
            (
                new_width,
                new_height,
            ),
            Image.Resampling.LANCZOS,
        )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG",
        optimize=True
    )

    return ScreenCapture(
        image_bytes=buffer.getvalue(),
        width=image.width,
        height=image.height,
    )