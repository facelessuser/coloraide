"""Test HPLuv."""
from coloraide import NaN
import unittest
from .. import util
from coloraide.everything import ColorAll as Color
import pytest


class TestsHPLuv(util.ColorAssertsPyTest):
    """Test HPLuv."""

    COLORS = [
        # Test color
        ('color(--hpluv 270 30 50)', 'color(--hpluv 270 30 50)'),
        ('color(--hpluv 270 30 50 / 0.5)', 'color(--hpluv 270 30 50 / 0.5)'),
        ('color(--hpluv 50% 50% 50% / 50%)', 'color(--hpluv 180 50 50 / 0.5)'),
        ('color(--hpluv none none none / none)', 'color(--hpluv none none none / none)'),
        # Test percent ranges
        ('color(--hpluv 0% 0% 0%)', 'color(--hpluv 0 0 none)'),
        ('color(--hpluv 100% 100% 100%)', 'color(--hpluv 360 100 100 / 1)'),
        ('color(--hpluv -100% -100% -100%)', 'color(--hpluv -360 -100 -100 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hpluv'), Color(color2))


class TestHPLuvSerialize(util.ColorAssertsPyTest):
    """Test HPLuv serialization."""

    COLORS = [
        # Test color
        ('color(--hpluv 50 30 50 / 0.5)', {}, 'color(--hpluv 50 30 50 / 0.5)'),
        # Test alpha
        ('color(--hpluv 50 30 50)', {'alpha': True}, 'color(--hpluv 50 30 50 / 1)'),
        ('color(--hpluv 50 30 50 / 0.5)', {'alpha': False}, 'color(--hpluv 50 30 50)'),
        # Test None
        ('color(--hpluv 50 30 none)', {}, 'color(--hpluv 50 30 0)'),
        ('color(--hpluv 50 30 none)', {'none': True}, 'color(--hpluv 50 30 none)'),
        # Test Fit (not bound)
        ('color(--hpluv 50 110 50)', {}, 'color(--hpluv 50 100 50)'),
        ('color(--hpluv 50 110 50)', {'fit': False}, 'color(--hpluv 50 110 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHPluvProperties(util.ColorAsserts, unittest.TestCase):
    """Test HPLuv."""

    def test_names(self):
        """Test HSL-ish names."""

        self.assertEqual(Color('color(--hpluv 270 0% 0.75 / 1)')._space.names(), ('h', 'p', 'l'))

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hpluv 120 50% 90% / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_perpendiculars(self):
        """Test `perpendiculars`."""

        c = Color('color(--hpluv 120 50% 90% / 1)')
        self.assertEqual(c['perpendiculars'], 50)
        c['perpendiculars'] = 60
        self.assertEqual(c['perpendiculars'], 60)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--hpluv 120 50% 90% / 1)')
        self.assertEqual(c['lightness'], 90)
        c['lightness'] = 80
        self.assertEqual(c['lightness'], 80)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hpluv 120 50% 90% / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestHPLuvNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('hpluv', [NaN, 0.5, 1], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--hpluv none 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_sat(self):
        """Test minimum saturation."""

        c = Color('color(--hpluv 270 0% 0.75 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_max_light(self):
        """Test maximum lightness."""

        c = Color('color(--hpluv 270 20% 100% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_light(self):
        """Test minimum lightness."""

        c = Color('color(--hpluv 270 20% 0% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('hpluv', [270, 50, 0]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, 50, 100]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, 0, 50]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, 0.000001, 50]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, 50, 99.99999999]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, NaN, 100]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, 0.0, NaN]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, 50, NaN]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, NaN, 50]).is_achromatic(), True)
        self.assertEqual(Color('hpluv', [270, NaN, NaN]).is_achromatic(), True)
