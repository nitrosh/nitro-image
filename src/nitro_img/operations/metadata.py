"""Metadata operations: strip EXIF, read metadata, auto-orient."""

from __future__ import annotations

from PIL import Image as PILImage
from PIL.ExifTags import Base as ExifBase


def auto_orient(img: PILImage.Image) -> PILImage.Image:
    """Apply EXIF orientation and remove the orientation tag."""
    try:
        exif = img.getexif()
        orientation = exif.get(ExifBase.Orientation)
        if orientation is None:
            return img

        transforms = {
            2: PILImage.FLIP_LEFT_RIGHT,
            3: PILImage.ROTATE_180,
            4: PILImage.FLIP_TOP_BOTTOM,
            5: PILImage.TRANSPOSE,
            6: PILImage.ROTATE_270,
            7: PILImage.TRANSVERSE,
            8: PILImage.ROTATE_90,
        }
        if orientation in transforms:
            img = img.transpose(transforms[orientation])
            exif[ExifBase.Orientation] = 1
        return img
    except Exception:
        return img


def strip_metadata() -> callable:
    """Remove all EXIF, IPTC, and XMP metadata."""
    def _strip(img: PILImage.Image) -> PILImage.Image:
        cleaned = PILImage.frombytes(img.mode, img.size, img.tobytes())
        return cleaned
    return _strip


def get_metadata(img: PILImage.Image) -> dict:
    """Read image dimensions, format, color space, and EXIF data."""
    info: dict = {
        "width": img.size[0],
        "height": img.size[1],
        "mode": img.mode,
        "format": getattr(img, "format", None),
    }

    try:
        exif = img.getexif()
        if exif:
            exif_data = {}
            for tag_id, value in exif.items():
                tag_name = ExifBase(tag_id).name if tag_id in ExifBase._value2member_map_ else str(tag_id)
                try:
                    exif_data[tag_name] = str(value)
                except Exception:
                    exif_data[tag_name] = repr(value)
            info["exif"] = exif_data
    except Exception:
        pass

    return info
