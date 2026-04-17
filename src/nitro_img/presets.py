"""Pre-built pipelines for common image tasks."""

from __future__ import annotations

from pathlib import Path
from typing import IO

from PIL import Image as PILImage, ImageDraw, ImageFont

from .types import Format
from . import loaders
from .operations.resize import resize_fit, cover
from .operations.metadata import strip_metadata as _strip_metadata_op
from .output.encode import encode
from .responsive import save_responsive


def _load(source: str | Path | bytes | IO[bytes]) -> tuple[PILImage.Image, Format | None]:
    if isinstance(source, bytes):
        img, fmt, _ = loaders.load_from_bytes(source)
    elif isinstance(source, (str, Path)):
        img, fmt, _ = loaders.load_from_path(source)
    else:
        img, fmt, _ = loaders.load_from_file(source)
    return img, fmt


class Presets:
    """One-call helpers for the most common image tasks.

    Each preset loads the source, runs a fixed pipeline, and returns the
    encoded bytes (or, for ``responsive``, a dict of saved paths). Use
    these when you want a sensible default without composing a pipeline.

    Access the shared instance as ``nitro_img.presets`` or
    ``Image.preset``.

    Example:
        >>> from nitro_img import presets
        >>> thumb = presets.thumbnail("photo.jpg")
        >>> og = presets.og_image("photo.jpg")
    """

    @staticmethod
    def thumbnail(
        source: str | Path | bytes,
        width: int = 200,
        height: int = 200,
        *,
        fmt: Format = Format.WEBP,
        quality: int | None = None,
    ) -> bytes:
        """Generate a thumbnail that fits within ``width`` by ``height``.

        Preserves aspect ratio and strips metadata. Returns the encoded
        bytes — does not write to disk.

        Args:
            source: File path, bytes, or file-like object.
            width: Maximum width of the thumbnail in pixels.
            height: Maximum height of the thumbnail in pixels.
            fmt: Output image format.
            quality: Encoder quality (format-specific); falls back to
                the matching config default when None.

        Returns:
            Encoded image bytes.

        Example:
            >>> from nitro_img import presets
            >>> data = presets.thumbnail("photo.jpg", width=150, height=150)
        """
        img, _ = _load(source)
        img = resize_fit(width, height)(img)
        img = _strip_metadata_op()(img)
        return encode(img, fmt, quality=quality)

    @staticmethod
    def avatar(
        source: str | Path | bytes,
        size: int = 128,
        *,
        fmt: Format = Format.PNG,
        quality: int | None = None,
    ) -> bytes:
        """Produce a square, circle-cropped avatar.

        Cover-crops to a square, then applies a circular alpha mask, so
        PNG or WebP output is recommended to preserve transparency.

        Args:
            source: File path, bytes, or file-like object.
            size: Side length of the square avatar in pixels.
            fmt: Output format; keep transparency-capable formats for the
                circle mask.
            quality: Encoder quality (format-specific).

        Returns:
            Encoded avatar bytes.

        Example:
            >>> from nitro_img import presets
            >>> avatar = presets.avatar("user.jpg", size=256)
        """
        img, _ = _load(source)
        # Cover to fill the square, then circle-mask
        img = cover(size, size, allow_upscale=True)(img)
        img = img.convert("RGBA")

        mask = PILImage.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size - 1, size - 1), fill=255)
        img.putalpha(mask)

        return encode(img, fmt, quality=quality)

    @staticmethod
    def avatar_placeholder(
        initials: str,
        size: int = 128,
        bg: str = "#4A90D9",
        text_color: str = "white",
        *,
        fmt: Format = Format.PNG,
    ) -> bytes:
        """Render a colored circle avatar with initials.

        Useful as a fallback when a user has not uploaded a profile image.
        No source image is required.

        Args:
            initials: Characters to draw in the centre of the circle;
                uppercased automatically.
            size: Side length of the avatar in pixels.
            bg: Background color for the circle (any value accepted by
                ``PIL.ImageColor``).
            text_color: Text color for the initials.
            fmt: Output format.

        Returns:
            Encoded avatar bytes.

        Example:
            >>> from nitro_img import presets
            >>> data = presets.avatar_placeholder("SN", bg="#E74C3C")
        """
        img = PILImage.new("RGBA", (size, size), bg)
        draw = ImageDraw.Draw(img)

        # Circle mask
        mask = PILImage.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, size - 1, size - 1), fill=255)
        img.putalpha(mask)

        # Draw initials
        font_size = size // 2
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), initials.upper(), font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) // 2
        y = (size - text_h) // 2 - bbox[1]  # Adjust for baseline offset
        draw.text((x, y), initials.upper(), fill=text_color, font=font)

        return encode(img, fmt)

    @staticmethod
    def og_image(
        source: str | Path | bytes,
        width: int = 1200,
        height: int = 630,
        *,
        fmt: Format = Format.JPEG,
        quality: int = 85,
    ) -> bytes:
        """Produce a social/Open Graph card image.

        Cover-crops to the target dimensions (1200x630 by default) so the
        result fills a typical social preview card without letterboxing.

        Args:
            source: File path, bytes, or file-like object.
            width: Target width in pixels.
            height: Target height in pixels.
            fmt: Output format.
            quality: Encoder quality.

        Returns:
            Encoded OG image bytes.

        Example:
            >>> from nitro_img import presets
            >>> card = presets.og_image("hero.jpg")
        """
        img, _ = _load(source)
        img = cover(width, height, allow_upscale=True)(img)
        img = _strip_metadata_op()(img)
        return encode(img, fmt, quality=quality)

    @staticmethod
    def banner(
        source: str | Path | bytes,
        width: int = 1920,
        height: int = 400,
        *,
        fmt: Format = Format.JPEG,
        quality: int = 85,
    ) -> bytes:
        """Produce a wide hero/banner crop.

        Cover-crops to a wide aspect ratio (1920x400 by default), which
        suits page headers and section dividers.

        Args:
            source: File path, bytes, or file-like object.
            width: Target width in pixels.
            height: Target height in pixels.
            fmt: Output format.
            quality: Encoder quality.

        Returns:
            Encoded banner bytes.

        Example:
            >>> from nitro_img import presets
            >>> hero = presets.banner("photo.jpg", width=2400, height=500)
        """
        img, _ = _load(source)
        img = cover(width, height, allow_upscale=True)(img)
        img = _strip_metadata_op()(img)
        return encode(img, fmt, quality=quality)

    @staticmethod
    def responsive(
        source: str | Path | bytes,
        widths: list[int] | None = None,
        output_dir: str | Path = ".",
        name: str = "image",
        *,
        fmt: Format = Format.WEBP,
        quality: int | None = None,
    ) -> dict[int, Path]:
        """Generate a responsive image set and save each width to disk.

        Writes files named ``{name}_{width}.{ext}`` into ``output_dir``
        (creating it if necessary). Suitable for building an ``<img
        srcset>`` set in one call.

        Args:
            source: File path, bytes, or file-like object.
            widths: Target widths in pixels. Defaults to
                ``[320, 640, 1024, 1920]``.
            output_dir: Destination directory.
            name: Filename prefix for each generated image.
            fmt: Output format used for every width.
            quality: Encoder quality applied uniformly.

        Returns:
            Mapping of width to the saved ``Path``.

        Example:
            >>> from nitro_img import presets
            >>> presets.responsive("hero.jpg", output_dir="static/", name="hero")
        """
        if widths is None:
            widths = [320, 640, 1024, 1920]
        img, _ = _load(source)
        img = _strip_metadata_op()(img)
        return save_responsive(img, widths, output_dir, name, fmt=fmt, quality=quality)


presets = Presets()
