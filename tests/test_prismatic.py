"""Test Prismatic."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestPrismatic(util.ColorAssertsPyTest):
    """Test Prismatic."""

    COLORS = [
        ('red', 'color(--prismatic 1 1 0 0)'),
        ('orange', 'color(--prismatic 1 0.60714 0.39286 0)'),
        ('yellow', 'color(--prismatic 1 0.5 0.5 0)'),
        ('green', 'color(--prismatic 0.50196 0 1 0)'),
        ('blue', 'color(--prismatic 1 0 0 1)'),
        ('indigo', 'color(--prismatic 0.5098 0.36585 0 0.63415)'),
        ('violet', 'color(--prismatic 0.93333 0.39274 0.21452 0.39274)'),
        ('white', 'color(--prismatic 1 0.33333 0.33333 0.33333)'),
        ('gray', 'color(--prismatic 0.50196 0.33333 0.33333 0.33333)'),
        ('black', 'color(--prismatic 0 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_prismatic_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('prismatic'), Color(color2))


class TestPrismaticPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Prismatic."""

    def test_l(self):
        """Test `l`."""

        c = Color('color(--prismatic 1 0.5 0.5 0)')
        self.assertEqual(c['l'], 1)
        c['l'] = 0.2
        self.assertEqual(c['l'], 0.2)

    def test_r(self):
        """Test `r`."""

        c = Color('color(--prismatic 1 0.5 0.5 0)')
        self.assertEqual(c['r'], 0.5)
        c['r'] = 0.1
        self.assertEqual(c['r'], 0.1)

    def test_g(self):
        """Test `g`."""

        c = Color('color(--prismatic 1 0.5 0.5 0)')
        self.assertEqual(c['g'], 0.5)
        c['g'] = 0.1
        self.assertEqual(c['g'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--prismatic 1 0.5 0.5 0)')
        self.assertEqual(c['b'], 0)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--prismatic 1 0.5 0.5 0)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
