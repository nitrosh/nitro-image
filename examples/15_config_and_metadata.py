"""Global config and image metadata (EXIF etc.)."""

from __future__ import annotations

from nitro_img import Image, config

from _sample import banner, out, photo


def main() -> None:
    banner("15 - Config and metadata")
    src = photo()

    # Global defaults — use config.update() to change them.
    # Known keys (see Config dataclass): default_jpeg_quality, default_webp_quality,
    # default_png_compression, allow_upscale, auto_orient, strip_metadata,
    # max_input_size, max_output_dimensions, url_timeout, url_max_size.
    config.update(
        default_jpeg_quality=90,
        default_webp_quality=85,
        allow_upscale=False,
        auto_orient=True,
    )
    print(
        f"config.default_jpeg_quality={config.default_jpeg_quality}, "
        f"config.default_webp_quality={config.default_webp_quality}"
    )

    # Read metadata (dimensions, mode, format, EXIF tags) without running the pipeline.
    meta = Image(src).get_metadata()
    summary = {k: v for k, v in meta.items() if k != "exif"}
    exif_count = len(meta.get("exif", {}))
    print(f"Metadata: {summary}, exif_tags={exif_count}")

    # strip_metadata() drops EXIF/IPTC/XMP inside the pipeline.
    (
        Image(src)
        .strip_metadata()
        .resize(800)
        .jpeg()
        .save(out("15_stripped.jpg"))
    )

    # Image exposes width, height, size, and source_format as simple properties.
    img = Image(src)
    print(f"width={img.width}, height={img.height}, source_format={img.source_format}")


if __name__ == "__main__":
    main()
