"""Test HSL library."""
from coloraide import NaN
import unittest
import math
from . import util
from coloraide import Color
import pytest


class TestHSL(util.ColorAssertsPyTest):
    """Test HSL."""

    COLORS = [
        ('red', 'color(--hsl 0 1 0.5)'),
        ('orange', 'color(--hsl 38.824 1 0.5)'),
        ('yellow', 'color(--hsl 60 1 0.5)'),
        ('green', 'color(--hsl 120 1 0.25098)'),
        ('blue', 'color(--hsl 240 1 0.5)'),
        ('indigo', 'color(--hsl 274.62 1 0.2549)'),
        ('violet', 'color(--hsl 300 0.76056 0.72157)'),
        ('white', 'color(--hsl none 0 1)'),
        ('gray', 'color(--hsl none 0 0.50196)'),
        ('black', 'color(--hsl none 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hsl'), Color(color2), color=True)


class TestHSLProperties(util.ColorAsserts, unittest.TestCase):
    """Test HSL."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c['saturation'], 0.5)
        c['saturation'] = 0.6
        self.assertEqual(c['saturation'], 0.6)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c['lightness'], 0.9)
        c['lightness'] = 0.8
        self.assertEqual(c['lightness'], 0.8)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_real_achromatic_hue(self):
        """Test that we get the expected achromatic hue."""

        self.assertEqual(Color('white').convert('hsl')._space.achromatic_hue(), 0.0)

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
