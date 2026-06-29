import base64
import io
from typing import NamedTuple

from PIL import Image, ImageGrab


class Screenshot(NamedTuple):
    image: Image.Image
    data_url: str           # "data:image/png;base64,..."
    thumb: Image.Image      # 160×90 thumbnail for preview


def capture_screen() -> Screenshot:
    img = ImageGrab.grab()
    data_url = _to_data_url(img)
    thumb = img.copy()
    thumb.thumbnail((160, 90))
    return Screenshot(image=img, data_url=data_url, thumb=thumb)


def _to_data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"
