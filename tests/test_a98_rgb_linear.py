"""Test Linear A98 RGB."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestLinearA98RGB(util.ColorAssertsPyTest):
    """Test Linear A98 RGB."""

    COLORS = [
        ('red', 'color(--a98-rgb-linear 0.71513 0 0)'),
        ('orange', 'color(--a98-rgb-linear 0.82231 0.37626 0.01549)'),
        ('yellow', 'color(--a98-rgb-linear 1 1 0.04116)'),
        ('green', 'color(--a98-rgb-linear 0.06149 0.21586 0.00889)'),
        ('blue', 'color(--a98-rgb-linear 0 0 0.95884)'),
        ('indigo', 'color(--a98-rgb-linear 0.05032 0 0.21404)'),
        ('violet', 'color(--a98-rgb-linear 0.67502 0.22323 0.82899)'),
        ('white', 'color(--a98-rgb-linear 1 1 1)'),
        ('gray', 'color(--a98-rgb-linear 0.21586 0.21586 0.21586)'),
        ('black', 'color(--a98-rgb-linear 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('a98-rgb-linear'), Color(color2))


class TestLinearA98RGBPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Linear A98 RGB properties."""

    def test_r(self):
        """Test `r`."""

        c = Color('color(--a98-rgb-linear 0.1 0.2 0.3)')
        self.assertEqual(c['r'], 0.1)
        c['r'] = 0.2
        self.assertEqual(c['r'], 0.2)

    def test_g(self):
        """Test `g`."""

        c = Color('color(--a98-rgb-linear 0.1 0.2 0.3)')
        self.assertEqual(c['g'], 0.2)
        c['g'] = 0.1
        self.assertEqual(c['g'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--a98-rgb-linear 0.1 0.2 0.3)')
        self.assertEqual(c['b'], 0.3)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--a98-rgb-linear 0.1 0.2 0.3)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
