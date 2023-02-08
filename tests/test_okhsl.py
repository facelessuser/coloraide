"""Test Okhsl library."""
from coloraide import NaN
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestsOkhsl(util.ColorAssertsPyTest):
    """Test Okhsl."""

    COLORS = [
        ('red', 'color(--okhsl 29.234 1 0.56808)'),
        ('orange', 'color(--okhsl 70.67 1 0.75883)'),
        ('yellow', 'color(--okhsl 109.77 1 0.9627)'),
        ('green', 'color(--okhsl 142.5 1 0.44371)'),
        ('blue', 'color(--okhsl 264.05 1 0.36657)'),
        ('indigo', 'color(--okhsl 301.68 1.0018 0.24043)'),
        ('violet', 'color(--okhsl 327.21 0.90624 0.7231)'),
        ('white', 'color(--okhsl none 0 1)'),
        ('gray', 'color(--okhsl none 0 0.53571)'),
        ('black', 'color(--okhsl none 0 0)'),
        # Test color
        ('color(--okhsl 270 0.3 0.5)', 'color(--okhsl 270 0.3 0.5)'),
        ('color(--okhsl 270 0.3 0.5 / 0.5)', 'color(--okhsl 270 0.3 0.5 / 0.5)'),
        ('color(--okhsl 50% 50% 50% / 50%)', 'color(--okhsl 180 0.5 0.5 / 0.5)'),
        ('color(--okhsl none none none / none)', 'color(--okhsl none none none / none)'),
        # Test percent ranges
        ('color(--okhsl 0% 0% 0%)', 'color(--okhsl 0 0 none)'),
        ('color(--okhsl 100% 100% 100%)', 'color(--okhsl 360 1 1 / 1)'),
        ('color(--okhsl -100% -100% -100%)', 'color(--okhsl -360 -1 -1 / 1)'),
        # Space specific tests to ensure complete coverage in algorithm
        ('color(--oklab 0.5 0.1 0)', 'color(--okhsl 0 0.49656 0.42114)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('okhsl'), Color(color2))


class TestOkhslSerialize(util.ColorAssertsPyTest):
    """Test Okhsl serialization."""

    COLORS = [
        # Test color
        ('color(--okhsl 50 0.3 0.5 / 0.5)', {}, 'color(--okhsl 50 0.3 0.5 / 0.5)'),
        # Test alpha
        ('color(--okhsl 50 0.3 0.5)', {'alpha': True}, 'color(--okhsl 50 0.3 0.5 / 1)'),
        ('color(--okhsl 50 0.3 0.5 / 0.5)', {'alpha': False}, 'color(--okhsl 50 0.3 0.5)'),
        # Test None
        ('color(--okhsl 50 0.3 none)', {}, 'color(--okhsl 50 0.3 0)'),
        ('color(--okhsl 50 0.3 none)', {'none': True}, 'color(--okhsl 50 0.3 none)'),
        # Test Fit (not bound)
        ('color(--okhsl 50 1.1 0.5)', {}, 'color(--okhsl 50 1 0.5)'),
        ('color(--okhsl 50 1.1 0.5)', {'fit': False}, 'color(--okhsl 50 1.1 0.5)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestOkhslProperties(util.ColorAsserts, unittest.TestCase):
    """Test Okhsl."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--okhsl 120 50% 90% / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--okhsl 120 50% 90% / 1)')
        self.assertEqual(c['saturation'], 0.5)
        c['saturation'] = 0.6
        self.assertEqual(c['saturation'], 0.6)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--okhsl 120 50% 90% / 1)')
        self.assertEqual(c['lightness'], 0.9)
        c['lightness'] = 0.8
        self.assertEqual(c['lightness'], 0.8)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--okhsl 120 50% 90% / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_real_achromatic_hue(self):
        """Test that we get the expected achromatic hue."""

        self.assertEqual(Color('white').convert('okhsl')._space.achromatic_hue(), 0.0)

    def test_null_input(self):
        """Test null input."""

        c = Color('okhsl', [NaN, 0.5, 1], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--okhsl none 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_sat(self):
        """Test minimum saturation."""

        c = Color('color(--okhsl 270 0% 0.75 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_max_light(self):
        """Test maximum lightness."""

        c = Color('color(--okhsl 270 20% 100% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_light(self):
        """Test minimum lightness."""

        c = Color('color(--okhsl 270 20% 0% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))
