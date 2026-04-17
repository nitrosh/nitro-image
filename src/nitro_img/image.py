"""Core Image class — chainable interface with lazy execution."""

from __future__ import annotations

from pathlib import Path
from typing import IO

from PIL import Image as PILImage

from .config import config
from .errors import ImageFormatError
from .pipeline import Pipeline
from .types import Anchor, Format
from .utils import format_from_extension

from . import loaders
from .operations import resize as resize_ops
from .operations import crop as crop_ops
from .operations import transform as transform_ops
from .operations import metadata as metadata_ops
from .operations import overlay as overlay_ops
from .operations import adjust as adjust_ops
from .operations import effects as effects_ops
from .output import export
from .output import optimize as optimize_mod


class Image:
    """Chainable image processing interface with lazy execution.

    Each ``Image`` wraps an original Pillow image plus a queue of pending
    operations. Transform methods (``resize``, ``brightness``, ...) append
    to the queue and return ``self`` so calls can be chained. No pixels
    are touched until an output method (``save``, ``to_bytes``,
    ``to_base64``, ``to_data_uri``, ``to_response``, ``responsive``, ...)
    is called, which runs the full pipeline once against a fresh copy of
    the source.

    Construct an instance from a filesystem path, or use the ``from_*``
    class methods for bytes, base64 strings, URLs, or file-like objects.

    Example:
        >>> from nitro_img import Image
        >>> (
        ...     Image("photo.jpg")
        ...     .resize(800)
        ...     .brightness(1.1)
        ...     .webp(quality=80)
        ...     .save("photo.webp")
        ... )
    """

    # Class-level preset accessor
    from .presets import Presets as _Presets
    preset = _Presets()

    def __init__(self, source: str | Path) -> None:
        """Load an image from a filesystem path.

        Args:
            source: Path to an image file on disk.

        Raises:
            ImageLoadError: If the file cannot be read or decoded.
            ImageSizeError: If the file exceeds ``config.max_input_size``.
        """
        img, fmt, path = loaders.load_from_path(source)
        self._original: PILImage.Image = img
        self._source_format: Format | None = fmt
        self._source_path: str | Path | None = path
        self._pipeline: Pipeline = Pipeline()
        self._output_format: Format | None = None
        self._output_quality: int | None = None
        self._auto_format: bool = False

    # -- Alternative constructors --

    @classmethod
    def _new_instance(
        cls,
        img: PILImage.Image,
        fmt: Format | None,
        path: str | Path | None = None,
    ) -> Image:
        inst = cls.__new__(cls)
        inst._original = img
        inst._source_format = fmt
        inst._source_path = path
        inst._pipeline = Pipeline()
        inst._output_format = None
        inst._output_quality = None
        inst._auto_format = False
        return inst

    @classmethod
    def from_bytes(cls, data: bytes) -> Image:
        """Create an ``Image`` from raw encoded image bytes.

        Args:
            data: Encoded image bytes (JPEG, PNG, WebP, ...).

        Returns:
            A new ``Image`` instance with an empty pipeline.

        Raises:
            ImageLoadError: If the bytes cannot be decoded.

        Example:
            >>> Image.from_bytes(response.content).resize(400).to_bytes()
        """
        img, fmt, _ = loaders.load_from_bytes(data)
        return cls._new_instance(img, fmt)

    @classmethod
    def from_file(cls, file_obj: IO[bytes]) -> Image:
        """Create an ``Image`` from a binary file-like object.

        Reads the stream fully, so the caller keeps ownership of the file
        handle but should not reuse the stream position.

        Args:
            file_obj: Any object with a ``read`` method returning bytes
                (e.g. Django's ``UploadedFile`` or Flask's
                ``FileStorage``).

        Returns:
            A new ``Image`` instance.

        Raises:
            ImageLoadError: If the stream cannot be decoded.

        Example:
            >>> with open("photo.jpg", "rb") as f:
            ...     img = Image.from_file(f)
        """
        img, fmt, _ = loaders.load_from_file(file_obj)
        return cls._new_instance(img, fmt)

    @classmethod
    def from_base64(cls, b64_string: str) -> Image:
        """Create an ``Image`` from a base64-encoded string.

        Accepts both plain base64 and full data URIs
        (``data:image/...;base64,...``).

        Args:
            b64_string: Base64 text, optionally prefixed with a data URI
                scheme.

        Returns:
            A new ``Image`` instance.

        Raises:
            ImageLoadError: If the string cannot be decoded to a valid
                image.

        Example:
            >>> img = Image.from_base64(data_uri)
        """
        img, fmt, _ = loaders.load_from_base64(b64_string)
        return cls._new_instance(img, fmt)

    @classmethod
    def from_url(cls, url: str) -> Image:
        """Fetch and load an image from a URL.

        Requires the ``url`` extra: ``pip install nitro-image[url]``.
        Download honours ``config.url_timeout`` and ``config.url_max_size``.

        Args:
            url: HTTP(S) URL pointing to an image.

        Returns:
            A new ``Image`` instance.

        Raises:
            ImageLoadError: If the download fails or the response is not
                a valid image.
            ImageSizeError: If the response exceeds ``config.url_max_size``.

        Example:
            >>> img = Image.from_url("https://example.com/photo.jpg")
        """
        img, fmt, _ = loaders.load_from_url(url)
        return cls._new_instance(img, fmt)

    # -- Resize operations --

    def resize(
        self,
        width: int | None = None,
        height: int | None = None,
        *,
        allow_upscale: bool | None = None,
    ) -> Image:
        """Queue a proportional resize, preserving aspect ratio.

        Supply one dimension to scale proportionally, or both to fit the
        image inside the given box. Downscales use Lanczos resampling;
        upscales are blocked by default because they degrade quality.

        Args:
            width: Target width in pixels, or None to derive from height.
            height: Target height in pixels, or None to derive from width.
            allow_upscale: Permit enlarging past the source size. Falls
                back to ``config.allow_upscale`` when None.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").resize(800).save("out.jpg")
        """
        up = allow_upscale if allow_upscale is not None else config.allow_upscale
        self._pipeline.add(
            "resize",
            resize_ops.resize_fit(width, height, allow_upscale=up),
        )
        return self

    def thumbnail(
        self,
        width: int,
        height: int,
        *,
        allow_upscale: bool | None = None,
    ) -> Image:
        """Queue an in-place thumbnail fit inside a box.

        Mirrors Pillow's ``thumbnail`` semantics: shrinks the image so
        both dimensions fit inside ``width`` x ``height`` while keeping
        aspect ratio.

        Args:
            width: Maximum width in pixels.
            height: Maximum height in pixels.
            allow_upscale: Permit enlarging images smaller than the box.
                Falls back to ``config.allow_upscale`` when None.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").thumbnail(200, 200).save("thumb.jpg")
        """
        up = allow_upscale if allow_upscale is not None else config.allow_upscale
        self._pipeline.add(
            "thumbnail",
            resize_ops.thumbnail(width, height, allow_upscale=up),
        )
        return self

    def cover(
        self,
        width: int,
        height: int,
        *,
        allow_upscale: bool | None = None,
    ) -> Image:
        """Queue a cover-fit resize, centre-cropping overflow.

        The output exactly matches ``width`` x ``height``; content that
        does not fit is cropped equally from both sides.

        Args:
            width: Target width in pixels.
            height: Target height in pixels.
            allow_upscale: Permit enlarging small images to fill the
                target. Falls back to ``config.allow_upscale`` when None.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").cover(400, 400).save("square.jpg")
        """
        up = allow_upscale if allow_upscale is not None else config.allow_upscale
        self._pipeline.add(
            "cover",
            resize_ops.cover(width, height, allow_upscale=up),
        )
        return self

    def contain(
        self,
        width: int,
        height: int,
        bg: str = "white",
        *,
        allow_upscale: bool | None = None,
    ) -> Image:
        """Queue a contain-fit resize, padding empty space.

        The image fits entirely inside the box; any letterboxing is
        filled with ``bg``. Aspect ratio is preserved.

        Args:
            width: Target width in pixels.
            height: Target height in pixels.
            bg: Background color for padding (any value accepted by
                ``PIL.ImageColor``).
            allow_upscale: Permit enlarging small images. Falls back to
                ``config.allow_upscale`` when None.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").contain(400, 400, bg="black").save("out.jpg")
        """
        up = allow_upscale if allow_upscale is not None else config.allow_upscale
        self._pipeline.add(
            "contain",
            resize_ops.contain(width, height, bg, allow_upscale=up),
        )
        return self

    # -- Crop operations --

    def crop(
        self,
        width: int,
        height: int,
        anchor: Anchor = "center",
    ) -> Image:
        """Queue a crop to the given dimensions at an anchor point.

        Args:
            width: Crop width in pixels.
            height: Crop height in pixels.
            anchor: Where to anchor the crop box — one of ``"center"``,
                ``"top"``, ``"bottom"``, ``"left"``, ``"right"``, or any
                corner such as ``"top-left"``.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").crop(500, 400, anchor="top-left").save("out.jpg")
        """
        self._pipeline.add("crop", crop_ops.crop(width, height, anchor))
        return self

    # -- Transform operations --

    def rotate(self, degrees: float, *, expand: bool = True, fill: str = "white") -> Image:
        """Queue a rotation by the given number of degrees counter-clockwise.

        Args:
            degrees: Rotation angle; positive values rotate
                counter-clockwise.
            expand: Enlarge the canvas so no pixels are clipped. Set to
                False to keep the original dimensions.
            fill: Color used to fill exposed corners when the canvas is
                expanded or rotation is not a multiple of 90°.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").rotate(45, fill="black").save("tilted.jpg")
        """
        self._pipeline.add("rotate", transform_ops.rotate(degrees, expand=expand, fill=fill))
        return self

    def flip(self) -> Image:
        """Queue a vertical flip (top-to-bottom).

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").flip().save("flipped.jpg")
        """
        self._pipeline.add("flip", transform_ops.flip())
        return self

    def mirror(self) -> Image:
        """Queue a horizontal flip (left-to-right).

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").mirror().save("mirrored.jpg")
        """
        self._pipeline.add("mirror", transform_ops.mirror())
        return self

    def grayscale(self) -> Image:
        """Queue a grayscale conversion.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").grayscale().save("gray.jpg")
        """
        self._pipeline.add("grayscale", transform_ops.grayscale())
        return self

    # -- Metadata operations --

    def strip_metadata(self) -> Image:
        """Queue removal of EXIF, IPTC, and XMP metadata from the output.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").strip_metadata().jpeg().save("clean.jpg")
        """
        self._pipeline.add("strip_metadata", metadata_ops.strip_metadata())
        return self

    def get_metadata(self) -> dict:
        """Return metadata from the original source image.

        Reads from the untransformed original — the pipeline is not run
        and any queued ``strip_metadata`` is ignored.

        Returns:
            Dict with ``width``, ``height``, ``mode``, ``format`` keys,
            plus ``exif`` when the source has EXIF data.

        Example:
            >>> Image("photo.jpg").get_metadata()["width"]
            1920
        """
        return metadata_ops.get_metadata(self._original)

    # -- Overlay operations --

    def watermark(
        self,
        source: str | Path | PILImage.Image,
        position: str = "bottom-right",
        opacity: float = 0.3,
        scale: float | None = None,
        margin: int = 10,
    ) -> Image:
        """Queue an image watermark overlay.

        Args:
            source: Path, ``Path``, or already-loaded Pillow image to
                place on top of the base image.
            position: Anchor such as ``"bottom-right"`` or the literal
                ``"tiled"`` for a repeating pattern.
            opacity: Blending opacity between 0.0 (invisible) and 1.0
                (opaque).
            scale: If set, resize the watermark so its width is this
                fraction of the base image width.
            margin: Distance in pixels from the anchored edge; ignored
                when ``position="tiled"``.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").watermark("logo.png", position="bottom-right").save("out.jpg")
        """
        self._pipeline.add(
            "watermark",
            overlay_ops.watermark(source, position, opacity, scale, margin),
        )
        return self

    def text_overlay(
        self,
        text: str,
        position: str = "bottom-right",
        font_path: str | None = None,
        font_size: int = 24,
        color: str | tuple = "white",
        opacity: float = 1.0,
        margin: int = 10,
    ) -> Image:
        """Queue a text overlay drawn on top of the image.

        Args:
            text: The text to render.
            position: Anchor such as ``"center"`` or ``"bottom-right"``.
            font_path: Path to a TrueType/OpenType font file. When None,
                Pillow's default bitmap font is used.
            font_size: Font size in pixels.
            color: Text color; any value accepted by ``PIL.ImageColor``
                or an ``(R, G, B[, A])`` tuple.
            opacity: Blending opacity between 0.0 and 1.0.
            margin: Distance in pixels from the anchored edge.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").text_overlay("Draft", font_size=48, color="red").save("out.jpg")
        """
        self._pipeline.add(
            "text_overlay",
            overlay_ops.text_overlay(
                text, position, font_path, font_size, color, opacity, margin,
            ),
        )
        return self

    # -- Adjustment operations --

    def brightness(self, factor: float) -> Image:
        """Queue a brightness adjustment.

        Args:
            factor: Multiplier where ``1.0`` is unchanged, values above
                1.0 brighten, and values below 1.0 darken.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").brightness(1.2).save("brighter.jpg")
        """
        self._pipeline.add("brightness", adjust_ops.brightness(factor))
        return self

    def contrast(self, factor: float) -> Image:
        """Queue a contrast adjustment.

        Args:
            factor: Multiplier where ``1.0`` is unchanged; higher values
                increase contrast, lower values flatten it.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").contrast(1.15).save("punchier.jpg")
        """
        self._pipeline.add("contrast", adjust_ops.contrast(factor))
        return self

    def saturation(self, factor: float) -> Image:
        """Queue a saturation adjustment.

        Args:
            factor: Multiplier where ``1.0`` is unchanged, ``0.0``
                produces grayscale, and larger values produce more
                vivid colors.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").saturation(1.3).save("vivid.jpg")
        """
        self._pipeline.add("saturation", adjust_ops.saturation(factor))
        return self

    def sharpen(self, factor: float = 2.0) -> Image:
        """Queue a sharpness adjustment.

        Args:
            factor: Multiplier where ``1.0`` is unchanged; higher values
                sharpen, lower values soften.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").sharpen(1.5).save("sharp.jpg")
        """
        self._pipeline.add("sharpen", adjust_ops.sharpen(factor))
        return self

    def blur(self, radius: float = 2.0) -> Image:
        """Queue a Gaussian blur.

        Args:
            radius: Blur radius in pixels; larger values blur more.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").blur(3.0).save("soft.jpg")
        """
        self._pipeline.add("blur", adjust_ops.blur(radius))
        return self

    # -- Effect operations --

    def sepia(self) -> Image:
        """Queue a sepia tone effect.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").sepia().save("vintage.jpg")
        """
        self._pipeline.add("sepia", effects_ops.sepia())
        return self

    def rounded_corners(self, radius: int) -> Image:
        """Queue rounded-corner masking, producing an alpha channel.

        Use a transparency-capable output format such as PNG or WebP.

        Args:
            radius: Corner radius in pixels.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").rounded_corners(20).png().save("rounded.png")
        """
        self._pipeline.add("rounded_corners", effects_ops.rounded_corners(radius))
        return self

    # -- Responsive images --

    def responsive(
        self,
        widths: list[int] | None = None,
        *,
        fmt: Format | None = None,
        quality: int | None = None,
        allow_upscale: bool = False,
    ) -> dict[int, bytes]:
        """Render the pipeline at multiple widths and return the encoded bytes.

        Executes the pipeline immediately. Widths above the original size
        are clamped when ``allow_upscale`` is False, which may collapse
        duplicate entries in the returned dict.

        Args:
            widths: Target widths in pixels. Defaults to
                ``[320, 640, 1024, 1920]``.
            fmt: Output format. Falls back to the format set via
                ``.jpeg()``/``.webp()``/... or the source format.
            quality: Encoder quality applied to every width.
            allow_upscale: Permit widths larger than the source width.

        Returns:
            Mapping of effective width to encoded bytes.

        Example:
            >>> data = Image("photo.jpg").responsive([400, 800, 1200])
            >>> sorted(data)
            [400, 800, 1200]
        """
        from .responsive import generate_responsive
        if widths is None:
            widths = [320, 640, 1024, 1920]
        out_fmt = fmt or self._output_format or self._source_format or Format.WEBP
        img = self._execute()
        return generate_responsive(
            img, widths, fmt=out_fmt, quality=quality or self._output_quality,
            allow_upscale=allow_upscale,
        )

    def save_responsive(
        self,
        output_dir: str | Path,
        widths: list[int] | None = None,
        name: str | None = None,
        *,
        fmt: Format | None = None,
        quality: int | None = None,
        allow_upscale: bool = False,
    ) -> dict[int, Path]:
        """Render the pipeline at multiple widths and save each to disk.

        Files are written as ``{name}_{width}.{ext}`` inside
        ``output_dir``, which is created if it does not exist.

        Args:
            output_dir: Destination directory for the generated files.
            widths: Target widths in pixels. Defaults to
                ``[320, 640, 1024, 1920]``.
            name: Filename prefix; defaults to the source filename stem,
                or ``"image"`` when the source is not a path.
            fmt: Output format. Falls back to the format set via
                ``.jpeg()``/``.webp()``/... or the source format.
            quality: Encoder quality applied uniformly.
            allow_upscale: Permit widths larger than the source width.

        Returns:
            Mapping of effective width to the saved ``Path``.

        Example:
            >>> Image("hero.jpg").save_responsive("static/", [400, 800, 1200])
        """
        from .responsive import save_responsive
        if widths is None:
            widths = [320, 640, 1024, 1920]
        out_fmt = fmt or self._output_format or self._source_format or Format.WEBP
        if name is None:
            name = Path(self._source_path).stem if self._source_path else "image"
        img = self._execute()
        return save_responsive(
            img, widths, output_dir, name,
            fmt=out_fmt, quality=quality or self._output_quality,
            allow_upscale=allow_upscale,
        )

    # -- Placeholders (execute immediately) --

    def lqip(self, width: int = 20) -> str:
        """Return a Low Quality Image Placeholder as a base64 data URI.

        Produces a tiny, inline-friendly data URI suitable for
        progressive image loading. Runs on the untransformed source.

        Args:
            width: Width in pixels of the placeholder (default 20).

        Returns:
            A ``data:image/webp;base64,...`` URI.

        Example:
            >>> uri = Image("photo.jpg").lqip()
            >>> uri.startswith("data:image/")
            True
        """
        from .placeholder import lqip
        return lqip(self._original, width)

    def dominant_color(self) -> str:
        """Return the dominant color of the image as a hex string.

        Returns:
            A lowercased ``#rrggbb`` color string.

        Example:
            >>> Image("photo.jpg").dominant_color()
            '#3a6b8c'
        """
        from .placeholder import dominant_color
        return dominant_color(self._original)

    def color_palette(self, count: int = 5) -> list[str]:
        """Return the top ``count`` colors as a list of hex strings.

        Args:
            count: Number of palette entries to return.

        Returns:
            List of ``#rrggbb`` strings ordered by prominence.

        Example:
            >>> Image("photo.jpg").color_palette(3)
            ['#3a6b8c', '#d4a574', '#1a1a1a']
        """
        from .placeholder import color_palette
        return color_palette(self._original, count)

    def svg_placeholder(self, width: int | None = None, height: int | None = None) -> str:
        """Return a tiny SVG placeholder filled with the dominant color.

        The SVG matches the source aspect ratio unless both ``width`` and
        ``height`` are supplied.

        Args:
            width: Optional SVG width attribute (defaults to the source
                width).
            height: Optional SVG height attribute (defaults to the source
                height).

        Returns:
            An inline SVG string.

        Example:
            >>> Image("photo.jpg").svg_placeholder(width=800, height=600)  # doctest: +ELLIPSIS
            '<svg ...'
        """
        from .placeholder import svg_placeholder
        return svg_placeholder(self._original, width, height)

    def blurhash(self, components_x: int = 4, components_y: int = 3) -> str:
        """Return a BlurHash string representing the source image.

        Requires the ``blur`` extra: ``pip install nitro-image[blur]``.

        Args:
            components_x: Number of horizontal BlurHash components (1-9).
            components_y: Number of vertical BlurHash components (1-9).

        Returns:
            A BlurHash string suitable for client-side decoding.

        Raises:
            ImportError: If ``blurhash-python`` is not installed.

        Example:
            >>> Image("photo.jpg").blurhash()  # doctest: +SKIP
            'LKO2:N%2Tw=w]~RBVZRi...'
        """
        from .placeholder import blurhash
        return blurhash(self._original, components_x, components_y)

    # -- Optimization --

    def optimize(self, target_kb: int, *, min_quality: int = 10, max_quality: int = 95) -> bytes:
        """Encode while binary-searching quality to hit a target file size.

        Runs the pipeline, then repeatedly encodes at different quality
        levels until the output is at or below ``target_kb`` kilobytes.

        Args:
            target_kb: Desired maximum output size in kilobytes.
            min_quality: Lowest quality to try before giving up.
            max_quality: Highest quality to try first.

        Returns:
            Encoded bytes, as close to ``target_kb`` as quality allows.

        Example:
            >>> data = Image("photo.jpg").resize(1200).optimize(target_kb=200)
            >>> len(data) <= 200 * 1024
            True
        """
        fmt = self._resolve_format()
        img = self._execute()
        data, _ = optimize_mod.optimize(
            img, fmt, target_kb, min_quality=min_quality, max_quality=max_quality,
        )
        return data

    def auto_format(self) -> Image:
        """Defer format choice until output time, picking the best fit.

        At output time the image is inspected: images with alpha prefer
        PNG, photographic images prefer the smaller of WebP and JPEG.
        The choice is remembered only for the current output call.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").auto_format().save("out.webp")
        """
        # Deferred — we resolve at output time
        self._auto_format = True
        return self

    # -- Format selection --

    def jpeg(self, quality: int | None = None) -> Image:
        """Select JPEG as the output format.

        Args:
            quality: Encoder quality (1-100). Falls back to
                ``config.default_jpeg_quality`` when None.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.png").jpeg(quality=90).save("photo.jpg")
        """
        self._output_format = Format.JPEG
        self._output_quality = quality
        return self

    def png(self) -> Image:
        """Select PNG as the output format.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").png().save("photo.png")
        """
        self._output_format = Format.PNG
        return self

    def webp(self, quality: int | None = None) -> Image:
        """Select WebP as the output format.

        Args:
            quality: Encoder quality (1-100). Falls back to
                ``config.default_webp_quality`` when None.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").webp(quality=80).save("photo.webp")
        """
        self._output_format = Format.WEBP
        self._output_quality = quality
        return self

    def gif(self) -> Image:
        """Select GIF as the output format.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.png").gif().save("photo.gif")
        """
        self._output_format = Format.GIF
        return self

    def format(self, fmt: Format | str, quality: int | None = None) -> Image:
        """Select an output format by enum or case-insensitive string.

        Args:
            fmt: Desired format, either a :class:`Format` member or a
                string such as ``"webp"``.
            quality: Encoder quality for formats that support it.

        Returns:
            The same ``Image`` for chaining.

        Example:
            >>> Image("photo.jpg").format("webp", quality=80).save("photo.webp")
        """
        if isinstance(fmt, str):
            fmt = Format(fmt.upper())
        self._output_format = fmt
        if quality is not None:
            self._output_quality = quality
        return self

    # -- Output methods (trigger pipeline execution) --

    def _resolve_format(self, path: str | Path | None = None) -> Format:
        if self._output_format is not None:
            return self._output_format
        if path is not None:
            fmt = format_from_extension(path)
            if fmt is not None:
                return fmt
        if self._source_format is not None:
            return self._source_format
        raise ImageFormatError(
            "Cannot determine output format. Call .jpeg(), .png(), .webp(), "
            "or save to a path with a recognized extension."
        )

    def _execute(self) -> PILImage.Image:
        return self._pipeline.execute(self._original.copy())

    def save(self, path: str | Path) -> Path:
        """Run the pipeline and write the result to disk.

        The output format is resolved from the explicit format method,
        then ``auto_format``, then the file extension, then the source
        format. Parent directories are created as needed.

        Args:
            path: Destination file path.

        Returns:
            The resolved destination ``Path``.

        Raises:
            ImageFormatError: If no format can be resolved.
            ImageOutputError: If the file cannot be written.

        Example:
            >>> Image("photo.jpg").resize(800).save("out/photo.webp")
        """
        img = self._execute()
        if self._auto_format and self._output_format is None:
            data, fmt = optimize_mod.auto_format(img, quality=self._output_quality)
            path = Path(path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            return path
        fmt = self._resolve_format(path)
        return export.save(img, path, fmt, quality=self._output_quality)

    def to_bytes(self) -> bytes:
        """Run the pipeline and return the encoded image bytes.

        Requires an output format set via ``.jpeg()``/``.png()``/...,
        ``.auto_format()``, or inherited from the source.

        Returns:
            Encoded image bytes.

        Raises:
            ImageFormatError: If no format can be resolved.

        Example:
            >>> data = Image("photo.jpg").resize(400).webp().to_bytes()
        """
        img = self._execute()
        if self._auto_format and self._output_format is None:
            data, _ = optimize_mod.auto_format(img, quality=self._output_quality)
            return data
        fmt = self._resolve_format()
        return export.to_bytes(img, fmt, quality=self._output_quality)

    def to_base64(self) -> str:
        """Run the pipeline and return a base64-encoded string.

        Returns:
            The encoded image as a base64 ASCII string (no data URI
            prefix).

        Raises:
            ImageFormatError: If no format can be resolved.

        Example:
            >>> Image("photo.jpg").resize(100).webp().to_base64()  # doctest: +ELLIPSIS
            'UklGR...'
        """
        img = self._execute()
        if self._auto_format and self._output_format is None:
            import base64
            data, _ = optimize_mod.auto_format(img, quality=self._output_quality)
            return base64.b64encode(data).decode("ascii")
        fmt = self._resolve_format()
        return export.to_base64(img, fmt, quality=self._output_quality)

    def to_data_uri(self) -> str:
        """Run the pipeline and return an inline data URI.

        Returns:
            A ``data:image/...;base64,...`` string suitable for embedding
            directly in HTML or CSS.

        Raises:
            ImageFormatError: If no format can be resolved.

        Example:
            >>> uri = Image("photo.jpg").thumbnail(200, 200).webp().to_data_uri()
            >>> uri.startswith("data:image/webp;base64,")
            True
        """
        img = self._execute()
        if self._auto_format and self._output_format is None:
            import base64 as b64mod
            from .utils import mime_type
            data, fmt = optimize_mod.auto_format(img, quality=self._output_quality)
            b64 = b64mod.b64encode(data).decode("ascii")
            return f"data:{mime_type(fmt)};base64,{b64}"
        fmt = self._resolve_format()
        return export.to_data_uri(img, fmt, quality=self._output_quality)

    def to_response(self) -> dict:
        """Run the pipeline and return a framework-agnostic response dict.

        Returns:
            Dict with ``body`` (bytes), ``content_type`` (str), and
            ``content_length`` (int) keys.

        Raises:
            ImageFormatError: If no format can be resolved.

        Example:
            >>> resp = Image("photo.jpg").resize(400).webp().to_response()
            >>> resp["content_type"]
            'image/webp'
        """
        img = self._execute()
        if self._auto_format and self._output_format is None:
            from .utils import mime_type
            data, fmt = optimize_mod.auto_format(img, quality=self._output_quality)
            return {
                "body": data,
                "content_type": mime_type(fmt),
                "content_length": len(data),
            }
        fmt = self._resolve_format()
        return export.to_response(img, fmt, quality=self._output_quality)

    # -- Framework integration responses --

    def to_django_response(self, *, filename: str | None = None) -> object:
        """Run the pipeline and return a Django ``HttpResponse``.

        Requires Django to be installed.

        Args:
            filename: Optional download filename; sets a
                ``Content-Disposition: inline`` header when provided.

        Returns:
            A ``django.http.HttpResponse`` instance.

        Raises:
            ImportError: If Django is not installed.
            ImageFormatError: If no format can be resolved.

        Example:
            >>> def view(request):  # doctest: +SKIP
            ...     return Image("photo.jpg").resize(400).webp().to_django_response()
        """
        from .integrations import to_django_response
        fmt = self._resolve_format()
        img = self._execute()
        return to_django_response(img, fmt, quality=self._output_quality, filename=filename)

    def to_flask_response(self, *, filename: str | None = None) -> object:
        """Run the pipeline and return a Flask ``Response``.

        Requires Flask to be installed.

        Args:
            filename: Optional download filename; sets a
                ``Content-Disposition: inline`` header when provided.

        Returns:
            A ``flask.Response`` instance.

        Raises:
            ImportError: If Flask is not installed.
            ImageFormatError: If no format can be resolved.

        Example:
            >>> @app.route("/thumb")  # doctest: +SKIP
            ... def thumb():
            ...     return Image("photo.jpg").resize(400).webp().to_flask_response()
        """
        from .integrations import to_flask_response
        fmt = self._resolve_format()
        img = self._execute()
        return to_flask_response(img, fmt, quality=self._output_quality, filename=filename)

    def to_fastapi_response(self, *, filename: str | None = None) -> object:
        """Run the pipeline and return a FastAPI/Starlette ``Response``.

        Requires Starlette (installed transitively with FastAPI).

        Args:
            filename: Optional download filename; sets a
                ``Content-Disposition: inline`` header when provided.

        Returns:
            A ``starlette.responses.Response`` instance.

        Raises:
            ImportError: If Starlette is not installed.
            ImageFormatError: If no format can be resolved.

        Example:
            >>> @app.get("/thumb")  # doctest: +SKIP
            ... async def thumb():
            ...     return Image("photo.jpg").resize(400).webp().to_fastapi_response()
        """
        from .integrations import to_fastapi_response
        fmt = self._resolve_format()
        img = self._execute()
        return to_fastapi_response(img, fmt, quality=self._output_quality, filename=filename)

    # -- Info --

    @property
    def width(self) -> int:
        """Width of the original source image in pixels.

        Reflects the untransformed source; queued pipeline operations do
        not affect this value.
        """
        return self._original.size[0]

    @property
    def height(self) -> int:
        """Height of the original source image in pixels.

        Reflects the untransformed source; queued pipeline operations do
        not affect this value.
        """
        return self._original.size[1]

    @property
    def size(self) -> tuple[int, int]:
        """Size of the original source image as ``(width, height)``.

        Reflects the untransformed source; queued pipeline operations do
        not affect this value.
        """
        return self._original.size

    @property
    def source_format(self) -> Format | None:
        """Detected format of the original source image, if known.

        Returns:
            The :class:`Format` decoded from the source, or None when the
            format could not be inferred (for example, raw bytes without
            a recognisable signature).
        """
        return self._source_format

    def __repr__(self) -> str:
        src = self._source_path or "bytes"
        return f"Image({src!r}, {self.width}x{self.height}, pipeline={self._pipeline})"
