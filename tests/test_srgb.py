"""Test SRGB library."""
import unittest
from colorcss import SRGB


class TestSRGBParse(unittest.TestCase):
    """Test SRGB."""

    def test_comma_comma(self):
        """Test comma format."""

        color = "rgb(30, 100, 200)"
        rgb = SRGB(color)
        self.assertEqual(color, rgb.to_css(comma=True))

        color = "rgb(30, 100, 200, 1)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_css(comma=True))

        color = "rgb(30, 100, 200, 0.2)"
        rgb = SRGB(color)
        self.assertEqual("rgba(30, 100, 200, 0.2)", rgb.to_css(comma=True))

    def test_space_space(self):
        """Test space format."""

        color = "rgb(30 100 200)"
        rgb = SRGB(color)
        self.assertEqual(color, rgb.to_css())

        color = "rgb(30 100 200 / 1)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_css())

        color = "rgb(30 100 200 / 0.2)"
        rgb = SRGB(color)
        self.assertEqual(color, rgb.to_css())

    def test_hex_hex(self):
        """Test hex input."""

        color = "#AA33DD"
        rgb = SRGB(color)
        self.assertEqual(color.lower(), rgb.to_css(hex_code=True))

        color = "#AA33DDFF"
        rgb = SRGB(color)
        self.assertEqual("#aa33dd", rgb.to_css(hex_code=True))

        color = "#AA33DD22"
        rgb = SRGB(color)
        self.assertEqual("#aa33dd22", rgb.to_css(hex_code=True))

    def test_hex_compressed(self):
        """Test hex input."""

        color = "#AA33DD"
        rgb = SRGB(color)
        self.assertEqual("#a3d", rgb.to_css(hex_code=True, compress=True))

        color = "#AA33DDFF"
        rgb = SRGB(color)
        self.assertEqual("#a3d", rgb.to_css(hex_code=True, compress=True))

        color = "#AA33DD22"
        rgb = SRGB(color)
        self.assertEqual("#a3d2", rgb.to_css(hex_code=True, compress=True, alpha=True))

    def test_alias(self):
        """Test that `rgba` is an alias for `rgb`."""

        color = "rgba(30, 100, 200)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_css(comma=True))

        color = "rgba(30, 100, 200, 1)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_css(comma=True))

        color = "rgba(30 100 200)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_css())

        color = "rgba(30 100 200 / 1)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_css())

    def test_percent(self):
        """Test that `rgba` is an alias for `rgb`."""

        color = "rgb(30%, 100%, 200%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77, 255, 255)", rgb.to_css(comma=True))

        color = "rgba(30%, 100%, 200%, 100%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77, 255, 255)", rgb.to_css(comma=True))

        color = "rgba(30%, 100%, 200%, 20%)"
        rgb = SRGB(color)
        self.assertEqual("rgba(77, 255, 255, 0.2)", rgb.to_css(comma=True))

        color = "rgb(30% 100% 200%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77 255 255)", rgb.to_css())

        color = "rgba(30% 100% 200% / 100%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77 255 255)", rgb.to_css())

        color = "rgba(30% 100% 200% / 20%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77 255 255 / 0.2)", rgb.to_css())

    def test_no_alpha(self):
        """Test no alpha."""

        color = "rgb(30, 100, 200, 0.2)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_css(comma=True, alpha=False))

        color = "rgb(30 100 200 / 0.2)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_css(alpha=False))

        color = "#AA33DD22"
        rgb = SRGB(color)
        self.assertEqual("#aa33dd", rgb.to_css(hex_code=True, alpha=False))

    def test_force_alpha(self):
        """Test force alpha."""

        color = "rgb(30, 100, 200, 100%)"
        rgb = SRGB(color)
        self.assertEqual("rgba(30, 100, 200, 1)", rgb.to_css(comma=True, alpha=True))

        color = "rgb(30 100 200 / 100%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200 / 1)", rgb.to_css(alpha=True))

        color = "#AA33DDFF"
        rgb = SRGB(color)
        self.assertEqual("#aa33ddff", rgb.to_css(hex_code=True, alpha=True))

    def test_name_name(self):
        """Test color names."""

        color = "rebeccapurple"
        rgb = SRGB(color)
        self.assertEqual("rebeccapurple", rgb.to_css(name=True))

        color = "#663399"
        rgb = SRGB(color)
        self.assertEqual("rebeccapurple", rgb.to_css(name=True))

        color = "#663399"
        rgb = SRGB(color)
        self.assertEqual("#663399", rgb.to_css(hex_code=True))

        color = "#663399"
        rgb = SRGB(color)
        self.assertEqual("rebeccapurple", rgb.to_css(hex_code=True, name=True))

        color = "#663399FF"
        rgb = SRGB(color)
        self.assertEqual("rebeccapurple", rgb.to_css(hex_code=True, alpha=True, name=True))

        color = "#66339922"
        rgb = SRGB(color)
        self.assertEqual("#66339922", rgb.to_css(hex_code=True, alpha=True, name=True))
