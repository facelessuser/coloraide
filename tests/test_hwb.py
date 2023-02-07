"""Test HWB library."""
import unittest
import math
from . import util
from coloraide import Color, NaN
import pytest


class TestHWB(util.ColorAssertsPyTest):
    """Test HWB."""

    COLORS = [
        ('red', 'color(--hwb 0 0 0)'),
        ('orange', 'color(--hwb 38.824 0 0)'),
        ('yellow', 'color(--hwb 60 0 0)'),
        ('green', 'color(--hwb 120 0 0.49804)'),
        ('blue', 'color(--hwb 240 0 0)'),
        ('indigo', 'color(--hwb 274.62 0 0.4902)'),
        ('violet', 'color(--hwb 300 0.5098 0.06667)'),
        ('white', 'color(--hwb none 1 0)'),
        ('gray', 'color(--hwb none 0.50196 0.49804)'),
        ('black', 'color(--hwb none 0 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hwb'), Color(color2), color=True)


class TestHWBProperties(util.ColorAsserts, unittest.TestCase):
    """Test HWB."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_whiteness(self):
        """Test `whiteness`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c['whiteness'], 0.5)
        c['whiteness'] = 0.6
        self.assertEqual(c['whiteness'], 0.6)

    def test_blackness(self):
        """Test `blackness`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c['blackness'], 0.2)
        c['blackness'] = 0.1
        self.assertEqual(c['blackness'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_real_achromatic_hue(self):
        """Test that we get the expected achromatic hue."""

        self.assertEqual(Color('white').convert('hwb')._space.achromatic_hue(), 0.0)

    def test_null_input(self):
        """Test null input."""

        c = Color('hwb', [NaN, 0.1, 0.2], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('hwb(none 100% 0% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_max_white_black(self):
        """Test maximum lightness."""

        c = Color('hwb(270 20% 100% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_to_hsv(self):
        """Test null from Lab conversion."""

        c1 = Color('color(--hsv 0 0% 50%)')
        c2 = c1.convert('hwb')
        self.assertColorEqual(c2, Color('hwb(0 50% 50%)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_from_hsv(self):
        """Test null from Lab conversion."""

        c1 = Color('hwb(0 50% 50%)')
        c2 = c1.convert('hsv')
        self.assertColorEqual(c2, Color('color(--hsv 0 0% 50%)'))
        self.assertTrue(c2.is_nan('hue'))
