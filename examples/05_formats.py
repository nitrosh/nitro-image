"""Format conversion and automatic format selection.

Resolution order for the output format:
    1. Explicit method: .jpeg() / .png() / .webp() / .gif() / .format(fmt)
    2. .auto_format() flag  (picks WebP/PNG based on content)
    3. The file extension passed to .save()
    4. The source image's format
"""

from __future__ import annotations

from nitro_img import Image, Format

from _sample import banner, out, photo


def main() -> None:
    banner("05 - Formats")
    src = photo()

    # Explicit format methods
    Image(src).resize(800).jpeg(quality=85).save(out("05_explicit.jpg"))
    Image(src).resize(800).png().save(out("05_explicit.png"))
    Image(src).resize(800).webp(quality=82).save(out("05_explicit.webp"))
    Image(src).resize(400).gif().save(out("05_explicit.gif"))

    # .format() accepts a Format enum or a string
    Image(src).resize(800).format("webp", quality=70).save(out("05_format_str.webp"))
    Image(src).resize(800).format(Format.JPEG, quality=70).save(out("05_format_enum.jpg"))

    # auto_format: let nitro pick what's best for the content.
    Image(src).resize(800).auto_format().save(out("05_auto.webp"))

    # With no explicit format, the save path's extension wins.
    Image(src).resize(800).save(out("05_by_extension.png"))

    print("Saved one file per format style")


if __name__ == "__main__":
    main()
