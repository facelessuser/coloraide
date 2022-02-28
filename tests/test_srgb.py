"""Test SRGB library."""
import unittest
from . import util
from coloraide import Color


class TestSRGBInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test SRGB."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("srgb", [1, 1, 1]), Color('rgb(100% 100% 100%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("srgb", [1, 1, 1])), Color('rgb(100% 100% 100%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(srgb 0.3 1 0.5)"

        self.assertEqual(Color(color).to_string(**args), 'color(srgb 0.3 1 0.5)')

        color = "color(srgb 0.3 1 0.5 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(srgb 0.3 1 0.5 / 0.5)')

        color = "color(srgb 30% 100% 50% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(srgb 0.3 1 0.5 / 0.5)')

    def test_comma(self):
        """Test comma input and comma output format."""

        args = {"comma": True}

        color = "rgb(30, 100, 200)"
        rgb = Color(color)
        self.assertEqual(color, rgb.to_string(**args))

        color = "rgb(30, 100, 200, 1)"
        rgb = Color(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_string(**args))

        color = "rgb(30, 100, 200, 0.2)"
        rgb = Color(color)
        self.assertEqual("rgba(30, 100, 200, 0.2)", rgb.to_string(**args))

    def test_space(self):
        """Test space input and space output format."""

        args = {}

        color = "rgb(30 100 200)"
        rgb = Color(color)
        self.assertEqual(color, rgb.to_string(**args))

        color = "rgb(30 100 200 / 1)"
        rgb = Color(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_string(**args))

        color = "rgb(30 100 200 / 0.2)"
        rgb = Color(color)
        self.assertEqual(color, rgb.to_string(**args))

    def test_hex(self):
        """Test hex input and hex output format."""

        args = {"hex": True}

        color = "#AA33DD"
        rgb = Color(color)
        self.assertEqual(color.lower(), rgb.to_string(**args))

        color = "#AA33DDFF"
        rgb = Color(color)
        self.assertEqual("#aa33dd", rgb.to_string(**args))

        color = "#AA33DD22"
        rgb = Color(color)
        self.assertEqual("#aa33dd22", rgb.to_string(**args))

    def test_hex_upper(self):
        """Test hex input."""

        args = {"hex": True, "upper": True}

        color = "#AA33DD"
        rgb = Color(color)
        self.assertEqual(color, rgb.to_string(**args))

        color = "#AA33DDFF"
        rgb = Color(color)
        self.assertEqual("#AA33DD", rgb.to_string(**args))

        color = "#AA33DD22"
        rgb = Color(color)
        self.assertEqual("#AA33DD22", rgb.to_string(**args))

    def test_hex_compressed(self):
        """Test hex input."""

        args = {"hex": True, "compress": True}

        color = "#AA33DD"
        rgb = Color(color)
        self.assertEqual("#a3d", rgb.to_string(**args))

        color = "#AA33DDFF"
        rgb = Color(color)
        self.assertEqual("#a3d", rgb.to_string(**args))

        args["alpha"] = True

        color = "#AA33DD22"
        rgb = Color(color)
        self.assertEqual("#a3d2", rgb.to_string(**args))

        args["alpha"] = None

        color = "#A3D"
        rgb = Color(color)
        self.assertEqual("#a3d", rgb.to_string(**args))

        color = "#A3DF"
        rgb = Color(color)
        self.assertEqual("#a3d", rgb.to_string(**args))

        args["alpha"] = True

        color = "#A3D2"
        rgb = Color(color)
        self.assertEqual("#a3d2", rgb.to_string(**args))

    def test_alias(self):
        """Test that `rgba` is an alias for `rgb`."""

        args = {"comma": True}

        color = "rgba(30, 100, 200)"
        rgb = Color(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_string(**args))

        color = "rgba(30, 100, 200, 1)"
        rgb = Color(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_string(**args))

        color = "rgba(30, 100, 200, 0.5)"
        rgb = Color(color)
        self.assertEqual("rgba(30, 100, 200, 0.5)", rgb.to_string(**args))

        args["comma"] = False

        color = "rgba(30 100 200)"
        rgb = Color(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_string(**args))

        color = "rgba(30 100 200 / 1)"
        rgb = Color(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_string(**args))

        color = "rgba(30 100 200 / 0.5)"
        rgb = Color(color)
        self.assertEqual("rgb(30 100 200 / 0.5)", rgb.to_string(**args))

    def test_percent(self):
        """Test that percents work properly."""

        args = {"comma": True}
        pargs = {"comma": True, "percent": True}

        color = "rgb(30%, 100%, 100%)"
        rgb = Color(color)
        self.assertEqual("rgb(76.5, 255, 255)", rgb.to_string(**args))
        self.assertEqual("rgb(30%, 100%, 100%)", rgb.to_string(**pargs))

        color = "rgba(30%, 100%, 100%, 100%)"
        rgb = Color(color)
        self.assertEqual("rgb(76.5, 255, 255)", rgb.to_string(**args))
        self.assertEqual("rgb(30%, 100%, 100%)", rgb.to_string(**pargs))

        color = "rgba(30%, 100%, 100%, 20%)"
        rgb = Color(color)
        self.assertEqual("rgba(76.5, 255, 255, 0.2)", rgb.to_string(**args))
        self.assertEqual("rgba(30%, 100%, 100%, 0.2)", rgb.to_string(**pargs))

        args["comma"] = False
        pargs["comma"] = False

        color = "rgb(30% 100% 100%)"
        rgb = Color(color)
        self.assertEqual("rgb(76.5 255 255)", rgb.to_string(**args))
        self.assertEqual("rgb(30% 100% 100%)", rgb.to_string(**pargs))

        color = "rgba(30% 100% 100% / 100%)"
        rgb = Color(color)
        self.assertEqual("rgb(76.5 255 255)", rgb.to_string(**args))
        self.assertEqual("rgb(30% 100% 100%)", rgb.to_string(**pargs))

        color = "rgba(30% 100% 100% / 20%)"
        rgb = Color(color)
        self.assertEqual("rgb(76.5 255 255 / 0.2)", rgb.to_string(**args))
        self.assertEqual("rgb(30% 100% 100% / 0.2)", rgb.to_string(**pargs))

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"comma": True, "alpha": False}

        color = "rgb(30, 100, 200, 0.2)"
        rgb = Color(color)
        self.assertEqual("rgb(30, 100, 200)", rgb.to_string(**args))

        args["comma"] = False

        color = "rgb(30 100 200 / 0.2)"
        rgb = Color(color)
        self.assertEqual("rgb(30 100 200)", rgb.to_string(**args))

        args["hex"] = True

        color = "#AA33DD22"
        rgb = Color(color)
        self.assertEqual("#aa33dd", rgb.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"comma": True, "alpha": True}

        color = "rgb(30, 100, 200, 100%)"
        rgb = Color(color)
        self.assertEqual("rgba(30, 100, 200, 1)", rgb.to_string(**args))

        args["comma"] = False

        color = "rgb(30 100 200 / 100%)"
        rgb = Color(color)
        self.assertEqual("rgb(30 100 200 / 1)", rgb.to_string(**args))

        args["hex"] = True

        color = "#AA33DDFF"
        rgb = Color(color)
        self.assertEqual("#aa33ddff", rgb.to_string(**args))

    def test_name(self):
        """Test color names."""

        args = {"names": True}

        color = "rebeccapurple"
        rgb = Color(color)
        self.assertEqual("rebeccapurple", rgb.to_string(**args))

        color = "#663399"
        rgb = Color(color)
        self.assertEqual("rebeccapurple", rgb.to_string(**args))

        args["hex"] = True
        args["names"] = False

        color = "#663399"
        rgb = Color(color)
        self.assertEqual("#663399", rgb.to_string(**args))

        args["names"] = True

        color = "#663399"
        rgb = Color(color)
        self.assertEqual("rebeccapurple", rgb.to_string(**args))

        args["alpha"] = True

        color = "#663399FF"
        rgb = Color(color)
        self.assertEqual("rebeccapurple", rgb.to_string(**args))

        color = "#66339922"
        rgb = Color(color)
        self.assertEqual("#66339922", rgb.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(srgb 0.1234567 0.1234567 0.1234567)'
        self.assertEqual(Color(color).to_string(), 'rgb(31.481 31.481 31.481)')
        self.assertEqual(Color(color).to_string(precision=3), 'rgb(31.5 31.5 31.5)')
        self.assertEqual(Color(color).to_string(precision=0), 'rgb(31 31 31)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'rgb(31.481458500000002231899998150765895843505859375 31.481458500000002231899998150765895843505859375 31.481458500000002231899998150765895843505859375)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(srgb 2 -1 0)').to_string(),
            'rgb(255 118.31 100.77)'
        )

        self.assertEqual(
            Color('color(srgb 2 -1 0)').to_string(fit="clip"),
            'rgb(255 0 0)'
        )

        self.assertEqual(
            Color('color(srgb 2 -1 0)').to_string(fit=False),
            'rgb(510 -255 0)'
        )


class TestSRGBProperties(util.ColorAsserts, unittest.TestCase):
    """Test sRGB."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.red, 0.1)
        c.red = 0.2
        self.assertEqual(c.red, 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.green, 0.2)
        c.green = 0.1
        self.assertEqual(c.green, 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.blue, 0.3)
        c.blue = 0.1
        self.assertEqual(c.blue, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)
