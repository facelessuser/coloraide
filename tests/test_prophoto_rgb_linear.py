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
        ('black', 'color(--prophoto-rgb-linear 0 0 0)'),
        # Test CSS color
        ('color(--prophoto-rgb-linear 0 0.50196 0)', 'color(--prophoto-rgb-linear 0 0.50196 0)'),
        ('color(--prophoto-rgb-linear 0 0.50196 0 / 0.5)', 'color(--prophoto-rgb-linear 0 0.50196 0 / 0.5)'),
        ('color(--prophoto-rgb-linear 50% 50% 50% / 50%)', 'color(--prophoto-rgb-linear 0.5 0.5 0.5 / 0.5)'),
        ('color(--prophoto-rgb-linear none none none / none)', 'color(--prophoto-rgb-linear none none none / none)'),
        # Test range
        ('color(--prophoto-rgb-linear 0% 0% 0%)', 'color(--prophoto-rgb-linear 0 0 0)'),
        ('color(--prophoto-rgb-linear 100% 100% 100%)', 'color(--prophoto-rgb-linear 1 1 1)'),
        ('color(--prophoto-rgb-linear -100% -100% -100%)', 'color(--prophoto-rgb-linear -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('prophoto-rgb-linear'), Color(color2))


class TestLinearProPhotoRGBSerialize(util.ColorAssertsPyTest):
    """Test Linear ProPhoto RGB serialization."""

    COLORS = [
        # Test color
        ('color(--prophoto-rgb-linear 0 0.3 0.75 / 0.5)', {}, 'color(--prophoto-rgb-linear 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--prophoto-rgb-linear 0 0.3 0.75)', {'alpha': True}, 'color(--prophoto-rgb-linear 0 0.3 0.75 / 1)'),
        ('color(--prophoto-rgb-linear 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--prophoto-rgb-linear 0 0.3 0.75)'),
        # Test None
        ('color(--prophoto-rgb-linear none 0.3 0.75)', {}, 'color(--prophoto-rgb-linear 0 0.3 0.75)'),
        ('color(--prophoto-rgb-linear none 0.3 0.75)', {'none': True}, 'color(--prophoto-rgb-linear none 0.3 0.75)'),
        # Test Fit
        ('color(--prophoto-rgb-linear 1.2 0.2 0)', {}, 'color(--prophoto-rgb-linear 1 0.24172 0.01194)'),
        ('color(--prophoto-rgb-linear 1.2 0.2 0)', {'fit': False}, 'color(--prophoto-rgb-linear 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


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
