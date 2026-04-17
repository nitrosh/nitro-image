"""Responsive image sets for <img srcset>.

- .responsive(widths)        returns {width: bytes} in memory
- .save_responsive(...)      writes {name}_{width}.{ext} files

Both run the pipeline once and then generate each size from the result.
"""

from __future__ import annotations

from nitro_img import Image

from _sample import banner, out, photo


def main() -> None:
    banner("07 - Responsive")
    src = photo()

    # In-memory set
    sizes = Image(src).responsive([400, 800, 1200, 1600])
    for width, data in sorted(sizes.items()):
        print(f"  {width}px -> {len(data) // 1024} KB")

    # Save a set to disk. Output format is taken from the chained format call.
    paths = (
        Image(src)
        .webp(quality=80)
        .save_responsive(out("srcset"), [400, 800, 1200, 1600], name="hero")
    )
    for width, path in sorted(paths.items()):
        print(f"  {path.name}")

    # Build an <img srcset="..."> string from the result
    srcset = ", ".join(f"{path.name} {width}w" for width, path in sorted(paths.items()))
    print(f"\nsrcset: {srcset}")


if __name__ == "__main__":
    main()
