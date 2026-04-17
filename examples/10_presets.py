"""Presets: opinionated one-call helpers.

Presets are static methods that accept a source (path / bytes / file-like)
and return encoded bytes directly. Use them when you don't need to build a
custom pipeline.
"""

from __future__ import annotations

from nitro_img import Image, presets

from _sample import banner, out, photo


def main() -> None:
    banner("10 - Presets")
    src = photo()

    # All presets take a source and return bytes.
    out("10_thumbnail.webp").write_bytes(presets.thumbnail(str(src)))
    out("10_avatar.png").write_bytes(presets.avatar(str(src), size=128))
    out("10_og_image.jpg").write_bytes(presets.og_image(str(src)))
    out("10_banner.jpg").write_bytes(presets.banner(str(src)))

    # avatar_placeholder: generate an initials avatar from scratch — no source.
    out("10_initials.png").write_bytes(
        presets.avatar_placeholder("SN", size=256, bg="#4A90D9", text_color="white"),
    )

    # The Presets class is also reachable via Image.preset for convenience.
    out("10_via_class.webp").write_bytes(Image.preset.thumbnail(str(src)))

    # The responsive preset loads, strips metadata, and writes a full set.
    paths = presets.responsive(
        str(src),
        widths=[320, 640, 1024],
        output_dir=out("10_responsive"),
        name="img",
    )
    print(f"Responsive preset wrote: {[p.name for p in paths.values()]}")


if __name__ == "__main__":
    main()
