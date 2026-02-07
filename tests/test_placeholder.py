"""Tests for placeholder generation."""

from __future__ import annotations


from nitro_img import Image


class TestLQIP:
    def test_lqip_returns_data_uri(self, sample_jpg):
        uri = Image(sample_jpg).lqip()
        assert uri.startswith("data:image/webp;base64,")
        assert len(uri) > 30

    def test_lqip_custom_width(self, sample_jpg):
        uri = Image(sample_jpg).lqip(width=10)
        assert uri.startswith("data:image/webp;base64,")

    def test_lqip_is_small(self, sample_jpg):
        uri = Image(sample_jpg).lqip(width=20)
        # Data URI for a 20px wide image should be quite small
        assert len(uri) < 5000


class TestDominantColor:
    def test_dominant_color_is_hex(self, sample_jpg):
        color = Image(sample_jpg).dominant_color()
        assert color.startswith("#")
        assert len(color) == 7
        # Should be valid hex
        int(color[1:], 16)

    def test_dominant_color_red_image(self, fixtures_dir):
        from PIL import Image as PILImage
        path = fixtures_dir / "red.jpg"
        PILImage.new("RGB", (100, 100), (255, 0, 0)).save(path)
        color = Image(path).dominant_color()
        # Should be close to red — quantized to nearest 16
        assert color == "#f00000"


class TestColorPalette:
    def test_palette_count(self, sample_jpg):
        palette = Image(sample_jpg).color_palette(count=3)
        assert isinstance(palette, list)
        assert len(palette) <= 3
        for color in palette:
            assert color.startswith("#")

    def test_palette_default(self, sample_jpg):
        palette = Image(sample_jpg).color_palette()
        assert len(palette) <= 5


class TestSVGPlaceholder:
    def test_svg_placeholder(self, sample_jpg):
        svg = Image(sample_jpg).svg_placeholder()
        assert svg.startswith("<svg")
        assert 'width="800"' in svg
        assert 'height="600"' in svg
        assert "fill=" in svg

    def test_svg_placeholder_custom_dimensions(self, sample_jpg):
        svg = Image(sample_jpg).svg_placeholder(width=400, height=300)
        assert 'width="400"' in svg
        assert 'height="300"' in svg
