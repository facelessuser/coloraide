"""Test ACEScg."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestACEScg(util.ColorAssertsPyTest):
    """Test ACEScg."""

    COLORS = [
        ('red', 'color(--acescg 0.6131 0.07019 0.02062)'),
        ('orange', 'color(--acescg 0.74085 0.41498 0.06184)'),
        ('yellow', 'color(--acescg 0.95262 0.98655 0.13019)'),
        ('green', 'color(--acescg 0.07329 0.1978 0.02365)'),
        ('blue', 'color(--acescg 0.04738 0.01345 0.86981)'),
        ('indigo', 'color(--acescg 0.05371 0.00794 0.19562)'),
        ('violet', 'color(--acescg 0.64049 0.27607 0.78577)'),
        ('white', 'color(--acescg 1 1 1)'),
        ('gray', 'color(--acescg 0.21586 0.21586 0.21586)'),
        ('black', 'color(--acescg 0 0 0)'),
        # Test CSS color
        ('color(--acescg 0 0.50196 0)', 'color(--acescg 0 0.50196 0)'),
        ('color(--acescg 0 0.50196 0 / 0.5)', 'color(--acescg 0 0.50196 0 / 0.5)'),
        ('color(--acescg 50% 50% 50% / 50%)', 'color(--acescg 32752 32752 32752 / 0.5)'),
        ('color(--acescg none none none / none)', 'color(--acescg none none none / none)'),
        # Test range
        ('color(--acescg 0% 0% 0%)', 'color(--acescg 0 0 0)'),
        ('color(--acescg 100% 100% 100%)', 'color(--acescg 65504 65504 65504)'),
        ('color(--acescg -100% -100% -100%)', 'color(--acescg -65504 -65504 -65504)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('acescg'), Color(color2))


class TestACEScgSerialize(util.ColorAssertsPyTest):
    """Test ACEScg serialization."""

    COLORS = [
        # Test color
        ('color(--acescg 0 0.3 0.75 / 0.5)', {}, 'color(--acescg 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--acescg 0 0.3 0.75)', {'alpha': True}, 'color(--acescg 0 0.3 0.75 / 1)'),
        ('color(--acescg 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--acescg 0 0.3 0.75)'),
        # Test None
        ('color(--acescg none 0.3 0.75)', {}, 'color(--acescg 0 0.3 0.75)'),
        ('color(--acescg none 0.3 0.75)', {'none': True}, 'color(--acescg none 0.3 0.75)'),
        # Test Fit
        ('color(--acescg 665510 0.2 0)', {}, 'color(--acescg 65504 65504 65504)'),
        ('color(--acescg 665510 0.2 0)', {'fit': False}, 'color(--acescg 665510 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestACEScgProperties(util.ColorAsserts, unittest.TestCase):
    """Test ACEScg."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(--acescg 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(--acescg 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(--acescg 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--acescg 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
