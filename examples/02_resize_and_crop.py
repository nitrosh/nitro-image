"""Resize modes and cropping.

- resize():    fit inside the given box, preserving aspect ratio
- thumbnail(): same as resize but never upscales by default
- cover():     fill the box, cropping the overflow (CSS background-size: cover)
- contain():   fit inside the box with padding (CSS background-size: contain)
- crop():      take an exact width x height from an anchor point
"""

from __future__ import annotations

from nitro_img import Image

from _sample import OUTPUT, banner, out, photo


def main() -> None:
    banner("02 - Resize and crop")
    src = photo()

    Image(src).resize(800).jpeg().save(out("02_resize_w800.jpg"))
    Image(src).resize(height=400).jpeg().save(out("02_resize_h400.jpg"))
    Image(src).resize(800, 800).jpeg().save(out("02_resize_fit_box.jpg"))

    # allow_upscale: by default we never enlarge.
    Image(src).resize(4000, allow_upscale=True).jpeg().save(out("02_upscaled.jpg"))

    Image(src).thumbnail(200, 200).jpeg().save(out("02_thumb.jpg"))

    # cover: fills the box, center-cropping overflow.
    Image(src).cover(500, 500).jpeg().save(out("02_cover_square.jpg"))

    # contain: fits inside the box, padded with a background color.
    Image(src).contain(500, 500, bg="black").jpeg().save(out("02_contain_square.jpg"))

    # crop: take an exact region. Anchor controls where the crop box sits.
    for anchor in ("center", "top-left", "bottom-right"):
        path = out(f"02_crop_{anchor}.jpg")
        Image(src).crop(400, 400, anchor=anchor).jpeg().save(path)
        print(f"Saved {path.name}")

    print(f"Output dir: {OUTPUT}")


if __name__ == "__main__":
    main()
