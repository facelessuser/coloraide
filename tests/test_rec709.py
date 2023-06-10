"""Test Rec.709 library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestRec709(util.ColorAssertsPyTest):
    """Test Rec. 709."""

    COLORS = [
        ('red', 'color(--rec709 1 0 0)'),
        ('orange', 'color(--rec709 1 0.60889 0)'),
        ('yellow', 'color(--rec709 1 1 0)'),
        ('green', 'color(--rec709 0 0.45228 0)'),
        ('blue', 'color(--rec709 0 0 1)'),
        ('indigo', 'color(--rec709 0.23389 0 0.46067)'),
        ('violet', 'color(--rec709 0.92519 0.46067 0.92519)'),
        ('white', 'color(--rec709 1 1 1)'),
        ('gray', 'color(--rec709 0.45228 0.45228 0.45228)'),
        ('black', 'color(--rec709 0 0 0)'),
        # Test CSS color
        ('color(--rec709 0 0.50196 0)', 'color(--rec709 0 0.50196 0)'),
        ('color(--rec709 0 0.50196 0 / 0.5)', 'color(--rec709 0 0.50196 0 / 0.5)'),
        ('color(--rec709 50% 50% 50% / 50%)', 'color(--rec709 0.5 0.5 0.5 / 0.5)'),
        ('color(--rec709 none none none / none)', 'color(--rec709 none none none / none)'),
        # Test range
        ('color(--rec709 0% 0% 0%)', 'color(--rec709 0 0 0)'),
        ('color(--rec709 100% 100% 100%)', 'color(--rec709 1 1 1)'),
        ('color(--rec709 -100% -100% -100%)', 'color(--rec709 -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('rec709'), Color(color2))


class TestRec709Serialize(util.ColorAssertsPyTest):
    """Test Rec. 709 serialization."""

    COLORS = [
        # Test color
        ('color(--rec709 0 0.3 0.75 / 0.5)', {}, 'color(--rec709 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--rec709 0 0.3 0.75)', {'alpha': True}, 'color(--rec709 0 0.3 0.75 / 1)'),
        ('color(--rec709 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--rec709 0 0.3 0.75)'),
        # Test None
        ('color(--rec709 none 0.3 0.75)', {}, 'color(--rec709 0 0.3 0.75)'),
        ('color(--rec709 none 0.3 0.75)', {'none': True}, 'color(--rec709 none 0.3 0.75)'),
        # Test Fit
        ('color(--rec709 1.2 0.2 0)', {}, 'color(--rec709 1 0.37235 0.18769)'),
        ('color(--rec709 1.2 0.2 0)', {'fit': False}, 'color(--rec709 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestRec709Properties(util.ColorAsserts, unittest.TestCase):
    """Test Rec709."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(--rec709 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(--rec709 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(--rec709 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--rec709 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
