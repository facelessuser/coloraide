"""Test Luv library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestLuv(util.ColorAssertsPyTest):
    """Test Luv."""

    COLORS = [
        ('red', 'color(--luv 53.237 175.01 37.765)'),
        ('orange', 'color(--luv 74.934 74.839 74.014)'),
        ('yellow', 'color(--luv 97.139 7.7042 106.81)'),
        ('green', 'color(--luv 46.228 -43.768 56.599)'),
        ('blue', 'color(--luv 32.301 -9.4024 -130.35)'),
        ('indigo', 'color(--luv 20.47 10.08 -61.34)'),
        ('violet', 'color(--luv 69.695 51.84 -67.037)'),
        ('white', 'color(--luv 100 0 0)'),
        ('gray', 'color(--luv 53.585 0 0)'),
        ('black', 'color(--luv 0 0 0)'),
        # Test color
        ('color(--luv 100 0.1 -0.1)', 'color(--luv 100 0.1 -0.1)'),
        ('color(--luv 100 0.1 -0.1 / 0.5)', 'color(--luv 100 0.1 -0.1 / 0.5)'),
        ('color(--luv 50% 50% -50% / 50%)', 'color(--luv 50 107.5 -107.5 / 0.5)'),
        ('color(--luv none none none / none)', 'color(--luv none none none / none)'),
        # Test percent ranges
        ('color(--luv 0% 0% 0%)', 'color(--luv 0 0 0)'),
        ('color(--luv 100% 100% 100%)', 'color(--luv 100 215 215)'),
        ('color(--luv -100% -100% -100%)', 'color(--luv -100 -215 -215)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('luv'), Color(color2))


class TestLuvSerialize(util.ColorAssertsPyTest):
    """Test Luv serialization."""

    COLORS = [
        # Test color
        ('color(--luv 75 10 -10 / 0.5)', {}, 'color(--luv 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--luv 75 10 -10)', {'alpha': True}, 'color(--luv 75 10 -10 / 1)'),
        ('color(--luv 75 10 -10 / 0.5)', {'alpha': False}, 'color(--luv 75 10 -10)'),
        # Test None
        ('color(--luv none 10 -10)', {}, 'color(--luv 0 10 -10)'),
        ('color(--luv none 10 -10)', {'none': True}, 'color(--luv none 10 -10)'),
        # Test Fit (not bound)
        ('color(--luv 120 10 -10)', {}, 'color(--luv 120 10 -10)'),
        ('color(--luv 120 10 -10)', {'fit': False}, 'color(--luv 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestLuvProperties(util.ColorAsserts, unittest.TestCase):
    """Test Luv."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--luv 90% 50 -20 / 1)')
        self.assertEqual(c['lightness'], 90)
        c['lightness'] = 80
        self.assertEqual(c['lightness'], 80)

    def test_u(self):
        """Test `u`."""

        c = Color('color(--luv 90% 50 -20 / 1)')
        self.assertEqual(c['u'], 50)
        c['u'] = 40
        self.assertEqual(c['u'], 40)

    def test_v(self):
        """Test `v`."""

        c = Color('color(--luv 90% 50 -20 / 1)')
        self.assertEqual(c['v'], -20)
        c['v'] = -10
        self.assertEqual(c['v'], -10)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--luv 90% 50 -20 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('luv', [30, 0, 0]).is_achromatic(), True)
        self.assertEqual(Color('luv', [30, 0.000001, 0]).is_achromatic(), True)
        self.assertEqual(Color('luv', [NaN, 0.00001, 0]).is_achromatic(), True)
        self.assertEqual(Color('luv', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('luv', [0, 30, -40]).is_achromatic(), True)
        self.assertEqual(Color('luv', [NaN, 0, -30]).is_achromatic(), True)
        self.assertEqual(Color('luv', [30, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('luv', [NaN, NaN, 0]).is_achromatic(), True)
