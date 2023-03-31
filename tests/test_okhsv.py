"""Test Okhsv library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
from coloraide import NaN
import pytest


class TestsOkhsv(util.ColorAssertsPyTest):
    """Test Okhsv."""

    COLORS = [
        ('red', 'color(--okhsv 29.234 1 1)'),
        ('orange', 'color(--okhsv 70.67 1 1)'),
        ('yellow', 'color(--okhsv 109.77 1 1)'),
        ('green', 'color(--okhsv 142.5 1 0.52704)'),
        ('blue', 'color(--okhsv 264.05 1 1)'),
        ('indigo', 'color(--okhsv 301.68 1 0.50334)'),
        ('violet', 'color(--okhsv 327.21 0.60487 0.93895)'),
        ('white', 'color(--okhsv none 0 1)'),
        ('gray', 'color(--okhsv none 0 0.53571)'),
        ('black', 'color(--okhsv none 0 0)'),
        # Test color
        ('color(--okhsv 270 0.3 0.5)', 'color(--okhsv 270 0.3 0.5)'),
        ('color(--okhsv 270 0.3 0.5 / 0.5)', 'color(--okhsv 270 0.3 0.5 / 0.5)'),
        ('color(--okhsv 50% 50% 50% / 50%)', 'color(--okhsv 180 0.5 0.5 / 0.5)'),
        ('color(--okhsv none none none / none)', 'color(--okhsv none none none / none)'),
        # Test percent ranges
        ('color(--okhsv 0% 0% 0%)', 'color(--okhsv 0 0 none)'),
        ('color(--okhsv 100% 100% 100%)', 'color(--okhsv 360 1 1 / 1)'),
        ('color(--okhsv -100% -100% -100%)', 'color(--okhsv -360 -1 -1 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('okhsv'), Color(color2))


class TestOkhsvSerialize(util.ColorAssertsPyTest):
    """Test Okhsv serialization."""

    COLORS = [
        # Test color
        ('color(--okhsv 50 0.3 0.5 / 0.5)', {}, 'color(--okhsv 50 0.3 0.5 / 0.5)'),
        # Test alpha
        ('color(--okhsv 50 0.3 0.5)', {'alpha': True}, 'color(--okhsv 50 0.3 0.5 / 1)'),
        ('color(--okhsv 50 0.3 0.5 / 0.5)', {'alpha': False}, 'color(--okhsv 50 0.3 0.5)'),
        # Test None
        ('color(--okhsv 50 0.3 none)', {}, 'color(--okhsv 50 0.3 0)'),
        ('color(--okhsv 50 0.3 none)', {'none': True}, 'color(--okhsv 50 0.3 none)'),
        # Test Fit (not bound)
        ('color(--okhsv 50 1.1 0.5)', {}, 'color(--okhsv 50 1 0.5)'),
        ('color(--okhsv 50 1.1 0.5)', {'fit': False}, 'color(--okhsv 50 1.1 0.5)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestOkhsvProperties(util.ColorAsserts, unittest.TestCase):
    """Test Okhsv."""

    def test_names(self):
        """Test HSL-ish names."""

        self.assertEqual(Color('color(--okhsv 120 50% 50% / 1)')._space.names(), ('h', 's', 'v'))

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--okhsv 120 50% 50% / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--okhsv 120 50% 50% / 1)')
        self.assertEqual(c['saturation'], 0.5)
        c['saturation'] = 0.6
        self.assertEqual(c['saturation'], 0.6)

    def test_value(self):
        """Test `value`."""

        c = Color('color(--okhsv 120 50% 50% / 1)')
        self.assertEqual(c['value'], 0.5)
        c['value'] = 0.4
        self.assertEqual(c['value'], 0.4)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--okhsv 120 50% 50% / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('okhsv', [NaN, 0.5, 0.75], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_gray_null(self):
        """Test that gray has null."""

        c = Color('gray').convert('okhsv')
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--okhsv none 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_sat(self):
        """Test minimum saturation."""

        c = Color('color(--okhsv 270 0% 0.75 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('okhsv', [270, 0.5, 0]).is_achromatic(), True)
        self.assertEqual(Color('okhsv', [270, 0, 0.5]).is_achromatic(), True)
        self.assertEqual(Color('okhsv', [270, 0.000001, 0.5]).is_achromatic(), True)
        self.assertEqual(Color('okhsv', [270, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('okhsv', [270, 0.0, NaN]).is_achromatic(), True)
        self.assertEqual(Color('okhsv', [270, 0.5, 1]).is_achromatic(), False)
        self.assertEqual(Color('okhsv', [270, NaN, 1]).is_achromatic(), True)
        self.assertEqual(Color('okhsv', [270, 0.5, NaN]).is_achromatic(), True)
        self.assertEqual(Color('okhsv', [270, NaN, NaN]).is_achromatic(), True)
