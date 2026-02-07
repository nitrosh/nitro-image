"""Tests for the core Image class and loading."""

from __future__ import annotations

import io

import pytest

from nitro_img import Image, ImageLoadError, ImageFormatError


class TestImageLoading:
    def test_load_from_path(self, sample_jpg):
        img = Image(str(sample_jpg))
        assert img.width == 800
        assert img.height == 600

    def test_load_from_path_object(self, sample_jpg):
        img = Image(sample_jpg)
        assert img.size == (800, 600)

    def test_load_from_bytes(self, sample_bytes):
        img = Image.from_bytes(sample_bytes)
        assert img.width == 200
        assert img.height == 150

    def test_load_from_file_object(self, sample_jpg):
        with open(sample_jpg, "rb") as f:
            img = Image.from_file(f)
        assert img.width == 800
        assert img.height == 600

    def test_load_from_base64(self, sample_base64):
        img = Image.from_base64(sample_base64)
        assert img.width == 200
        assert img.height == 150

    def test_load_from_base64_data_uri(self, sample_base64):
        uri = f"data:image/jpeg;base64,{sample_base64}"
        img = Image.from_base64(uri)
        assert img.width == 200

    def test_load_nonexistent_file(self):
        with pytest.raises(ImageLoadError, match="File not found"):
            Image("/nonexistent/path.jpg")

    def test_load_invalid_data(self):
        with pytest.raises(ImageLoadError):
            Image.from_bytes(b"not an image")


class TestImageFormats:
    def test_load_jpg(self, sample_jpg):
        img = Image(sample_jpg)
        assert img.source_format.value == "JPEG"

    def test_load_png(self, sample_png):
        img = Image(sample_png)
        assert img.source_format.value == "PNG"

    def test_load_webp(self, sample_webp):
        img = Image(sample_webp)
        assert img.source_format.value == "WEBP"


class TestImageRepr:
    def test_repr(self, sample_jpg):
        img = Image(sample_jpg)
        r = repr(img)
        assert "800x600" in r
        assert "Image(" in r


class TestOutputFormatResolution:
    def test_format_from_save_extension(self, sample_jpg, tmp_output):
        out = tmp_output / "out.webp"
        Image(sample_jpg).save(out)
        assert out.exists()

    def test_format_from_method(self, sample_jpg, tmp_output):
        out = tmp_output / "out.bin"
        Image(sample_jpg).jpeg().save(out)
        assert out.exists()

    def test_format_fallback_to_source(self, sample_jpg, tmp_output):
        # No extension, but source format (JPEG) is used as fallback
        out = tmp_output / "noext"
        Image(sample_jpg).save(out)
        assert out.exists()

    def test_format_error_no_hint(self, tmp_output):
        # Create raw image from PIL (no source format) + no extension + no format method
        from PIL import Image as PILImage
        from nitro_img.image import Image as NImage
        pil_img = PILImage.new("RGB", (10, 10), "red")
        buf = io.BytesIO()
        # Save without format info that Pillow would auto-detect
        pil_img.save(buf, "BMP")
        img = NImage.from_bytes(buf.getvalue())
        # Override source format to None to simulate truly unknown format
        img._source_format = None
        with pytest.raises(ImageFormatError):
            img.save(tmp_output / "noext")

    def test_falls_back_to_source_format(self, sample_jpg):
        data = Image(sample_jpg).to_bytes()
        assert len(data) > 0
