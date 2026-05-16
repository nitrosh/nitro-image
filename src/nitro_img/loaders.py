"""Input loaders: file, bytes, URL, upload, base64."""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import IO, TYPE_CHECKING
from urllib.parse import urlparse

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


def _check_pixel_count(img: PILImage.Image) -> None:
    width, height = img.size
    pixels = width * height
    if pixels > config.max_pixels:
        raise ImageSizeError(
            f"Image has {pixels} pixels ({width}x{height}), exceeds limit of "
            f"{config.max_pixels}. Adjust config.max_pixels to allow larger inputs."
        )


def _post_load(img: PILImage.Image) -> PILImage.Image:
    if config.auto_orient:
        from .operations.metadata import auto_orient
        img = auto_orient(img)
    if config.strip_metadata:
        from .operations.metadata import strip_metadata
        img = strip_metadata()(img)
    return img


def _detect_format(img: PILImage.Image) -> Format | None:
    return format_from_pillow(img.format)


def _open_and_validate(source: object) -> PILImage.Image:
    img = PILImage.open(source)
    _check_pixel_count(img)
    img.load()
    return img


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
        img = _open_and_validate(path)
        fmt = _detect_format(img)
        img = _post_load(img)
        return img, fmt, path
    except (ImageSizeError, ImageLoadError):
        raise
    except Exception as e:
        raise ImageLoadError(f"Cannot load '{path}': {e}") from e


def load_from_bytes(data: bytes) -> tuple[PILImage.Image, Format | None, None]:
    _validate_size(data)
    try:
        img = _open_and_validate(io.BytesIO(data))
        fmt = _detect_format(img)
        img = _post_load(img)
        return img, fmt, None
    except (ImageSizeError, ImageLoadError):
        raise
    except Exception as e:
        raise ImageLoadError(f"Cannot load image from bytes: {e}") from e


def load_from_file(file_obj: IO[bytes]) -> tuple[PILImage.Image, Format | None, None]:
    try:
        data = file_obj.read()
        return load_from_bytes(data)
    except (ImageLoadError, ImageSizeError):
        raise
    except Exception as e:
        raise ImageLoadError(f"Cannot load image from file object: {e}") from e


def load_from_base64(b64_string: str) -> tuple[PILImage.Image, Format | None, None]:
    if "," in b64_string and b64_string.startswith("data:"):
        b64_string = b64_string.split(",", 1)[1]
    try:
        data = base64.b64decode(b64_string)
    except Exception as e:
        raise ImageLoadError(f"Invalid base64 data: {e}") from e
    return load_from_bytes(data)


def _validate_url_scheme(url: str) -> None:
    scheme = urlparse(url).scheme.lower()
    allowed = tuple(s.lower() for s in config.url_allowed_schemes)
    if scheme not in allowed:
        raise ImageLoadError(
            f"URL scheme '{scheme}' is not allowed. "
            f"Permitted schemes: {', '.join(allowed)}."
        )


def _stream_url_body(url: str) -> bytes:
    import httpx

    limit = config.url_max_size
    chunks: list[bytes] = []
    total = 0
    with httpx.stream(
        "GET", url, timeout=config.url_timeout, follow_redirects=True,
    ) as response:
        response.raise_for_status()
        # Honour Content-Length when present so oversized bodies fail fast.
        declared = response.headers.get("Content-Length")
        if declared is not None:
            try:
                if int(declared) > limit:
                    raise ImageSizeError(
                        f"URL response declares {declared} bytes, exceeds limit of {limit}"
                    )
            except ValueError:
                pass
        for chunk in response.iter_bytes():
            total += len(chunk)
            if total > limit:
                raise ImageSizeError(
                    f"URL response exceeded limit of {limit} bytes; download aborted"
                )
            chunks.append(chunk)
    return b"".join(chunks)


def load_from_url(url: str) -> tuple[PILImage.Image, Format | None, None]:
    try:
        import httpx  # noqa: F401
    except ImportError:
        raise ImageLoadError(
            "httpx is required for URL loading. Install with: pip install nitro-img[url]"
        )
    _validate_url_scheme(url)
    try:
        data = _stream_url_body(url)
    except (ImageSizeError, ImageLoadError):
        raise
    except Exception as e:
        raise ImageLoadError(f"Cannot fetch image from '{url}': {e}") from e
    return load_from_bytes(data)
