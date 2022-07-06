"""Test Linear ProPhoto RGB."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestLinearProPhotoRGB(util.ColorAssertsPyTest):
    """Test Linear ProPhoto RGB."""

    COLORS = [
        ('red', 'color(--prophoto-rgb-linear 0.52928 0.09837 0.01688)'),
        ('orange', 'color(--prophoto-rgb-linear 0.6535 0.42702 0.06115)'),
        ('yellow', 'color(--prophoto-rgb-linear 0.85943 0.97183 0.13453)'),
        ('green', 'color(--prophoto-rgb-linear 0.07127 0.18855 0.0254)'),
        ('blue', 'color(--prophoto-rgb-linear 0.14057 0.02817 0.86547)'),
        ('indigo', 'color(--prophoto-rgb-linear 0.06862 0.01321 0.19438)'),
        ('violet', 'color(--prophoto-rgb-linear 0.64641 0.30317 0.78066)'),
        ('white', 'color(--prophoto-rgb-linear 1 1 1)'),
        ('gray', 'color(--prophoto-rgb-linear 0.21586 0.21586 0.21586)'),
        ('black', 'color(--prophoto-rgb-linear 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('prophoto-rgb-linear'), Color(color2))


class TestLinearProPhotoRGBPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Linear ProPhoto RGB properties."""

    def test_r(self):
        """Test `r`."""

        c = Color('color(--prophoto-rgb-linear 0.1 0.2 0.3)')
        self.assertEqual(c['r'], 0.1)
        c['r'] = 0.2
        self.assertEqual(c['r'], 0.2)

    def test_g(self):
        """Test `g`."""

        c = Color('color(--prophoto-rgb-linear 0.1 0.2 0.3)')
        self.assertEqual(c['g'], 0.2)
        c['g'] = 0.1
        self.assertEqual(c['g'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--prophoto-rgb-linear 0.1 0.2 0.3)')
        self.assertEqual(c['b'], 0.3)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--prophoto-rgb-linear 0.1 0.2 0.3)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
