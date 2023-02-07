"""Test HSV library."""
import unittest
from . import util
from coloraide import Color, NaN
import pytest


class TestHSV(util.ColorAssertsPyTest):
    """Test HSV."""

    COLORS = [
        ('red', 'color(--hsv 0 1 1)'),
        ('orange', 'color(--hsv 38.824 1 1)'),
        ('yellow', 'color(--hsv 60 1 1)'),
        ('green', 'color(--hsv 120 1 0.50196)'),
        ('blue', 'color(--hsv 240 1 1)'),
        ('indigo', 'color(--hsv 274.62 1 0.5098)'),
        ('violet', 'color(--hsv 300 0.45378 0.93333)'),
        ('white', 'color(--hsv none 0 1)'),
        ('gray', 'color(--hsv none 0 0.50196)'),
        ('black', 'color(--hsv none 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hsv'), Color(color2))


class TestHSVProperties(util.ColorAsserts, unittest.TestCase):
    """Test HSV."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hsv 120 50% 50% / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--hsv 120 50% 50% / 1)')
        self.assertEqual(c['saturation'], 0.5)
        c['saturation'] = 0.6
        self.assertEqual(c['saturation'], 0.6)

    def test_value(self):
        """Test `value`."""

        c = Color('color(--hsv 120 50% 50% / 1)')
        self.assertEqual(c['value'], 0.5)
        c['value'] = 0.4
        self.assertEqual(c['value'], 0.4)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hsv 120 50% 50% / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_real_achromatic_hue(self):
        """Test that we get the expected achromatic hue."""

        self.assertEqual(Color('white').convert('hsv')._space.achromatic_hue(), 0.0)

    def test_null_input(self):
        """Test null input."""

        c = Color('hsv', [NaN, 0.5, 0.75], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--hsv none 0% 0.75 / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_sat(self):
        """Test minimum saturation."""

        c = Color('color(--hsv 270 0% 0.75 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_to_hsl(self):
        """Test null from Lab conversion."""

        c1 = Color('color(--hsv 0 0% 50%)')
        c2 = c1.convert('hsl')
        self.assertColorEqual(c2, Color('hsl(0 0% 50%)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_from_hsl(self):
        """Test null from Lab conversion."""

        c1 = Color('hsl(0 0% 50%)')
        c2 = c1.convert('hsv')
        self.assertColorEqual(c2, Color('color(--hsv 0 0% 50%)'))
        self.assertTrue(c2.is_nan('hue'))
