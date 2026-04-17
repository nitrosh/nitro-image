"""Tonal adjustments and creative effects.

Adjustments use a multiplicative factor (1.0 = unchanged). Blur radius and
sharpen factor are absolute. Effects like sepia and rounded_corners are
boolean on/off — just call them.
"""

from __future__ import annotations

from nitro_img import Image

from _sample import banner, out, photo


def main() -> None:
    banner("04 - Adjustments and effects")
    src = photo()

    # Tonal adjustments (factor: 1.0 = no change)
    Image(src).brightness(1.3).jpeg().save(out("04_brighter.jpg"))
    Image(src).brightness(0.7).jpeg().save(out("04_darker.jpg"))
    Image(src).contrast(1.4).jpeg().save(out("04_contrast.jpg"))
    Image(src).saturation(1.6).jpeg().save(out("04_saturated.jpg"))
    Image(src).saturation(0.0).jpeg().save(out("04_desaturated.jpg"))  # == grayscale

    # Sharpness and blur
    Image(src).sharpen(2.0).jpeg().save(out("04_sharpened.jpg"))
    Image(src).blur(4.0).jpeg().save(out("04_blurred.jpg"))

    # Effects
    Image(src).sepia().jpeg().save(out("04_sepia.jpg"))
    Image(src).rounded_corners(40).png().save(out("04_rounded.png"))  # PNG for alpha

    # Combined
    (
        Image(src)
        .resize(800)
        .brightness(1.1)
        .contrast(1.1)
        .saturation(1.2)
        .sharpen(1.3)
        .jpeg(quality=88)
        .save(out("04_combined.jpg"))
    )

    print("Saved adjustment + effect variations")


if __name__ == "__main__":
    main()
