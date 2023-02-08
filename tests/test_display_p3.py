"""Test Display P3 library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestDisplayP3(util.ColorAssertsPyTest):
    """Test Display P3."""

    COLORS = [
        ('red', 'color(display-p3 0.91749 0.20029 0.13856)'),
        ('orange', 'color(display-p3 0.94965 0.6629 0.23297)'),
        ('yellow', 'color(display-p3 1 1 0.3309)'),
        ('green', 'color(display-p3 0.21604 0.49418 0.13151)'),
        ('blue', 'color(display-p3 0 0 0.95959)'),
        ('indigo', 'color(display-p3 0.26681 0.03018 0.48951)'),
        ('violet', 'color(display-p3 0.87709 0.53133 0.91095)'),
        ('white', 'color(display-p3 1 1 1)'),
        ('gray', 'color(display-p3 0.50196 0.50196 0.50196)'),
        ('black', 'color(display-p3 0 0 0)'),
        # Test CSS color
        ('color(display-p3 0 0.50196 0)', 'color(display-p3 0 0.50196 0)'),
        ('color(display-p3 0 0.50196 0 / 0.5)', 'color(display-p3 0 0.50196 0 / 0.5)'),
        ('color(display-p3 50% 50% 50% / 50%)', 'color(display-p3 0.5 0.5 0.5 / 0.5)'),
        ('color(display-p3 none none none / none)', 'color(display-p3 none none none / none)'),
        # Test range
        ('color(display-p3 0% 0% 0%)', 'color(display-p3 0 0 0)'),
        ('color(display-p3 100% 100% 100%)', 'color(display-p3 1 1 1)'),
        ('color(display-p3 -100% -100% -100%)', 'color(display-p3 -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('display-p3'), Color(color2))


class TestDisplayP3Serialize(util.ColorAssertsPyTest):
    """Test Display P3 serialization."""

    COLORS = [
        # Test color
        ('color(display-p3 0 0.3 0.75 / 0.5)', {}, 'color(display-p3 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(display-p3 0 0.3 0.75)', {'alpha': True}, 'color(display-p3 0 0.3 0.75 / 1)'),
        ('color(display-p3 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(display-p3 0 0.3 0.75)'),
        # Test None
        ('color(display-p3 none 0.3 0.75)', {}, 'color(display-p3 0 0.3 0.75)'),
        ('color(display-p3 none 0.3 0.75)', {'none': True}, 'color(display-p3 none 0.3 0.75)'),
        # Test Fit
        ('color(display-p3 1.2 0.2 0)', {}, 'color(display-p3 1 0.44338 0.20739)'),
        ('color(display-p3 1.2 0.2 0)', {'fit': False}, 'color(display-p3 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestDisplayP3Properties(util.ColorAsserts, unittest.TestCase):
    """Test Display P3."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(display-p3 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(display-p3 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(display-p3 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(display-p3 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
