"""Placeholder techniques for progressive/blur-up image loading.

These run on the *original* image (they ignore the pipeline) and return
short strings you can inline in HTML / send to the browser before the
real image has finished loading.
"""

from __future__ import annotations

from nitro_img import Image

from _sample import banner, out, photo


def main() -> None:
    banner("08 - Placeholders")
    src = photo()
    img = Image(src)

    # LQIP: a tiny image encoded as a base64 data URI. Perfect for inlining
    # into <img src="..."> while the real image loads.
    lqip_uri = img.lqip(width=20)
    print(f"LQIP: {lqip_uri[:60]}... ({len(lqip_uri)} chars)")

    # Dominant color and a multi-color palette (good for theming / skeletons)
    print(f"Dominant color: {img.dominant_color()}")
    print(f"Palette (5):    {img.color_palette(5)}")

    # A lightweight SVG placeholder filled with the dominant color.
    svg = img.svg_placeholder(width=800, height=600)
    out("08_placeholder.svg").write_text(svg)
    print(f"SVG placeholder written ({len(svg)} chars)")

    # BlurHash is optional — install with `pip install nitro-image[blur]`
    try:
        bh = img.blurhash()
        print(f"BlurHash: {bh}")
    except ImportError:
        print("BlurHash skipped — install with: pip install nitro-image[blur]")


if __name__ == "__main__":
    main()
