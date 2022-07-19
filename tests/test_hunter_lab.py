"""Test Hunter Lab."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestHunterLab(util.ColorAssertsPyTest):
    """Test Hunter Lab."""

    COLORS = [
        ('red', 'color(--hunter-lab 46.113 82.672 28.408)'),
        ('orange', 'color(--hunter-lab 69.407 23.266 40.946)'),
        ('yellow', 'color(--hunter-lab 96.323 -21.054 55.869)'),
        ('green', 'color(--hunter-lab 39.291 -32.086 22.368)'),
        ('blue', 'color(--hunter-lab 26.869 75.478 -200.29)'),
        ('indigo', 'color(--hunter-lab 17.629 40.896 -62.916)'),
        ('violet', 'color(--hunter-lab 63.496 58.109 -40.51)'),
        ('white', 'color(--hunter-lab 100 0 0)'),
        ('gray', 'color(--hunter-lab 46.461 0 0)'),
        ('black', 'color(--hunter-lab 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_hunter_lab_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hunter-lab'), Color(color2))


class TestHunterLabPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Hunter Lab."""

    def test_l(self):
        """Test `l`."""

        c = Color('color(--hunter-lab 96.323 -21.06 55.728)')
        self.assertEqual(c['l'], 96.323)
        c['l'] = 0.2
        self.assertEqual(c['l'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--hunter-lab 96.323 -21.06 55.728)')
        self.assertEqual(c['a'], -21.06)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--hunter-lab 96.323 -21.06 55.728)')
        self.assertEqual(c['b'], 55.728)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hunter-lab 96.323 -21.06 55.728)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
