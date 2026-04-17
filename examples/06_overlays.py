"""Watermarks and text overlays."""

from __future__ import annotations

from nitro_img import Image

from _sample import banner, logo, out, photo


def main() -> None:
    banner("06 - Overlays")
    src = photo()
    logo_path = logo(size=240)

    # Image watermark at the bottom-right corner, half opacity
    Image(src).watermark(
        logo_path, position="bottom-right", opacity=0.5, margin=20,
    ).jpeg().save(out("06_wm_corner.jpg"))

    # Tiled watermark (classic "preview" style)
    Image(src).watermark(
        logo_path, position="tiled", opacity=0.15,
    ).jpeg().save(out("06_wm_tiled.jpg"))

    # Scaled watermark (25% of image width)
    Image(src).watermark(
        logo_path, position="bottom-right", opacity=0.8, scale=0.25,
    ).jpeg().save(out("06_wm_scaled.jpg"))

    # Text overlay
    Image(src).text_overlay(
        "© Nitro Image",
        position="bottom-right",
        font_size=48,
        color="white",
        opacity=0.8,
        margin=24,
    ).jpeg().save(out("06_text.jpg"))

    # Watermark + text in the same pipeline
    (
        Image(src)
        .watermark(logo_path, position="top-left", opacity=0.6, scale=0.1)
        .text_overlay("Sample", position="bottom-left", font_size=32, color="yellow")
        .jpeg()
        .save(out("06_wm_plus_text.jpg"))
    )

    print("Saved overlay variations")


if __name__ == "__main__":
    main()
