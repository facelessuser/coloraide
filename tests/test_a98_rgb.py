"""Test A98 RGB library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestA98RGB(util.ColorAssertsPyTest):
    """Test A98 RGB."""

    COLORS = [
        ('red', 'color(a98-rgb 0.85859 0 0)'),
        ('orange', 'color(a98-rgb 0.91489 0.64117 0.15031)'),
        ('yellow', 'color(a98-rgb 1 1 0.23442)'),
        ('green', 'color(a98-rgb 0.28137 0.49802 0.11675)'),
        ('blue', 'color(a98-rgb 0 0 0.98107)'),
        ('indigo', 'color(a98-rgb 0.25684 0 0.4961)'),
        ('violet', 'color(a98-rgb 0.83635 0.50567 0.91826)'),
        ('white', 'color(a98-rgb 1 1 1)'),
        ('gray', 'color(a98-rgb 0.49802 0.49802 0.49802)'),
        ('black', 'color(a98-rgb 0 0 0)'),
        # Test CSS color
        ('color(a98-rgb 0 0.50196 0)', 'color(a98-rgb 0 0.50196 0)'),
        ('color(a98-rgb 0 0.50196 0 / 0.5)', 'color(a98-rgb 0 0.50196 0 / 0.5)'),
        ('color(a98-rgb 50% 50% 50% / 50%)', 'color(a98-rgb 0.5 0.5 0.5 / 0.5)'),
        ('color(a98-rgb none none none / none)', 'color(a98-rgb none none none / none)'),
        # Test range
        ('color(a98-rgb 0% 0% 0%)', 'color(a98-rgb 0 0 0)'),
        ('color(a98-rgb 100% 100% 100%)', 'color(a98-rgb 1 1 1)'),
        ('color(a98-rgb -100% -100% -100%)', 'color(a98-rgb -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('a98-rgb'), Color(color2))


class TestA98RGBSerialize(util.ColorAssertsPyTest):
    """Test A98 RGB serialization."""

    COLORS = [
        # Test color
        ('color(a98-rgb 0 0.3 0.75 / 0.5)', {}, 'color(a98-rgb 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(a98-rgb 0 0.3 0.75)', {'alpha': True}, 'color(a98-rgb 0 0.3 0.75 / 1)'),
        ('color(a98-rgb 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(a98-rgb 0 0.3 0.75)'),
        # Test None
        ('color(a98-rgb none 0.3 0.75)', {}, 'color(a98-rgb 0 0.3 0.75)'),
        ('color(a98-rgb none 0.3 0.75)', {'none': True}, 'color(a98-rgb none 0.3 0.75)'),
        # Test Fit
        ('color(a98-rgb 1.2 0.2 0)', {}, 'color(a98-rgb 1 0.48449 0.33234)'),
        ('color(a98-rgb 1.2 0.2 0)', {'fit': False}, 'color(a98-rgb 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestA98RGBProperties(util.ColorAsserts, unittest.TestCase):
    """Test A98 RGB."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(a98-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(a98-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(a98-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(a98-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
