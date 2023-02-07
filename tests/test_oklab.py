"""Test Oklab library."""
import unittest
from . import util
from coloraide import Color as Color
import pytest


class TestsOklab(util.ColorAssertsPyTest):
    """Test Oklab."""

    COLORS = [
        ('red', 'color(--oklab 0.62796 0.22486 0.12585)'),
        ('orange', 'color(--oklab 0.79269 0.05661 0.16138)'),
        ('yellow', 'color(--oklab 0.96798 -0.07137 0.19857)'),
        ('green', 'color(--oklab 0.51975 -0.1403 0.10768)'),
        ('blue', 'color(--oklab 0.45201 -0.03246 -0.31153)'),
        ('indigo', 'color(--oklab 0.33898 0.09416 -0.15255)'),
        ('violet', 'color(--oklab 0.7619 0.15647 -0.1008)'),
        ('white', 'color(--oklab 1 0 0)'),
        ('gray', 'color(--oklab 0.59987 0 0)'),
        ('black', 'color(--oklab 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('oklab'), Color(color2), color=True)


class TestOklabProperties(util.ColorAsserts, unittest.TestCase):
    """Test Oklab."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--oklab 1 0.2 -0.3 / 1)')
        self.assertEqual(c['lightness'], 1)
        c['lightness'] = 0.2
        self.assertEqual(c['lightness'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--oklab 1 0.2 -0.3 / 1)')
        self.assertEqual(c['a'], 0.2)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--oklab 1 0.2 -0.3 / 1)')
        self.assertEqual(c['b'], -0.3)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--oklab 1 0.2 -0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
