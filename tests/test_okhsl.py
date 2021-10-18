"""Test Okhsl library."""
from coloraide.util import NaN
import unittest
from . import util
from coloraide import Color


class TestOkhslInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test Okhsl."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("okhsl", [20, 1, 0.75]), Color('color(--okhsl 20 1 0.75)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("okhsl", [20, 1, 0.75])), Color('color(--okhsl 20 1 0.75)'))

    def test_percent(self):
        """Test that percents work properly."""

        color = "color(--okhsl 20 100% 75% / 100%)"
        okhsl = Color(color)
        self.assertEqual("color(--okhsl 20 1 0.75)", okhsl.to_string())

        color = "color(--okhsl 20 1 0.75 / 20%)"
        okhsl = Color(color)
        self.assertEqual("color(--okhsl 20 1 0.75 / 0.2)", okhsl.to_string())

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(--okhsl 20 100% 75% / 0.2)"
        okhsl = Color(color)
        self.assertEqual("color(--okhsl 20 1 0.75)", okhsl.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(--okhsl 20 100% 75% / 1)"
        okhsl = Color(color)
        self.assertEqual("color(--okhsl 20 1 0.75 / 1)", okhsl.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--okhsl 20.1234567 0.1234567 0.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(--okhsl 20.123 0.12346 0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(--okhsl 20.1 0.123 0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(--okhsl 20 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(--okhsl 20.12345669999999842048055143095552921295166015625 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--okhsl 50 40% 110%)').to_string(),
            'color(--okhsl 90 0 1)'
        )

        self.assertEqual(
            Color('color(--okhsl 50 40% 110%)').to_string(fit="clip"),
            'color(--okhsl 50 0.4 1)'
        )

        self.assertEqual(
            Color('color(--okhsl 50 40% 110%)').to_string(fit=False),
            'color(--okhsl 50 0.4 1.1)'
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
        self.assertEqual(c.saturation, 0.5)
        c.saturation = 0.6
        self.assertEqual(c.saturation, 0.6)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--okhsl 120 50% 90% / 1)')
        self.assertEqual(c.lightness, 0.9)
        c.lightness = 0.8
        self.assertEqual(c.lightness, 0.8)

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

        c = Color('okhsl', [NaN, 0.5, 1], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_auto_null(self):
        """Test auto null."""

        c = Color('color(--okhsl 120 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))
