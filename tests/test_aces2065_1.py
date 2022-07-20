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
        ('black', 'color(--aces2065-1 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('aces2065-1'), Color(color2))


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
