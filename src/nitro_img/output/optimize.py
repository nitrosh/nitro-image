"""Quality optimization and file size targeting."""

from __future__ import annotations

from PIL import Image as PILImage

from ..types import Format
from .encode import encode


def optimize(
    img: PILImage.Image,
    fmt: Format,
    target_kb: int,
    *,
    min_quality: int = 10,
    max_quality: int = 95,
) -> tuple[bytes, int]:
    """Binary-search for the best quality that fits within target_kb.

    Returns (encoded_bytes, quality_used).
    """
    if fmt not in (Format.JPEG, Format.WEBP):
        # PNG/GIF/BMP don't have meaningful quality knobs — just encode
        data = encode(img, fmt)
        return data, 0

    target_bytes = target_kb * 1024
    lo, hi = min_quality, max_quality
    best_data: bytes | None = None
    best_quality = hi

    # Start with max quality — if it already fits, return immediately
    data = encode(img, fmt, quality=hi)
    if len(data) <= target_bytes:
        return data, hi

    while lo <= hi:
        mid = (lo + hi) // 2
        data = encode(img, fmt, quality=mid)

        if len(data) <= target_bytes:
            best_data = data
            best_quality = mid
            lo = mid + 1  # Try higher quality that still fits
        else:
            hi = mid - 1

    if best_data is not None:
        return best_data, best_quality

    # Even at min quality, exceeds target — return lowest quality result
    data = encode(img, fmt, quality=min_quality)
    return data, min_quality


def auto_format(img: PILImage.Image, quality: int | None = None) -> tuple[bytes, Format]:
    """Pick the best format for the image content.

    - Images with transparency -> PNG
    - Photographic content -> WebP (smaller than JPEG)
    - Fallback -> WebP
    """
    has_alpha = img.mode in ("RGBA", "LA", "PA")

    if has_alpha:
        # Check if alpha channel is actually used
        if img.mode == "RGBA":
            alpha = img.getchannel("A")
            extrema = alpha.getextrema()
            if extrema == (255, 255):
                has_alpha = False  # Fully opaque, alpha not needed

    if has_alpha:
        data = encode(img, Format.PNG)
        return data, Format.PNG

    # Compare WebP vs JPEG size at equivalent quality
    webp_data = encode(img, Format.WEBP, quality=quality)
    jpeg_data = encode(img, Format.JPEG, quality=quality)

    if len(webp_data) <= len(jpeg_data):
        return webp_data, Format.WEBP
    return jpeg_data, Format.JPEG
