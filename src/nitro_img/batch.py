"""Batch/glob processing for multiple images."""

from __future__ import annotations

import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .errors import ImageLoadError
from .image import Image
from .types import Anchor, Format


class BatchImage:
    """Apply the same pipeline to every file matching a glob pattern.

    Unlike :class:`Image`, ``BatchImage`` does not hold a shared
    ``Pipeline``. Each chainable method records the call name and
    arguments; on ``save`` a fresh ``Image`` is constructed for every
    matched file and the recorded calls are replayed against it.

    The constructor raises immediately if the glob matches zero files
    so batch mistakes surface before pipeline construction.

    Example:
        >>> from nitro_img import BatchImage
        >>> (
        ...     BatchImage("photos/*.jpg")
        ...     .resize(800)
        ...     .webp(quality=80)
        ...     .save("output/{name}.webp", parallel=True)
        ... )
    """

    def __init__(self, pattern: str) -> None:
        """Build a batch from a glob pattern.

        Args:
            pattern: A ``glob`` pattern (e.g. ``"photos/*.jpg"``).

        Raises:
            ImageLoadError: If no files match the pattern.
        """
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
        """Record a proportional resize applied to every file.

        See :meth:`Image.resize` for semantics.

        Args:
            width: Target width in pixels.
            height: Target height in pixels.
            **kw: Keyword arguments forwarded to :meth:`Image.resize`.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").resize(800).webp().save("out/{name}.webp")
        """
        return self._record("resize", width, height, **kw)

    def thumbnail(self, width: int, height: int, **kw: object) -> BatchImage:
        """Record a thumbnail fit inside ``width`` x ``height`` for each file.

        See :meth:`Image.thumbnail` for semantics.

        Args:
            width: Maximum width in pixels.
            height: Maximum height in pixels.
            **kw: Keyword arguments forwarded to :meth:`Image.thumbnail`.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").thumbnail(200, 200).save("thumbs/{name}.jpg")
        """
        return self._record("thumbnail", width, height, **kw)

    def cover(self, width: int, height: int, **kw: object) -> BatchImage:
        """Record a cover-fit resize applied to every file.

        See :meth:`Image.cover` for semantics.

        Args:
            width: Target width in pixels.
            height: Target height in pixels.
            **kw: Keyword arguments forwarded to :meth:`Image.cover`.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").cover(400, 400).save("squares/{name}.jpg")
        """
        return self._record("cover", width, height, **kw)

    def contain(self, width: int, height: int, bg: str = "white", **kw: object) -> BatchImage:
        """Record a contain-fit resize applied to every file.

        See :meth:`Image.contain` for semantics.

        Args:
            width: Target width in pixels.
            height: Target height in pixels.
            bg: Background color used for padding.
            **kw: Keyword arguments forwarded to :meth:`Image.contain`.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").contain(400, 400, bg="black").save("out/{name}.jpg")
        """
        return self._record("contain", width, height, bg, **kw)

    def crop(self, width: int, height: int, anchor: Anchor = "center") -> BatchImage:
        """Record a crop applied to every file.

        See :meth:`Image.crop` for semantics.

        Args:
            width: Crop width in pixels.
            height: Crop height in pixels.
            anchor: Crop anchor point.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").crop(500, 400, anchor="top").save("out/{name}.jpg")
        """
        return self._record("crop", width, height, anchor)

    def rotate(self, degrees: float, **kw: object) -> BatchImage:
        """Record a rotation applied to every file.

        See :meth:`Image.rotate` for semantics.

        Args:
            degrees: Rotation angle in degrees counter-clockwise.
            **kw: Keyword arguments forwarded to :meth:`Image.rotate`.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("scans/*.jpg").rotate(90).save("out/{name}.jpg")
        """
        return self._record("rotate", degrees, **kw)

    def flip(self) -> BatchImage:
        """Record a vertical flip applied to every file.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").flip().save("out/{name}.jpg")
        """
        return self._record("flip")

    def mirror(self) -> BatchImage:
        """Record a horizontal flip applied to every file.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").mirror().save("out/{name}.jpg")
        """
        return self._record("mirror")

    def grayscale(self) -> BatchImage:
        """Record a grayscale conversion applied to every file.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").grayscale().save("out/{name}.jpg")
        """
        return self._record("grayscale")

    def strip_metadata(self) -> BatchImage:
        """Record metadata stripping (EXIF/IPTC/XMP) for every file.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("uploads/*.jpg").strip_metadata().save("clean/{name}.jpg")
        """
        return self._record("strip_metadata")

    def brightness(self, factor: float) -> BatchImage:
        """Record a brightness adjustment applied to every file.

        Args:
            factor: Multiplier where ``1.0`` is unchanged.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").brightness(1.1).save("out/{name}.jpg")
        """
        return self._record("brightness", factor)

    def contrast(self, factor: float) -> BatchImage:
        """Record a contrast adjustment applied to every file.

        Args:
            factor: Multiplier where ``1.0`` is unchanged.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").contrast(1.15).save("out/{name}.jpg")
        """
        return self._record("contrast", factor)

    def saturation(self, factor: float) -> BatchImage:
        """Record a saturation adjustment applied to every file.

        Args:
            factor: Multiplier where ``1.0`` is unchanged.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").saturation(1.2).save("out/{name}.jpg")
        """
        return self._record("saturation", factor)

    def sharpen(self, factor: float = 2.0) -> BatchImage:
        """Record a sharpness adjustment applied to every file.

        Args:
            factor: Multiplier where ``1.0`` is unchanged.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").sharpen(1.3).save("out/{name}.jpg")
        """
        return self._record("sharpen", factor)

    def blur(self, radius: float = 2.0) -> BatchImage:
        """Record a Gaussian blur applied to every file.

        Args:
            radius: Blur radius in pixels.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").blur(3.0).save("out/{name}.jpg")
        """
        return self._record("blur", radius)

    def sepia(self) -> BatchImage:
        """Record a sepia tone effect applied to every file.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").sepia().save("out/{name}.jpg")
        """
        return self._record("sepia")

    def rounded_corners(self, radius: int) -> BatchImage:
        """Record rounded-corner masking applied to every file.

        Use PNG or WebP output to preserve the alpha channel.

        Args:
            radius: Corner radius in pixels.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").rounded_corners(16).png().save("out/{name}.png")
        """
        return self._record("rounded_corners", radius)

    def watermark(
        self, source: object, position: str = "bottom-right",
        opacity: float = 0.3, scale: float | None = None, margin: int = 10,
    ) -> BatchImage:
        """Record an image watermark applied to every file.

        See :meth:`Image.watermark` for parameter semantics.

        Args:
            source: Path, ``Path``, or PIL image for the watermark.
            position: Anchor position or ``"tiled"``.
            opacity: Blend opacity between 0.0 and 1.0.
            scale: Optional watermark width as a fraction of the base
                image width.
            margin: Distance from the anchored edge in pixels.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").watermark("logo.png").save("out/{name}.jpg")
        """
        return self._record("watermark", source, position, opacity, scale, margin)

    def text_overlay(self, text: str, **kw: object) -> BatchImage:
        """Record a text overlay applied to every file.

        See :meth:`Image.text_overlay` for supported keyword arguments.

        Args:
            text: Text to render on each image.
            **kw: Keyword arguments forwarded to :meth:`Image.text_overlay`.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").text_overlay("Draft").save("out/{name}.jpg")
        """
        return self._record("text_overlay", text, **kw)

    # -- Format selection --

    def jpeg(self, quality: int | None = None) -> BatchImage:
        """Select JPEG for every image in the batch.

        Args:
            quality: Encoder quality (1-100). Falls back to
                ``config.default_jpeg_quality`` when None.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.png").resize(800).jpeg(quality=85).save("out/{name}.jpg")
        """
        self._output_format = Format.JPEG
        self._output_quality = quality
        return self

    def png(self) -> BatchImage:
        """Select PNG for every image in the batch.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").png().save("out/{name}.png")
        """
        self._output_format = Format.PNG
        return self

    def webp(self, quality: int | None = None) -> BatchImage:
        """Select WebP for every image in the batch.

        Args:
            quality: Encoder quality (1-100). Falls back to
                ``config.default_webp_quality`` when None.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").webp(quality=80).save("out/{name}.webp")
        """
        self._output_format = Format.WEBP
        self._output_quality = quality
        return self

    def format(self, fmt: Format | str, quality: int | None = None) -> BatchImage:
        """Select the output format by enum or case-insensitive string.

        Args:
            fmt: Desired format, either a :class:`Format` member or a
                string such as ``"webp"``.
            quality: Encoder quality for formats that support it.

        Returns:
            The same ``BatchImage`` for chaining.

        Example:
            >>> BatchImage("photos/*.jpg").format("webp", quality=75).save("out/{name}.webp")
        """
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
        """Save every matched image through the recorded pipeline.

        Args:
            pattern: Destination path pattern; the substring ``{name}``
                is replaced with each source file's stem.
            parallel: When True, process files concurrently using a
                thread pool. Useful for IO-bound batches; CPU-bound
                batches may not benefit because of the GIL.
            max_workers: Thread pool size used when ``parallel`` is True.
                Defaults to ``min(count, 8)``.

        Returns:
            A list of destination paths in the order of the matched
            source files.

        Example:
            >>> BatchImage("photos/*.jpg").resize(800).webp().save(
            ...     "out/{name}.webp", parallel=True
            ... )
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
        """Number of files matched by the glob pattern."""
        return len(self._paths)

    @property
    def paths(self) -> list[str]:
        """List of matched source file paths, sorted alphabetically."""
        return list(self._paths)
