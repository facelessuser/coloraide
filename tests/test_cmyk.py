"""Test CMYK."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestCMYK(util.ColorAssertsPyTest):
    """Test CMYK."""

    COLORS = [
        ('red', 'color(--cmyk 0 1 1 0)'),
        ('orange', 'color(--cmyk 0 0.35294 1 0)'),
        ('yellow', 'color(--cmyk 0 0 1 0)'),
        ('green', 'color(--cmyk 1 0 1 0.49804)'),
        ('blue', 'color(--cmyk 1 1 0 0)'),
        ('indigo', 'color(--cmyk 0.42308 1 0 0.4902)'),
        ('violet', 'color(--cmyk 0 0.45378 0 0.06667)'),
        ('white', 'color(--cmyk 0 0 0 0)'),
        ('gray', 'color(--cmyk 0 0 0 0.49804)'),
        ('black', 'color(--cmyk 0 0 0 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_cmyk_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cmyk'), Color(color2))


class TestCMYKPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CMYK."""

    def test_c(self):
        """Test `c`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['c'], 0)
        c['c'] = 0.2
        self.assertEqual(c['c'], 0.2)

    def test_m(self):
        """Test `m`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['m'], 0)
        c['m'] = 0.1
        self.assertEqual(c['m'], 0.1)

    def test_y(self):
        """Test `y`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['y'], 1)
        c['y'] = 0.1
        self.assertEqual(c['y'], 0.1)

    def test_k(self):
        """Test `k`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['k'], 0)
        c['k'] = 0.1
        self.assertEqual(c['k'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
