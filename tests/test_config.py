"""Tests for the global config singleton and its enforcement."""

from __future__ import annotations

import pytest
from PIL import Image as PILImage

from nitro_img import Image, ImageSizeError, config


@pytest.fixture(autouse=True)
def restore_config():
    snapshot = {
        "max_input_size": config.max_input_size,
        "max_pixels": config.max_pixels,
        "max_output_dimensions": config.max_output_dimensions,
        "strip_metadata": config.strip_metadata,
        "auto_orient": config.auto_orient,
        "url_allowed_schemes": config.url_allowed_schemes,
        "url_max_size": config.url_max_size,
    }
    yield
    for key, value in snapshot.items():
        setattr(config, key, value)


class TestConfigUpdate:
    def test_update_known_field(self):
        config.update(default_jpeg_quality=99)
        assert config.default_jpeg_quality == 99
        config.update(default_jpeg_quality=85)

    def test_update_unknown_field_raises(self):
        with pytest.raises(ValueError, match="Unknown config option"):
            config.update(does_not_exist=True)

    def test_update_multiple_fields(self):
        config.update(default_jpeg_quality=70, default_webp_quality=70)
        assert config.default_jpeg_quality == 70
        assert config.default_webp_quality == 70


class TestMaxPixels:
    def test_load_above_max_pixels_raises(self, sample_jpg):
        config.update(max_pixels=100)  # 800x600 = 480_000 — well over 100
        with pytest.raises(ImageSizeError, match="pixels"):
            Image(sample_jpg)

    def test_load_below_max_pixels_succeeds(self, sample_jpg):
        config.update(max_pixels=10_000_000)
        img = Image(sample_jpg)
        assert img.width == 800


class TestMaxOutputDimensions:
    def test_resize_above_cap_raises(self, sample_jpg):
        config.update(max_output_dimensions=400)
        with pytest.raises(ImageSizeError, match="max_output_dimensions"):
            Image(sample_jpg).resize(800, allow_upscale=True).to_bytes()

    def test_cover_above_cap_raises(self, sample_jpg):
        config.update(max_output_dimensions=200)
        with pytest.raises(ImageSizeError, match="max_output_dimensions"):
            Image(sample_jpg).cover(400, 400).to_bytes()

    def test_contain_above_cap_raises(self, sample_jpg):
        config.update(max_output_dimensions=200)
        with pytest.raises(ImageSizeError, match="max_output_dimensions"):
            Image(sample_jpg).contain(400, 400).to_bytes()

    def test_thumbnail_above_cap_raises(self, sample_jpg):
        config.update(max_output_dimensions=100)
        # thumbnail only runs when the image exceeds the box, so allow upscale path
        with pytest.raises(ImageSizeError):
            Image(sample_jpg).thumbnail(400, 400, allow_upscale=True).to_bytes()

    def test_within_cap_succeeds(self, sample_jpg):
        config.update(max_output_dimensions=2000)
        Image(sample_jpg).resize(400).webp().to_bytes()


class TestStripMetadataConfig:
    def test_strip_on_load_removes_exif(self, tmp_path):
        path = tmp_path / "withexif.jpg"
        pil = PILImage.new("RGB", (50, 50), (10, 20, 30))
        exif = pil.getexif()
        exif[0x0112] = 6  # Orientation tag with rotation
        pil.save(path, "JPEG", exif=exif)

        config.update(strip_metadata=True, auto_orient=False)
        img = Image(path)
        meta = img.get_metadata()
        # After stripping, EXIF should be empty or absent
        assert not meta.get("exif")

    def test_no_strip_when_disabled(self, tmp_path):
        path = tmp_path / "withexif.jpg"
        pil = PILImage.new("RGB", (50, 50), (10, 20, 30))
        exif = pil.getexif()
        exif[0x010E] = "test caption"  # ImageDescription tag
        pil.save(path, "JPEG", exif=exif)

        config.update(strip_metadata=False, auto_orient=False)
        img = Image(path)
        meta = img.get_metadata()
        assert meta.get("exif")


class TestAutoOrient:
    def _save_oriented(self, path, orientation: int) -> None:
        # Build a tall image with distinct top/bottom colors so orientation
        # transforms are detectable.
        pil = PILImage.new("RGB", (40, 60), (255, 0, 0))
        # Draw a blue strip at the bottom 1/3 so transforms move it predictably.
        bottom = PILImage.new("RGB", (40, 20), (0, 0, 255))
        pil.paste(bottom, (0, 40))
        exif = pil.getexif()
        exif[0x0112] = orientation
        pil.save(path, "JPEG", exif=exif)

    def test_auto_orient_applies_rotation(self, tmp_path):
        path = tmp_path / "rot.jpg"
        self._save_oriented(path, orientation=6)  # 90° CW
        config.update(auto_orient=True)
        img = Image(path)
        # Orientation 6 swaps width/height (60x40 after rotation)
        assert img.width == 60
        assert img.height == 40

    def test_auto_orient_disabled_keeps_raw_dims(self, tmp_path):
        path = tmp_path / "rot.jpg"
        self._save_oriented(path, orientation=6)
        config.update(auto_orient=False)
        img = Image(path)
        assert img.width == 40
        assert img.height == 60

    def test_auto_orient_no_exif_is_safe(self, sample_jpg):
        config.update(auto_orient=True)
        img = Image(sample_jpg)
        assert img.width == 800


class TestMaxInputSize:
    def test_oversized_path_raises(self, sample_jpg):
        config.update(max_input_size=10)
        with pytest.raises(ImageSizeError, match="File size"):
            Image(sample_jpg)

    def test_oversized_bytes_raises(self, sample_bytes):
        config.update(max_input_size=10)
        with pytest.raises(ImageSizeError, match="Input size"):
            Image.from_bytes(sample_bytes)


class TestUrlSchemeAllowlist:
    def test_disallowed_scheme_raises(self):
        with pytest.raises(Exception) as exc:
            Image.from_url("file:///etc/passwd")
        # Either an ImportError (httpx missing) or ImageLoadError (scheme rejected).
        msg = str(exc.value).lower()
        assert "scheme" in msg or "httpx" in msg

    def test_default_allowed_schemes(self):
        assert "http" in config.url_allowed_schemes
        assert "https" in config.url_allowed_schemes
        assert "file" not in config.url_allowed_schemes
