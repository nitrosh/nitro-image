"""Loading images from different sources.

    Image(path)            file path
    Image.from_bytes(...)  raw bytes (from a request body, etc.)
    Image.from_base64(...) base64 string
    Image.from_file(f)     any file-like object (io.BytesIO, uploaded file, ...)
    Image.from_url(url)    HTTP(S) URL (requires the [url] extra: httpx)
"""

from __future__ import annotations

import base64
import io

from nitro_img import Image

from _sample import banner, out, photo


def main() -> None:
    banner("12 - Loading")
    src = photo()

    # From path (the default constructor).
    Image(src).resize(400).jpeg().save(out("12_from_path.jpg"))

    # From raw bytes.
    raw = src.read_bytes()
    Image.from_bytes(raw).resize(400).jpeg().save(out("12_from_bytes.jpg"))

    # From base64.
    b64 = base64.b64encode(raw).decode("ascii")
    Image.from_base64(b64).resize(400).jpeg().save(out("12_from_base64.jpg"))

    # From any file-like object (e.g. Flask's request.files["upload"]).
    with io.BytesIO(raw) as stream:
        Image.from_file(stream).resize(400).jpeg().save(out("12_from_file.jpg"))

    # From URL — requires `pip install nitro-image[url]`.
    try:
        Image.from_url("https://picsum.photos/400/300")\
             .resize(400)\
             .jpeg()\
             .save(out("12_from_url.jpg"))
        print("Loaded from URL")
    except Exception as exc:  # broad: networks fail, extras may be missing
        print(f"Skipping URL load: {exc}")

    print("Loaded from path, bytes, base64, file-like")


if __name__ == "__main__":
    main()
