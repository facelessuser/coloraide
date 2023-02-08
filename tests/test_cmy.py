"""Test CMY."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestCMY(util.ColorAssertsPyTest):
    """Test CMY."""

    COLORS = [
        ('red', 'color(--cmy 0 1 1)'),
        ('orange', 'color(--cmy 0 0.35294 1)'),
        ('yellow', 'color(--cmy 0 0 1)'),
        ('green', 'color(--cmy 1 0.49804 1)'),
        ('blue', 'color(--cmy 1 1 0)'),
        ('indigo', 'color(--cmy 0.70588 1 0.4902)'),
        ('violet', 'color(--cmy 0.06667 0.4902 0.06667)'),
        ('white', 'color(--cmy 0 0 0)'),
        ('gray', 'color(--cmy 0.49804 0.49804 0.49804)'),
        ('black', 'color(--cmy 1 1 1)'),
        # Test CSS color
        ('color(--cmy 0 0.50196 0)', 'color(--cmy 0 0.50196 0)'),
        ('color(--cmy 0 0.50196 0 / 0.5)', 'color(--cmy 0 0.50196 0 / 0.5)'),
        ('color(--cmy 50% 50% 50% / 50%)', 'color(--cmy 0.5 0.5 0.5 / 0.5)'),
        ('color(--cmy none none none / none)', 'color(--cmy none none none / none)'),
        # Test range
        ('color(--cmy 0% 0% 0%)', 'color(--cmy 0 0 0)'),
        ('color(--cmy 100% 100% 100%)', 'color(--cmy 1 1 1)'),
        ('color(--cmy -100% -100% -100%)', 'color(--cmy -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_cmy_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cmy'), Color(color2))


class TestCMYSerialize(util.ColorAssertsPyTest):
    """Test CMY serialization."""

    COLORS = [
        # Test color
        ('color(--cmy 0 0.3 0.75 / 0.5)', {}, 'color(--cmy 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--cmy 0 0.3 0.75)', {'alpha': True}, 'color(--cmy 0 0.3 0.75 / 1)'),
        ('color(--cmy 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--cmy 0 0.3 0.75)'),
        # Test None
        ('color(--cmy none 0.3 0.75)', {}, 'color(--cmy 0 0.3 0.75)'),
        ('color(--cmy none 0.3 0.75)', {'none': True}, 'color(--cmy none 0.3 0.75)'),
        # Test Fit
        ('color(--cmy 1.2 0.2 0)', {}, 'color(--cmy 1 0.2 0)'),
        ('color(--cmy 1.2 0.2 0)', {'fit': False}, 'color(--cmy 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestCMYPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CMY."""

    def test_c(self):
        """Test `c`."""

        c = Color('color(--cmy 0 0 1)')
        self.assertEqual(c['c'], 0)
        c['c'] = 0.2
        self.assertEqual(c['c'], 0.2)

    def test_m(self):
        """Test `m`."""

        c = Color('color(--cmy 0 0 1)')
        self.assertEqual(c['m'], 0)
        c['m'] = 0.1
        self.assertEqual(c['m'], 0.1)

    def test_y(self):
        """Test `y`."""

        c = Color('color(--cmy 0 0 1)')
        self.assertEqual(c['y'], 1)
        c['y'] = 0.1
        self.assertEqual(c['y'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cmy 0 0 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
