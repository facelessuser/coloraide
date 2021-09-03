"""Test HSL library."""
from coloraide.util import NaN
import unittest
import math
from . import util
from coloraide import Color


class TestHSLInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test HSL."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("hsl", [20, 100, 75]), Color('hsl(20 100% 75%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("hsl", [20, 100, 75])), Color('hsl(20 100% 75%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--hsl 20 100% 75%)"

        self.assertEqual(Color(color).to_string(**args), 'color(--hsl 20 100% 75%)')

        color = "color(--hsl 20 100% 75% / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--hsl 20 100% 75% / 0.5)')

        color = "color(--hsl 20 100% 75% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--hsl 20 100% 75% / 0.5)')

    def test_comma(self):
        """Test comma input and comma output format."""

        args = {"comma": True}

        color = "hsl(20, 100%, 75%)"
        hsl = Color(color)
        self.assertEqual(color, hsl.to_string(**args))

        color = "hsl(20, 100%, 75%, 1)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        color = "hsl(20, 100%, 75%, 0.2)"
        hsl = Color(color)
        self.assertEqual("hsla(20, 100%, 75%, 0.2)", hsl.to_string(**args))

    def test_space(self):
        """Test space input and space output format."""

        args = {}

        color = "hsl(20 100% 75%)"
        hsl = Color(color)
        self.assertEqual(color, hsl.to_string(**args))

        color = "hsl(20 100% 75% / 1)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

        color = "hsl(20 100% 75% / 0.2)"
        hsl = Color(color)
        self.assertEqual(color, hsl.to_string(**args))

    def test_alias(self):
        """Test that `hsla` is an alias for `hsl`."""

        args = {"comma": True}

        color = "hsla(20, 100%, 75%)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 1)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 0.5)"
        hsl = Color(color)
        self.assertEqual("hsla(20, 100%, 75%, 0.5)", hsl.to_string(**args))

        args["comma"] = False

        color = "hsla(20, 100%, 75%)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 1)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 0.5)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75% / 0.5)", hsl.to_string(**args))

    def test_percent(self):
        """Test that percents work properly."""

        args = {"comma": True}

        color = "hsla(20, 100%, 75%, 100%)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 20%)"
        hsl = Color(color)
        self.assertEqual("hsla(20, 100%, 75%, 0.2)", hsl.to_string(**args))

        args["comma"] = False

        color = "hsl(20 100% 75% / 100%)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

        color = "hsl(20 100% 75% / 20%)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75% / 0.2)", hsl.to_string(**args))

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"comma": True, "alpha": False}

        color = "hsla(20, 100%, 75%, 0.2)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        args["comma"] = False

        color = "hsl(20 100% 75% / 0.2)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"comma": True, "alpha": True}

        color = "hsla(20, 100%, 75%, 1)"
        hsl = Color(color)
        self.assertEqual("hsla(20, 100%, 75%, 1)", hsl.to_string(**args))

        args["comma"] = False

        color = "hsl(20 100% 75% / 1)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75% / 1)", hsl.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--hsl 20.1234567 50.1234567% 50.1234567%)'
        self.assertEqual(Color(color).to_string(), 'hsl(20.123 50.123% 50.123%)')
        self.assertEqual(Color(color).to_string(precision=3), 'hsl(20.1 50.1% 50.1%)')
        self.assertEqual(Color(color).to_string(precision=0), 'hsl(20 50% 50%)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'hsl(20.12345669999999842048055143095552921295166015625 50.12345669999999842048055143095552921295166015625% 50.12345669999999842048055143095552921295166015625%)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--hsl 20 150% 75%)').to_string(),
            'hsl(19.891 100% 76.496%)'
        )

        self.assertEqual(
            Color('color(--hsl 20 150% 75%)').to_string(fit="clip"),
            'hsl(20 100% 75%)'
        )

        self.assertEqual(
            Color('color(--hsl 20 150% 75%)').to_string(fit=False),
            'hsl(20 150% 75%)'
        )

    def test_hue_inputs(self):
        """Test hue inputs."""

        color = "hsl(90deg, 100%, 75%)"
        hsl = Color(color)
        self.assertEqual("hsl(90 100% 75%)", hsl.to_string())

        color = "hsl({:f}rad, 100%, 75%)".format(math.radians(90))
        hsl = Color(color)
        self.assertEqual("hsl(90 100% 75%)", hsl.to_string())

        color = "hsl(100grad, 100%, 75%)"
        hsl = Color(color)
        self.assertEqual("hsl(90 100% 75%)", hsl.to_string())

        color = "hsl(0.25turn, 100%, 75%)"
        hsl = Color(color)
        self.assertEqual("hsl(90 100% 75%)", hsl.to_string())


class TestHSLProperties(util.ColorAsserts, unittest.TestCase):
    """Test HSL."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hsl 120 50% 100% / 1)')
        self.assertEqual(c.hue, 120)
        c.hue = 110
        self.assertEqual(c.hue, 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--hsl 120 50% 100% / 1)')
        self.assertEqual(c.saturation, 50)
        c.saturation = 60
        self.assertEqual(c.saturation, 60)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--hsl 120 50% 100% / 1)')
        self.assertEqual(c.lightness, 100)
        c.lightness = 90
        self.assertEqual(c.lightness, 90)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hsl 120 50% 100% / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('hsl', [NaN, 50, 100], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_auto_null(self):
        """Test auto null."""

        c = Color('hsl(120 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_corner_case_null(self):
        """Test corner case that produces null."""

        c = Color('color(srgb -2 0 2)').convert('hsl')
        self.assertTrue(c.is_nan('hue'))
