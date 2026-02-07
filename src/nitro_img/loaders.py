"""Input loaders: file, bytes, URL, upload, base64."""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import IO, TYPE_CHECKING

from PIL import Image as PILImage

from .config import config
from .errors import ImageLoadError, ImageSizeError
from .utils import format_from_pillow

if TYPE_CHECKING:
    from .types import Format


def _validate_size(data: bytes) -> None:
    if len(data) > config.max_input_size:
        raise ImageSizeError(
            f"Input size {len(data)} bytes exceeds limit of {config.max_input_size} bytes"
        )


def _post_load(img: PILImage.Image) -> PILImage.Image:
    if config.auto_orient:
        from .operations.metadata import auto_orient
        img = auto_orient(img)
    return img


def _detect_format(img: PILImage.Image) -> Format | None:
    return format_from_pillow(img.format)


def load_from_path(path: str | Path) -> tuple[PILImage.Image, Format | None, str | Path]:
    path = Path(path)
    if not path.exists():
        raise ImageLoadError(f"File not found: {path}")
    try:
        size = path.stat().st_size
        if size > config.max_input_size:
            raise ImageSizeError(
                f"File size {size} bytes exceeds limit of {config.max_input_size} bytes"
            )
        img = PILImage.open(path)
        img.load()
        fmt = _detect_format(img)
        img = _post_load(img)
        return img, fmt, path
    except ImageSizeError:
        raise
    except Exception as e:
        raise ImageLoadError(f"Cannot load '{path}': {e}") from e


def load_from_bytes(data: bytes) -> tuple[PILImage.Image, Format | None, None]:
    _validate_size(data)
    try:
        img = PILImage.open(io.BytesIO(data))
        img.load()
        fmt = _detect_format(img)
        img = _post_load(img)
        return img, fmt, None
    except Exception as e:
        raise ImageLoadError(f"Cannot load image from bytes: {e}") from e


def load_from_file(file_obj: IO[bytes]) -> tuple[PILImage.Image, Format | None, None]:
    try:
        data = file_obj.read()
        return load_from_bytes(data)
    except ImageLoadError:
        raise
    except Exception as e:
        raise ImageLoadError(f"Cannot load image from file object: {e}") from e


def load_from_base64(b64_string: str) -> tuple[PILImage.Image, Format | None, None]:
    # Strip data URI prefix if present
    if "," in b64_string and b64_string.startswith("data:"):
        b64_string = b64_string.split(",", 1)[1]
    try:
        data = base64.b64decode(b64_string)
    except Exception as e:
        raise ImageLoadError(f"Invalid base64 data: {e}") from e
    return load_from_bytes(data)


def load_from_url(url: str) -> tuple[PILImage.Image, Format | None, None]:
    try:
        import httpx
    except ImportError:
        raise ImageLoadError(
            "httpx is required for URL loading. Install with: pip install nitro-img[url]"
        )
    try:
        response = httpx.get(url, timeout=config.url_timeout, follow_redirects=True)
        response.raise_for_status()
    except Exception as e:
        raise ImageLoadError(f"Cannot fetch image from '{url}': {e}") from e
    return load_from_bytes(response.content)
