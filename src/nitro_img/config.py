"""Global configuration with sensible defaults."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Config:
    """Process-wide defaults for load, processing, and output behaviour.

    A single instance is exposed as ``nitro_img.config``. Fields are
    read at operation time, so calling ``config.update(...)`` takes
    effect for every subsequent operation without recreating the
    ``Image`` instance.

    Attributes:
        max_input_size: Maximum accepted input size in bytes. Larger
            inputs raise :class:`ImageSizeError`.
        max_output_dimensions: Maximum width or height in pixels for any
            resize result.
        default_jpeg_quality: JPEG quality used when no explicit value is
            passed to ``.jpeg()`` or an output method.
        default_webp_quality: WebP quality used when no explicit value is
            passed to ``.webp()``.
        default_png_compression: PNG ``zlib`` compression level (0-9).
        allow_upscale: Permit enlarging images beyond their native
            dimensions during resize operations.
        auto_orient: Apply EXIF orientation to loaded images so downstream
            operations see upright pixels.
        strip_metadata: Strip EXIF/IPTC/XMP from every loaded image before
            the pipeline runs.
        url_timeout: Request timeout in seconds for ``Image.from_url``.
        url_max_size: Maximum accepted response size in bytes for
            ``Image.from_url``.

    Example:
        >>> from nitro_img import config
        >>> config.update(default_webp_quality=75, allow_upscale=True)
    """

    max_input_size: int = 50_000_000       # 50 MB
    max_output_dimensions: int = 10_000    # 10k px
    default_jpeg_quality: int = 85
    default_webp_quality: int = 80
    default_png_compression: int = 6
    allow_upscale: bool = False
    auto_orient: bool = True
    strip_metadata: bool = False
    url_timeout: float = 30.0
    url_max_size: int = 50_000_000         # 50 MB

    def update(self, **kwargs: object) -> None:
        """Update one or more config fields in place.

        Args:
            **kwargs: Field names and their new values. Every key must
                match an existing attribute on :class:`Config`.

        Raises:
            ValueError: If a keyword does not match a known config field.

        Example:
            >>> config.update(default_jpeg_quality=90, allow_upscale=True)
        """
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise ValueError(f"Unknown config option: {key}")
            setattr(self, key, value)


config = Config()
