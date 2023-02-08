"""Test ACES 2065-1."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestACES(util.ColorAssertsPyTest):
    """Test ACES 2065-1."""

    COLORS = [
        ('red', 'color(--aces2065-1 0.43963 0.08978 0.01754)'),
        ('orange', 'color(--aces2065-1 0.58374 0.39584 0.05951)'),
        ('yellow', 'color(--aces2065-1 0.82262 0.90322 0.12909)'),
        ('green', 'color(--aces2065-1 0.08267 0.17559 0.02408)'),
        ('blue', 'color(--aces2065-1 0.17738 0.09678 0.87091)'),
        ('indigo', 'color(--aces2065-1 0.07053 0.02792 0.19565)'),
        ('violet', 'color(--aces2065-1 0.61303 0.34109 0.78452)'),
        ('white', 'color(--aces2065-1 1 1 1)'),
        ('gray', 'color(--aces2065-1 0.21586 0.21586 0.21586)'),
        ('black', 'color(--aces2065-1 0 0 0)'),
        # Test CSS color
        ('color(--aces2065-1 0 0.50196 0)', 'color(--aces2065-1 0 0.50196 0)'),
        ('color(--aces2065-1 0 0.50196 0 / 0.5)', 'color(--aces2065-1 0 0.50196 0 / 0.5)'),
        ('color(--aces2065-1 50% 50% 50% / 50%)', 'color(--aces2065-1 32752 32752 32752 / 0.5)'),
        ('color(--aces2065-1 none none none / none)', 'color(--aces2065-1 none none none / none)'),
        # Test range
        ('color(--aces2065-1 0% 0% 0%)', 'color(--aces2065-1 0 0 0)'),
        ('color(--aces2065-1 100% 100% 100%)', 'color(--aces2065-1 65504 65504 65504)'),
        ('color(--aces2065-1 -100% -100% -100%)', 'color(--aces2065-1 -65504 -65504 -65504)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('aces2065-1'), Color(color2))


class TestACESSerialize(util.ColorAssertsPyTest):
    """Test ACES 2065-1 serialization."""

    COLORS = [
        # Test color
        ('color(--aces2065-1 0 0.3 0.75 / 0.5)', {}, 'color(--aces2065-1 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--aces2065-1 0 0.3 0.75)', {'alpha': True}, 'color(--aces2065-1 0 0.3 0.75 / 1)'),
        ('color(--aces2065-1 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--aces2065-1 0 0.3 0.75)'),
        # Test None
        ('color(--aces2065-1 none 0.3 0.75)', {}, 'color(--aces2065-1 0 0.3 0.75)'),
        ('color(--aces2065-1 none 0.3 0.75)', {'none': True}, 'color(--aces2065-1 none 0.3 0.75)'),
        # Test Fit
        ('color(--aces2065-1 665510 0.2 0)', {}, 'color(--aces2065-1 65504 65504 65504)'),
        ('color(--aces2065-1 665510 0.2 0)', {'fit': False}, 'color(--aces2065-1 665510 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestACESProperties(util.ColorAsserts, unittest.TestCase):
    """Test ACES 2065-1."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(--aces2065-1 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['red'], 0.1)
        c['red'] = 0.2
        self.assertEqual(c['red'], 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(--aces2065-1 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['green'], 0.2)
        c['green'] = 0.1
        self.assertEqual(c['green'], 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(--aces2065-1 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['blue'], 0.3)
        c['blue'] = 0.1
        self.assertEqual(c['blue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--aces2065-1 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
