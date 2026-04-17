"""Quickstart: load an image, run a pipeline, save the result.

Every chainable method queues a deferred operation; the pipeline only runs
when you call an output method like .save() or .to_bytes().
"""

from __future__ import annotations

from nitro_img import Image

from _sample import banner, out, photo


def main() -> None:
    banner("01 - Basics")
    src = photo()

    # One-liner: resize, encode as WebP, save.
    result = Image(src).resize(800).webp(quality=80).save(out("01_resized.webp"))
    print(f"Saved {result} ({result.stat().st_size // 1024} KB)")

    # Same idea, but a longer chain. Nothing runs until .save().
    result = (
        Image(src)
        .resize(1024)
        .brightness(1.1)
        .contrast(1.05)
        .sharpen(1.2)
        .webp(quality=85)
        .save(out("01_enhanced.webp"))
    )
    print(f"Saved {result}")

    # Inspect the image without executing the pipeline.
    img = Image(src)
    print(f"Source: {img.width}x{img.height}, format={img.source_format}")


if __name__ == "__main__":
    main()
