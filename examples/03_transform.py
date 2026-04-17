"""Geometric transforms: rotate, flip, mirror, grayscale."""

from __future__ import annotations

from nitro_img import Image

from _sample import banner, out, photo


def main() -> None:
    banner("03 - Transforms")
    src = photo()

    Image(src).rotate(45).jpeg().save(out("03_rotate_45.jpg"))
    Image(src).rotate(90, expand=True).jpeg().save(out("03_rotate_90.jpg"))
    Image(src).rotate(15, expand=False, fill="#222").jpeg().save(out("03_rotate_fill.jpg"))

    Image(src).flip().jpeg().save(out("03_flip.jpg"))       # vertical flip
    Image(src).mirror().jpeg().save(out("03_mirror.jpg"))   # horizontal mirror

    Image(src).grayscale().jpeg().save(out("03_grayscale.jpg"))

    print("Saved rotate, flip, mirror, grayscale outputs")


if __name__ == "__main__":
    main()
