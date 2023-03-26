"""Test HSLuv."""
from coloraide import NaN
import unittest
from .. import util
from coloraide.everything import ColorAll as Color
import pytest


class TestsOkhsl(util.ColorAssertsPyTest):
    """Test Okhsl."""

    COLORS = [
        ('red', 'color(--hsluv 12.177 100 53.237)'),
        ('orange', 'color(--hsluv 44.683 100 74.934)'),
        ('yellow', 'color(--hsluv 85.874 100 97.139)'),
        ('green', 'color(--hsluv 127.72 100 46.228)'),
        ('blue', 'color(--hsluv 265.87 100 32.301)'),
        ('indigo', 'color(--hsluv 279.33 100 20.47)'),
        ('violet', 'color(--hsluv 307.72 79.542 69.695)'),
        ('white', 'color(--hsluv 0 0 100)'),
        ('gray', 'color(--hsluv 0 0 53.585)'),
        ('black', 'color(--hsluv none 0 0)'),
        # Test color
        ('color(--hsluv 270 30 50)', 'color(--hsluv 270 30 50)'),
        ('color(--hsluv 270 30 50 / 0.5)', 'color(--hsluv 270 30 50 / 0.5)'),
        ('color(--hsluv 50% 50% 50% / 50%)', 'color(--hsluv 180 50 50 / 0.5)'),
        ('color(--hsluv none none none / none)', 'color(--hsluv none none none / none)'),
        # Test percent ranges
        ('color(--hsluv 0% 0% 0%)', 'color(--hsluv 0 0 none)'),
        ('color(--hsluv 100% 100% 100%)', 'color(--hsluv 360 100 100 / 1)'),
        ('color(--hsluv -100% -100% -100%)', 'color(--hsluv -360 -100 -100 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hsluv'), Color(color2))


class TestHSLuvSerialize(util.ColorAssertsPyTest):
    """Test HSLuv serialization."""

    COLORS = [
        # Test color
        ('color(--hsluv 50 30 50 / 0.5)', {}, 'color(--hsluv 50 30 50 / 0.5)'),
        # Test alpha
        ('color(--hsluv 50 30 50)', {'alpha': True}, 'color(--hsluv 50 30 50 / 1)'),
        ('color(--hsluv 50 30 50 / 0.5)', {'alpha': False}, 'color(--hsluv 50 30 50)'),
        # Test None
        ('color(--hsluv 50 30 none)', {}, 'color(--hsluv 50 30 0)'),
        ('color(--hsluv 50 30 none)', {'none': True}, 'color(--hsluv 50 30 none)'),
        # Test Fit (not bound)
        ('color(--hsluv 50 110 50)', {}, 'color(--hsluv 51.208 100 50)'),
        ('color(--hsluv 50 110 50)', {'fit': False}, 'color(--hsluv 50 110 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHSluvProperties(util.ColorAsserts, unittest.TestCase):
    """Test HSLuv."""

    def test_names(self):
        """Test HSL-ish names."""

        self.assertEqual(Color('color(--hsluv none 0% 75% / 1)')._space.names(), ('h', 's', 'l'))

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hsluv 120 50% 90% / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--hsluv 120 50% 90% / 1)')
        self.assertEqual(c['saturation'], 50)
        c['saturation'] = 60
        self.assertEqual(c['saturation'], 60)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--hsluv 120 50% 90% / 1)')
        self.assertEqual(c['lightness'], 90)
        c['lightness'] = 80
        self.assertEqual(c['lightness'], 80)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hsluv 120 50% 90% / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestHSLuvNulls(util.ColorAsserts, unittest.TestCase):
    """Test HSLuv Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('hsluv', [NaN, 0.5, 1], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--hsluv none 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_sat(self):
        """Test minimum saturation."""

        c = Color('color(--hsluv 270 0% 0.75 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_max_light(self):
        """Test maximum lightness."""

        c = Color('color(--hsluv 270 20% 100% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_light(self):
        """Test minimum lightness."""

        c = Color('color(--hsluv 270 20% 0% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('hsluv', [270, 50, 0]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, 50, 100]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, 0, 50]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, 0.000001, 50]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, 50, 99.99999999]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, NaN, 100]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, 0.0, NaN]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, 50, NaN]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, NaN, 50]).is_achromatic(), True)
        self.assertEqual(Color('hsluv', [270, NaN, NaN]).is_achromatic(), True)
