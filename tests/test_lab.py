"""Test Lab library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestLab(util.ColorAssertsPyTest):
    """Test Lab."""

    COLORS = [
        ('red', 'color(--lab 54.291 80.805 69.891)'),
        ('orange', 'color(--lab 75.59 27.516 79.121)'),
        ('yellow', 'color(--lab 97.607 -15.75 93.394)'),
        ('green', 'color(--lab 46.278 -47.552 48.586)'),
        ('blue', 'color(--lab 29.568 68.287 -112.03)'),
        ('indigo', 'color(--lab 19.715 47.029 -54.278)'),
        ('violet', 'color(--lab 69.618 53.295 -36.538)'),
        ('white', 'color(--lab 100 0 0)'),
        ('gray', 'color(--lab 53.585 0 0)'),
        ('black', 'color(--lab 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('lab'), Color(color2), color=True)


class TestLabProperties(util.ColorAsserts, unittest.TestCase):
    """Test Lab."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--lab 90% 50 -20 / 1)')
        self.assertEqual(c['lightness'], 90)
        c['lightness'] = 80
        self.assertEqual(c['lightness'], 80)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--lab 90% 50 -20 / 1)')
        self.assertEqual(c['a'], 50)
        c['a'] = 40
        self.assertEqual(c['a'], 40)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--lab 90% 50 -20 / 1)')
        self.assertEqual(c['b'], -20)
        c['b'] = -10
        self.assertEqual(c['b'], -10)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--lab 90% 50 -20 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
