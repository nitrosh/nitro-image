"""Tests for the presets system."""

from __future__ import annotations

from nitro_img import Image, presets, Format


class TestThumbnailPreset:
    def test_thumbnail_default(self, sample_jpg):
        data = presets.thumbnail(str(sample_jpg))
        assert isinstance(data, bytes)
        assert len(data) > 0
        result = Image.from_bytes(data)
        assert result.width <= 200
        assert result.height <= 200

    def test_thumbnail_custom_size(self, sample_jpg):
        data = presets.thumbnail(str(sample_jpg), width=100, height=100)
        result = Image.from_bytes(data)
        assert result.width <= 100
        assert result.height <= 100

    def test_thumbnail_jpeg_format(self, sample_jpg):
        data = presets.thumbnail(str(sample_jpg), fmt=Format.JPEG)
        assert data[:2] == b"\xff\xd8"

    def test_preset_via_class(self, sample_jpg):
        data = Image.preset.thumbnail(str(sample_jpg))
        assert len(data) > 0


class TestAvatarPreset:
    def test_avatar(self, sample_jpg):
        data = presets.avatar(str(sample_jpg), size=64)
        result = Image.from_bytes(data)
        assert result.width == 64
        assert result.height == 64

    def test_avatar_default_size(self, sample_jpg):
        data = presets.avatar(str(sample_jpg))
        result = Image.from_bytes(data)
        assert result.width == 128
        assert result.height == 128

    def test_avatar_is_png_by_default(self, sample_jpg):
        data = presets.avatar(str(sample_jpg))
        assert data[:4] == b"\x89PNG"

    def test_avatar_from_bytes(self, sample_bytes):
        data = presets.avatar(sample_bytes, size=64)
        result = Image.from_bytes(data)
        assert result.width == 64


class TestAvatarPlaceholder:
    def test_avatar_placeholder(self):
        data = presets.avatar_placeholder("SL", size=64)
        assert isinstance(data, bytes)
        result = Image.from_bytes(data)
        assert result.width == 64
        assert result.height == 64

    def test_avatar_placeholder_custom_colors(self):
        data = presets.avatar_placeholder(
            "AB", size=128, bg="#FF5500", text_color="black"
        )
        assert len(data) > 0


class TestOGImagePreset:
    def test_og_image(self, sample_jpg):
        data = presets.og_image(str(sample_jpg))
        result = Image.from_bytes(data)
        assert result.width == 1200
        assert result.height == 630

    def test_og_image_is_jpeg(self, sample_jpg):
        data = presets.og_image(str(sample_jpg))
        assert data[:2] == b"\xff\xd8"


class TestBannerPreset:
    def test_banner(self, sample_jpg):
        data = presets.banner(str(sample_jpg))
        result = Image.from_bytes(data)
        assert result.width == 1920
        assert result.height == 400

    def test_banner_custom_size(self, sample_jpg):
        data = presets.banner(str(sample_jpg), width=1280, height=300)
        result = Image.from_bytes(data)
        assert result.width == 1280
        assert result.height == 300


class TestResponsivePreset:
    def test_responsive_preset(self, sample_jpg, tmp_output):
        paths = presets.responsive(
            str(sample_jpg),
            widths=[200, 400],
            output_dir=tmp_output,
            name="test",
        )
        assert len(paths) == 2
        for width, path in paths.items():
            assert path.exists()
            assert path.suffix == ".webp"

    def test_responsive_preset_defaults(self, sample_jpg, tmp_output):
        paths = presets.responsive(str(sample_jpg), output_dir=tmp_output)
        assert len(paths) >= 2  # Some sizes capped by image size
