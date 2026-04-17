# Examples

Runnable examples covering every feature of Nitro Image. Each file is
self-contained — pick any one and run it directly:

```bash
pip install -e .            # from the repo root
python examples/01_basics.py
```

Sample inputs are generated on first run under `examples/samples/` and
outputs land in `examples/output/`. Both directories are gitignored.

## Index

| File                           | What it demonstrates                                      |
|--------------------------------|-----------------------------------------------------------|
| `01_basics.py`                 | Load, chain, save — the quickstart                        |
| `02_resize_and_crop.py`        | `resize`, `thumbnail`, `cover`, `contain`, `crop`         |
| `03_transform.py`              | `rotate`, `flip`, `mirror`, `grayscale`                   |
| `04_adjust_and_effects.py`     | Brightness, contrast, saturation, sharpen, blur, sepia, rounded corners |
| `05_formats.py`                | JPEG/PNG/WebP/GIF, `.format()`, `.auto_format()`          |
| `06_overlays.py`               | Image watermarks and text overlays                        |
| `07_responsive.py`             | `responsive()` and `save_responsive()` for `<img srcset>` |
| `08_placeholders.py`           | LQIP, dominant color, palette, SVG placeholder, BlurHash  |
| `09_optimize.py`               | Target-size optimization via quality search               |
| `10_presets.py`                | `thumbnail`, `avatar`, `og_image`, `banner`, `avatar_placeholder`, responsive preset |
| `11_batch.py`                  | `BatchImage` with `{name}` patterns, sequential + parallel |
| `12_loading.py`                | Load from path, bytes, base64, file-like, URL             |
| `13_output.py`                 | `save`, `to_bytes`, `to_base64`, `to_data_uri`, `to_response` |
| `14_integrations.py`           | Django / Flask / FastAPI response helpers                 |
| `15_config_and_metadata.py`    | Global `config.update()`, `get_metadata()`, `strip_metadata()` |

## Optional extras

A couple of examples need the optional dependencies:

```bash
pip install nitro-image[url]   # for from_url (12_loading.py)
pip install nitro-image[blur]  # for blurhash() (08_placeholders.py)
pip install nitro-image[avif]  # for AVIF output
pip install nitro-image[all]   # everything above
```

Examples gracefully skip features that aren't installed — you'll see a
"skipped" message in the output.

## Run them all

```bash
for f in examples/[0-9]*.py; do python "$f"; done
```
