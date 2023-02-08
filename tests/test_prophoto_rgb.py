"""Test ProPhoto RGB library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestProPhotoRGB(util.ColorAssertsPyTest):
    """Test Linear ProPhoto RGB."""

    COLORS = [
        ('red', 'color(prophoto-rgb 0.70225 0.27572 0.10355 )'),
        ('orange', 'color(prophoto-rgb 0.78951 0.62329 0.21172 )'),
        ('yellow', 'color(prophoto-rgb 0.91929 0.98425 0.32811 )'),
        ('green', 'color(prophoto-rgb 0.23052 0.39578 0.12995 )'),
        ('blue', 'color(prophoto-rgb 0.3362 0.13765 0.92287 )'),
        ('indigo', 'color(prophoto-rgb 0.22572 0.09037 0.40254 )'),
        ('violet', 'color(prophoto-rgb 0.78474 0.51528 0.87148 )'),
        ('white', 'color(prophoto-rgb 1 1 1 )'),
        ('gray', 'color(prophoto-rgb 0.42667 0.42667 0.42667 )'),
        ('black', 'color(prophoto-rgb 0 0 0 )'),
        # Test CSS color
        ('color(prophoto-rgb 0 0.50196 0)', 'color(prophoto-rgb 0 0.50196 0)'),
        ('color(prophoto-rgb 0 0.50196 0 / 0.5)', 'color(prophoto-rgb 0 0.50196 0 / 0.5)'),
        ('color(prophoto-rgb 50% 50% 50% / 50%)', 'color(prophoto-rgb 0.5 0.5 0.5 / 0.5)'),
        ('color(prophoto-rgb none none none / none)', 'color(prophoto-rgb none none none / none)'),
        # Test range
        ('color(prophoto-rgb 0% 0% 0%)', 'color(prophoto-rgb 0 0 0)'),
        ('color(prophoto-rgb 100% 100% 100%)', 'color(prophoto-rgb 1 1 1)'),
        ('color(prophoto-rgb -100% -100% -100%)', 'color(prophoto-rgb -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('prophoto-rgb'), Color(color2))


class TestProPhotoRGBSerialize(util.ColorAssertsPyTest):
    """Test ProPhoto RGB serialization."""

    COLORS = [
        # Test color
        ('color(prophoto-rgb 0 0.3 0.75 / 0.5)', {}, 'color(prophoto-rgb 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(prophoto-rgb 0 0.3 0.75)', {'alpha': True}, 'color(prophoto-rgb 0 0.3 0.75 / 1)'),
        ('color(prophoto-rgb 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(prophoto-rgb 0 0.3 0.75)'),
        # Test None
        ('color(prophoto-rgb none 0.3 0.75)', {}, 'color(prophoto-rgb 0 0.3 0.75)'),
        ('color(prophoto-rgb none 0.3 0.75)', {'none': True}, 'color(prophoto-rgb none 0.3 0.75)'),
        # Test Fit
        ('color(prophoto-rgb 1.2 0.2 0)', {}, 'color(prophoto-rgb 1 0.36333 0.13613)'),
        ('color(prophoto-rgb 1.2 0.2 0)', {'fit': False}, 'color(prophoto-rgb 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestProPhotoRGBProperties(util.ColorAsserts, unittest.TestCase):
    """Test ProPhoto RGB."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(prophoto-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(prophoto-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(prophoto-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(prophoto-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
