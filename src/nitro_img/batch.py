"""Batch/glob processing for multiple images."""

from __future__ import annotations

import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .errors import ImageLoadError
from .image import Image
from .types import Anchor, Format


class BatchImage:
    """Process multiple images with the same pipeline.

    Operations are recorded and applied to each image on output.
    """

    def __init__(self, pattern: str) -> None:
        self._paths = sorted(glob.glob(pattern))
        if not self._paths:
            raise ImageLoadError(f"No files matched pattern: {pattern}")
        self._operations: list[tuple[str, tuple, dict]] = []
        self._output_format: Format | None = None
        self._output_quality: int | None = None

    def _record(self, method: str, *args: object, **kwargs: object) -> BatchImage:
        self._operations.append((method, args, kwargs))
        return self

    # -- Chainable operations (recorded, not executed) --

    def resize(self, width: int | None = None, height: int | None = None, **kw: object) -> BatchImage:
        return self._record("resize", width, height, **kw)

    def thumbnail(self, width: int, height: int, **kw: object) -> BatchImage:
        return self._record("thumbnail", width, height, **kw)

    def cover(self, width: int, height: int, **kw: object) -> BatchImage:
        return self._record("cover", width, height, **kw)

    def contain(self, width: int, height: int, bg: str = "white", **kw: object) -> BatchImage:
        return self._record("contain", width, height, bg, **kw)

    def crop(self, width: int, height: int, anchor: Anchor = "center") -> BatchImage:
        return self._record("crop", width, height, anchor)

    def rotate(self, degrees: float, **kw: object) -> BatchImage:
        return self._record("rotate", degrees, **kw)

    def flip(self) -> BatchImage:
        return self._record("flip")

    def mirror(self) -> BatchImage:
        return self._record("mirror")

    def grayscale(self) -> BatchImage:
        return self._record("grayscale")

    def strip_metadata(self) -> BatchImage:
        return self._record("strip_metadata")

    def brightness(self, factor: float) -> BatchImage:
        return self._record("brightness", factor)

    def contrast(self, factor: float) -> BatchImage:
        return self._record("contrast", factor)

    def saturation(self, factor: float) -> BatchImage:
        return self._record("saturation", factor)

    def sharpen(self, factor: float = 2.0) -> BatchImage:
        return self._record("sharpen", factor)

    def blur(self, radius: float = 2.0) -> BatchImage:
        return self._record("blur", radius)

    def sepia(self) -> BatchImage:
        return self._record("sepia")

    def rounded_corners(self, radius: int) -> BatchImage:
        return self._record("rounded_corners", radius)

    def watermark(
        self, source: object, position: str = "bottom-right",
        opacity: float = 0.3, scale: float | None = None, margin: int = 10,
    ) -> BatchImage:
        return self._record("watermark", source, position, opacity, scale, margin)

    def text_overlay(self, text: str, **kw: object) -> BatchImage:
        return self._record("text_overlay", text, **kw)

    # -- Format selection --

    def jpeg(self, quality: int | None = None) -> BatchImage:
        self._output_format = Format.JPEG
        self._output_quality = quality
        return self

    def png(self) -> BatchImage:
        self._output_format = Format.PNG
        return self

    def webp(self, quality: int | None = None) -> BatchImage:
        self._output_format = Format.WEBP
        self._output_quality = quality
        return self

    def format(self, fmt: Format | str, quality: int | None = None) -> BatchImage:
        if isinstance(fmt, str):
            fmt = Format(fmt.upper())
        self._output_format = fmt
        if quality is not None:
            self._output_quality = quality
        return self

    # -- Output --

    def _apply_pipeline(self, img: Image) -> Image:
        for method_name, args, kwargs in self._operations:
            method = getattr(img, method_name)
            method(*args, **kwargs)
        if self._output_format is not None:
            img._output_format = self._output_format
            img._output_quality = self._output_quality
        return img

    def _process_one(self, src_path: str, pattern: str) -> Path:
        stem = Path(src_path).stem
        out_path = pattern.replace("{name}", stem)
        img = Image(src_path)
        img = self._apply_pipeline(img)
        return img.save(out_path)

    def save(self, pattern: str, *, parallel: bool = False, max_workers: int | None = None) -> list[Path]:
        """Save all images. Use {name} in pattern for the original filename stem.

        Args:
            parallel: If True, process images in parallel using threads.
            max_workers: Max thread count (default: min(count, 8)).
        """
        if not parallel:
            return [self._process_one(p, pattern) for p in self._paths]

        workers = max_workers or min(len(self._paths), 8)
        results: dict[int, Path] = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self._process_one, p, pattern): i
                for i, p in enumerate(self._paths)
            }
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()

        return [results[i] for i in sorted(results)]

    @property
    def count(self) -> int:
        return len(self._paths)

    @property
    def paths(self) -> list[str]:
        return list(self._paths)
