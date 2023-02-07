"""Test Luv library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
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
        ('black', 'color(--luv 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('luv'), Color(color2))


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
