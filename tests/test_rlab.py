"""Test RLAB."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestRLAB(util.ColorAssertsPyTest):
    """Test RLAB."""

    COLORS = [
        ('red', 'color(--rlab 51.012 79.742 57.26)'),
        ('orange', 'color(--rlab 72.793 25.151 74.11)'),
        ('yellow', 'color(--rlab 96.795 -23.838 95.194)'),
        ('green', 'color(--rlab 44.382 -46.503 42.09)'),
        ('blue', 'color(--rlab 31.893 71.681 -106.02)'),
        ('indigo', 'color(--rlab 22.107 42.674 -46.135)'),
        ('violet', 'color(--rlab 67.371 58.947 -38.558)'),
        ('white', 'color(--rlab 100 0 0)'),
        ('gray', 'color(--rlab 51.346 0 0)'),
        ('black', 'color(--rlab 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_hunter_lab_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('rlab'), Color(color2))


class TestRLABPoperties(util.ColorAsserts, unittest.TestCase):
    """Test RLAB."""

    def test_l(self):
        """Test `l`."""

        c = Color('color(--rlab 96.323 -21.06 55.728)')
        self.assertEqual(c['l'], 96.323)
        c['l'] = 0.2
        self.assertEqual(c['l'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--rlab 96.323 -21.06 55.728)')
        self.assertEqual(c['a'], -21.06)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--rlab 96.323 -21.06 55.728)')
        self.assertEqual(c['b'], 55.728)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--rlab 96.323 -21.06 55.728)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
