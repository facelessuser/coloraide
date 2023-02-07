"""Test sRGB library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestsRGB(util.ColorAssertsPyTest):
    """Test sRGB."""

    COLORS = [
        ('red', 'color(srgb 1 0 0)'),
        ('orange', 'color(srgb 1 0.64706 0)'),
        ('yellow', 'color(srgb 1 1 0)'),
        ('green', 'color(srgb 0 0.50196 0)'),
        ('blue', 'color(srgb 0 0 1)'),
        ('indigo', 'color(srgb 0.29412 0 0.5098)'),
        ('violet', 'color(srgb 0.93333 0.5098 0.93333)'),
        ('white', 'color(srgb 1 1 1)'),
        ('gray', 'color(srgb 0.50196 0.50196 0.50196)'),
        ('black', 'color(srgb 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('srgb'), Color(color2), color=True)


class TestsRGBProperties(util.ColorAsserts, unittest.TestCase):
    """Test sRGB."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(srgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
