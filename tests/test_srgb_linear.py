"""Test sRGB Linear library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestsRGBLinear(util.ColorAssertsPyTest):
    """Test sRGB Linear."""

    COLORS = [
        ('red', 'color(srgb-linear 1 0 0)'),
        ('orange', 'color(srgb-linear 1 0.37626 0)'),
        ('yellow', 'color(srgb-linear 1 1 0)'),
        ('green', 'color(srgb-linear 0 0.21586 0)'),
        ('blue', 'color(srgb-linear 0 0 1)'),
        ('indigo', 'color(srgb-linear 0.07036 0 0.22323)'),
        ('violet', 'color(srgb-linear 0.85499 0.22323 0.85499)'),
        ('white', 'color(srgb-linear 1 1 1)'),
        ('gray', 'color(srgb-linear 0.21586 0.21586 0.21586)'),
        ('black', 'color(srgb-linear 0 0 0)'),
        # Test CSS color
        ('color(srgb-linear 0 0.50196 0)', 'color(srgb-linear 0 0.50196 0)'),
        ('color(srgb-linear 0 0.50196 0 / 0.5)', 'color(srgb-linear 0 0.50196 0 / 0.5)'),
        ('color(srgb-linear 50% 50% 50% / 50%)', 'color(srgb-linear 0.5 0.5 0.5 / 0.5)'),
        ('color(srgb-linear none none none / none)', 'color(srgb-linear none none none / none)'),
        # Test range
        ('color(srgb-linear 0% 0% 0%)', 'color(srgb-linear 0 0 0)'),
        ('color(srgb-linear 100% 100% 100%)', 'color(srgb-linear 1 1 1)'),
        ('color(srgb-linear -100% -100% -100%)', 'color(srgb-linear -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('srgb-linear'), Color(color2))


class TestLinearsRGBSerialize(util.ColorAssertsPyTest):
    """Test Linear sRGB serialization."""

    COLORS = [
        # Test color
        ('color(srgb-linear 0 0.3 0.75 / 0.5)', {}, 'color(srgb-linear 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(srgb-linear 0 0.3 0.75)', {'alpha': True}, 'color(srgb-linear 0 0.3 0.75 / 1)'),
        ('color(srgb-linear 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(srgb-linear 0 0.3 0.75)'),
        # Test None
        ('color(srgb-linear none 0.3 0.75)', {}, 'color(srgb-linear 0 0.3 0.75)'),
        ('color(srgb-linear none 0.3 0.75)', {'none': True}, 'color(srgb-linear none 0.3 0.75)'),
        # Test Fit
        ('color(srgb-linear 1.2 0.2 0)', {}, 'color(srgb-linear 1 0.22803 0.02349)'),
        ('color(srgb-linear 1.2 0.2 0)', {'fit': False}, 'color(srgb-linear 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestsRGBLinearProperties(util.ColorAsserts, unittest.TestCase):
    """Test sRGB Linear properties."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(srgb-linear 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(srgb-linear 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(srgb-linear 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(srgb-linear 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
