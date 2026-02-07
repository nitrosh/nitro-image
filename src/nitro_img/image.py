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

    Operations are queued and only executed when an output method
    (save, to_bytes, to_base64, to_data_uri, to_response) is called.
    """

    # Class-level preset accessor
    from .presets import Presets as _Presets
    preset = _Presets()

    def __init__(self, source: str | Path) -> None:
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
        img, fmt, _ = loaders.load_from_bytes(data)
        return cls._new_instance(img, fmt)

    @classmethod
    def from_file(cls, file_obj: IO[bytes]) -> Image:
        img, fmt, _ = loaders.load_from_file(file_obj)
        return cls._new_instance(img, fmt)

    @classmethod
    def from_base64(cls, b64_string: str) -> Image:
        img, fmt, _ = loaders.load_from_base64(b64_string)
        return cls._new_instance(img, fmt)

    @classmethod
    def from_url(cls, url: str) -> Image:
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
        self._pipeline.add("crop", crop_ops.crop(width, height, anchor))
        return self

    # -- Transform operations --

    def rotate(self, degrees: float, *, expand: bool = True, fill: str = "white") -> Image:
        self._pipeline.add("rotate", transform_ops.rotate(degrees, expand=expand, fill=fill))
        return self

    def flip(self) -> Image:
        self._pipeline.add("flip", transform_ops.flip())
        return self

    def mirror(self) -> Image:
        self._pipeline.add("mirror", transform_ops.mirror())
        return self

    def grayscale(self) -> Image:
        self._pipeline.add("grayscale", transform_ops.grayscale())
        return self

    # -- Metadata operations --

    def strip_metadata(self) -> Image:
        self._pipeline.add("strip_metadata", metadata_ops.strip_metadata())
        return self

    def get_metadata(self) -> dict:
        """Read metadata from the original image (executes immediately)."""
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
        self._pipeline.add(
            "text_overlay",
            overlay_ops.text_overlay(
                text, position, font_path, font_size, color, opacity, margin,
            ),
        )
        return self

    # -- Adjustment operations --

    def brightness(self, factor: float) -> Image:
        self._pipeline.add("brightness", adjust_ops.brightness(factor))
        return self

    def contrast(self, factor: float) -> Image:
        self._pipeline.add("contrast", adjust_ops.contrast(factor))
        return self

    def saturation(self, factor: float) -> Image:
        self._pipeline.add("saturation", adjust_ops.saturation(factor))
        return self

    def sharpen(self, factor: float = 2.0) -> Image:
        self._pipeline.add("sharpen", adjust_ops.sharpen(factor))
        return self

    def blur(self, radius: float = 2.0) -> Image:
        self._pipeline.add("blur", adjust_ops.blur(radius))
        return self

    # -- Effect operations --

    def sepia(self) -> Image:
        self._pipeline.add("sepia", effects_ops.sepia())
        return self

    def rounded_corners(self, radius: int) -> Image:
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
        """Generate multiple sizes and return {width: bytes}. Executes pipeline immediately."""
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
        """Generate multiple sizes and save to disk. Returns {width: Path}."""
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
        """Generate a Low Quality Image Placeholder as a base64 data URI."""
        from .placeholder import lqip
        return lqip(self._original, width)

    def dominant_color(self) -> str:
        """Extract the dominant color as a hex string."""
        from .placeholder import dominant_color
        return dominant_color(self._original)

    def color_palette(self, count: int = 5) -> list[str]:
        """Extract a color palette as a list of hex strings."""
        from .placeholder import color_palette
        return color_palette(self._original, count)

    def svg_placeholder(self, width: int | None = None, height: int | None = None) -> str:
        """Generate a lightweight SVG placeholder with the dominant color."""
        from .placeholder import svg_placeholder
        return svg_placeholder(self._original, width, height)

    def blurhash(self, components_x: int = 4, components_y: int = 3) -> str:
        """Generate a BlurHash string. Requires blurhash-python."""
        from .placeholder import blurhash
        return blurhash(self._original, components_x, components_y)

    # -- Optimization --

    def optimize(self, target_kb: int, *, min_quality: int = 10, max_quality: int = 95) -> bytes:
        """Auto-reduce quality to hit a target file size. Executes pipeline immediately."""
        fmt = self._resolve_format()
        img = self._execute()
        data, _ = optimize_mod.optimize(
            img, fmt, target_kb, min_quality=min_quality, max_quality=max_quality,
        )
        return data

    def auto_format(self) -> Image:
        """Pick the best format for the image content (WebP > JPEG for photos, PNG for alpha)."""
        # Deferred — we resolve at output time
        self._auto_format = True
        return self

    # -- Format selection --

    def jpeg(self, quality: int | None = None) -> Image:
        self._output_format = Format.JPEG
        self._output_quality = quality
        return self

    def png(self) -> Image:
        self._output_format = Format.PNG
        return self

    def webp(self, quality: int | None = None) -> Image:
        self._output_format = Format.WEBP
        self._output_quality = quality
        return self

    def gif(self) -> Image:
        self._output_format = Format.GIF
        return self

    def format(self, fmt: Format | str, quality: int | None = None) -> Image:
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
        img = self._execute()
        if self._auto_format and self._output_format is None:
            data, _ = optimize_mod.auto_format(img, quality=self._output_quality)
            return data
        fmt = self._resolve_format()
        return export.to_bytes(img, fmt, quality=self._output_quality)

    def to_base64(self) -> str:
        img = self._execute()
        if self._auto_format and self._output_format is None:
            import base64
            data, _ = optimize_mod.auto_format(img, quality=self._output_quality)
            return base64.b64encode(data).decode("ascii")
        fmt = self._resolve_format()
        return export.to_base64(img, fmt, quality=self._output_quality)

    def to_data_uri(self) -> str:
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
        """Return a Django HttpResponse. Requires Django."""
        from .integrations import to_django_response
        fmt = self._resolve_format()
        img = self._execute()
        return to_django_response(img, fmt, quality=self._output_quality, filename=filename)

    def to_flask_response(self, *, filename: str | None = None) -> object:
        """Return a Flask Response. Requires Flask."""
        from .integrations import to_flask_response
        fmt = self._resolve_format()
        img = self._execute()
        return to_flask_response(img, fmt, quality=self._output_quality, filename=filename)

    def to_fastapi_response(self, *, filename: str | None = None) -> object:
        """Return a FastAPI/Starlette Response. Requires FastAPI."""
        from .integrations import to_fastapi_response
        fmt = self._resolve_format()
        img = self._execute()
        return to_fastapi_response(img, fmt, quality=self._output_quality, filename=filename)

    # -- Info --

    @property
    def width(self) -> int:
        return self._original.size[0]

    @property
    def height(self) -> int:
        return self._original.size[1]

    @property
    def size(self) -> tuple[int, int]:
        return self._original.size

    @property
    def source_format(self) -> Format | None:
        return self._source_format

    def __repr__(self) -> str:
        src = self._source_path or "bytes"
        return f"Image({src!r}, {self.width}x{self.height}, pipeline={self._pipeline})"
