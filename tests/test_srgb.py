"""Test SRGB library."""
import unittest
from coloraide.css import SRGB


class TestSRGBParse(unittest.TestCase):
    """Test SRGB."""

    def test_comma_comma(self):
        """Test comma format."""

        args = {"comma": True, "precision": 0}

        color = "rgb(30, 100, 200)"
        rgb = SRGB(color)
        self.assertEqual(color, rgb.to_string(**args))

        color = "rgb(30, 100, 200, 1)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_string(**args))

        color = "rgb(30, 100, 200, 0.2)"
        rgb = SRGB(color)
        self.assertEqual("rgba(30, 100, 200, 0.2)", rgb.to_string(**args))

    def test_space_space(self):
        """Test space format."""

        args = {"precision": 0}

        color = "rgb(30 100 200)"
        rgb = SRGB(color)
        self.assertEqual(color, rgb.to_string(**args))

        color = "rgb(30 100 200 / 1)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_string(**args))

        color = "rgb(30 100 200 / 0.2)"
        rgb = SRGB(color)
        self.assertEqual(color, rgb.to_string(**args))

    def test_hex_hex(self):
        """Test hex input."""

        args = {"hex_code": True}

        color = "#AA33DD"
        rgb = SRGB(color)
        self.assertEqual(color.lower(), rgb.to_string(**args))

        color = "#AA33DDFF"
        rgb = SRGB(color)
        self.assertEqual("#aa33dd", rgb.to_string(**args))

        color = "#AA33DD22"
        rgb = SRGB(color)
        self.assertEqual("#aa33dd22", rgb.to_string(**args))

    def test_hex_compressed(self):
        """Test hex input."""

        args = {"hex_code": True, "compress": True}

        color = "#AA33DD"
        rgb = SRGB(color)
        self.assertEqual("#a3d", rgb.to_string(**args))

        color = "#AA33DDFF"
        rgb = SRGB(color)
        self.assertEqual("#a3d", rgb.to_string(**args))

        args["alpha"] = True

        color = "#AA33DD22"
        rgb = SRGB(color)
        self.assertEqual("#a3d2", rgb.to_string(**args))

    def test_alias(self):
        """Test that `rgba` is an alias for `rgb`."""

        args = {"comma": True, "precision": 0}

        color = "rgba(30, 100, 200)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_string(**args))

        color = "rgba(30, 100, 200, 1)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_string(**args))

        args["comma"] = False

        color = "rgba(30 100 200)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_string(**args))

        color = "rgba(30 100 200 / 1)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_string(**args))

    def test_percent(self):
        """Test that `rgba` is an alias for `rgb`."""

        args = {"comma": True, "precision": 0}

        color = "rgb(30%, 100%, 200%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77, 255, 255)", rgb.to_string(**args))

        color = "rgba(30%, 100%, 200%, 100%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77, 255, 255)", rgb.to_string(**args))

        color = "rgba(30%, 100%, 200%, 20%)"
        rgb = SRGB(color)
        self.assertEqual("rgba(77, 255, 255, 0.2)", rgb.to_string(**args))

        args["comma"] = False

        color = "rgb(30% 100% 200%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77 255 255)", rgb.to_string(**args))

        color = "rgba(30% 100% 200% / 100%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77 255 255)", rgb.to_string(**args))

        color = "rgba(30% 100% 200% / 20%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(77 255 255 / 0.2)", rgb.to_string(**args))

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"comma": True, "precision": 0, "alpha": False}

        color = "rgb(30, 100, 200, 0.2)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_string(**args))

        args["comma"] = False

        color = "rgb(30 100 200 / 0.2)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_string(**args))

        args["hex_code"] = True

        color = "#AA33DD22"
        rgb = SRGB(color)
        self.assertEqual("#aa33dd", rgb.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"comma": True, "precision": 0, "alpha": True}

        color = "rgb(30, 100, 200, 100%)"
        rgb = SRGB(color)
        self.assertEqual("rgba(30, 100, 200, 1)", rgb.to_string(**args))

        args["comma"] = False

        color = "rgb(30 100 200 / 100%)"
        rgb = SRGB(color)
        self.assertEqual("rgb(30 100 200 / 1)", rgb.to_string(**args))

        args["hex_code"] = True

        color = "#AA33DDFF"
        rgb = SRGB(color)
        self.assertEqual("#aa33ddff", rgb.to_string(**args))

    def test_name_name(self):
        """Test color names."""

        args = {"name": True}

        color = "rebeccapurple"
        rgb = SRGB(color)
        self.assertEqual("rebeccapurple", rgb.to_string(**args))

        color = "#663399"
        rgb = SRGB(color)
        self.assertEqual("rebeccapurple", rgb.to_string(**args))

        args["hex_code"] = True
        args["name"] = False

        color = "#663399"
        rgb = SRGB(color)
        self.assertEqual("#663399", rgb.to_string(**args))

        args["name"] = True

        color = "#663399"
        rgb = SRGB(color)
        self.assertEqual("rebeccapurple", rgb.to_string(**args))

        args["alpha"] = True

        color = "#663399FF"
        rgb = SRGB(color)
        self.assertEqual("rebeccapurple", rgb.to_string(**args))

        color = "#66339922"
        rgb = SRGB(color)
        self.assertEqual("#66339922", rgb.to_string(**args))
