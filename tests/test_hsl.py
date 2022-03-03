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

        self.assertColorEqual(Color("hsl", [20, 1, 0.75]), Color('hsl(20 100% 75%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("hsl", [20, 1, 0.75])), Color('hsl(20 100% 75%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--hsl 20 100% 75%)"

        self.assertEqual(Color(color).to_string(**args), 'color(--hsl 20 1 0.75)')

        color = "color(--hsl 20 1 0.75 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--hsl 20 1 0.75 / 0.5)')

        color = "color(--hsl 20 100% 75% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--hsl 20 1 0.75 / 0.5)')

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

        color = 'color(--hsl 20.1234567 0.1234567 0.1234567)'
        self.assertEqual(Color(color).to_string(), 'hsl(20.123 12.346% 12.346%)')
        self.assertEqual(Color(color).to_string(precision=3), 'hsl(20.1 12.3% 12.3%)')
        self.assertEqual(Color(color).to_string(precision=0), 'hsl(20 12% 12%)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'hsl(20.12345669999999842048055143095552921295166015625 12.3456700000000001438138497178442776203155517578125% 12.3456700000000001438138497178442776203155517578125%)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--hsl 20 150% 75%)').to_string(),
            'hsl(19.89 100% 76.506%)'
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

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c.hue, 120)
        c.hue = 110
        self.assertEqual(c.hue, 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c.saturation, 0.5)
        c.saturation = 0.6
        self.assertEqual(c.saturation, 0.6)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c.lightness, 0.9)
        c.lightness = 0.8
        self.assertEqual(c.lightness, 0.8)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('hsl', [NaN, 0.5, 1], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('hsl(none 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_sat(self):
        """Test minimum saturation."""

        c = Color('hsl(270 0% 75% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_max_light(self):
        """Test maximum lightness."""

        c = Color('hsl(270 20% 100% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_light(self):
        """Test minimum lightness."""

        c = Color('hsl(270 20% 0% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_corner_case_null(self):
        """Test corner case that produces null."""

        c = Color('color(srgb -2 0 2)').convert('hsl')
        self.assertTrue(c.is_nan('hue'))
