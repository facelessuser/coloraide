"""Test Okokhsl library."""
from coloraide.util import NaN
import unittest
import math
from . import util
from coloraide import Color


class TestOkhslInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test Okhsl."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("okhsl", [20, 100, 75]), Color('color(--okhsl 20 100% 75%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("okhsl", [20, 100, 75])), Color('color(--okhsl 20 100% 75%)'))

    def test_percent(self):
        """Test that percents work properly."""

        color = "color(--okhsl 20 100% 75% / 100%)"
        okhsl = Color(color)
        self.assertEqual("color(--okhsl 20 100% 75%)", okhsl.to_string())

        color = "color(--okhsl 20 100% 75% / 20%)"
        okhsl = Color(color)
        self.assertEqual("color(--okhsl 20 100% 75% / 0.2)", okhsl.to_string())

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(--okhsl 20 100% 75% / 0.2)"
        okhsl = Color(color)
        self.assertEqual("color(--okhsl 20 100% 75%)", okhsl.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(--okhsl 20 100% 75% / 1)"
        okhsl = Color(color)
        self.assertEqual("color(--okhsl 20 100% 75% / 1)", okhsl.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--okhsl 20.1234567 50.1234567% 50.1234567%)'
        self.assertEqual(Color(color).to_string(), 'color(--okhsl 20.123 50.123% 50.123%)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(--okhsl 20.1 50.1% 50.1%)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(--okhsl 20 50% 50%)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(--okhsl 20.12345669999999842048055143095552921295166015625 50.12345669999999842048055143095552921295166015625% 50.12345669999999842048055143095552921295166015625%)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--okhsl 50 40% 110%)').to_string(),
            'color(--okhsl 259.98 0.20167% 100%)'
        )

        self.assertEqual(
            Color('color(--okhsl 50 40% 110%)').to_string(fit="clip"),
            'color(--okhsl 50 40% 100%)'
        )

        self.assertEqual(
            Color('color(--okhsl 50 40% 110%)').to_string(fit=False),
            'color(--okhsl 50 40% 110%)'
        )


class TestOkhslProperties(util.ColorAsserts, unittest.TestCase):
    """Test Okhsl."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--okhsl 120 50% 90% / 1)')
        self.assertEqual(c.hue, 120)
        c.hue = 110
        self.assertEqual(c.hue, 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--okhsl 120 50% 90% / 1)')
        self.assertEqual(c.saturation, 50)
        c.saturation = 60
        self.assertEqual(c.saturation, 60)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--okhsl 120 50% 90% / 1)')
        self.assertEqual(c.lightness, 90)
        c.lightness = 80
        self.assertEqual(c.lightness, 80)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--okhsl 120 50% 90% / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('okhsl', [NaN, 50, 100], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_auto_null(self):
        """Test auto null."""

        c = Color('color(--okhsl 120 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))
