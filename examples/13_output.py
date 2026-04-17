"""Output methods.

    .save(path)      write to disk, return a Path
    .to_bytes()      return raw encoded bytes
    .to_base64()     return a base64 string (no data-URI prefix)
    .to_data_uri()   return "data:image/<fmt>;base64,..." for inlining
    .to_response()   return a dict ready to hand to a web framework
"""

from __future__ import annotations

from nitro_img import Image

from _sample import banner, out, photo


def main() -> None:
    banner("13 - Output")
    src = photo()

    # save() returns the Path it wrote to.
    path = Image(src).resize(400).webp().save(out("13_save.webp"))
    print(f"save -> {path} ({path.stat().st_size} bytes)")

    # to_bytes() gives you raw encoded bytes (e.g. for streaming).
    data = Image(src).resize(400).webp().to_bytes()
    print(f"to_bytes: {len(data)} bytes, starts with {data[:4]!r}")

    # to_base64() / to_data_uri() for inline HTML.
    b64 = Image(src).resize(40).png().to_base64()
    print(f"to_base64: {b64[:60]}... ({len(b64)} chars)")

    uri = Image(src).resize(40).webp().to_data_uri()
    print(f"to_data_uri: {uri[:60]}...")

    # to_response() gives you the pieces a web framework needs.
    resp = Image(src).resize(400).webp().to_response()
    print(f"to_response: content_type={resp['content_type']}, "
          f"content_length={resp['content_length']}")


if __name__ == "__main__":
    main()
