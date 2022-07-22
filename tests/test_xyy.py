"""Test xyY."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestxyY(util.ColorAssertsPyTest):
    """Test xyY."""

    COLORS = [
        ('red', 'color(--xyy 0.64 0.33 0.21264)'),
        ('orange', 'color(--xyy 0.50047 0.4408 0.48173)'),
        ('yellow', 'color(--xyy 0.41931 0.50526 0.92781)'),
        ('green', 'color(--xyy 0.3 0.6 0.15438)'),
        ('blue', 'color(--xyy 0.15 0.06 0.07219)'),
        ('indigo', 'color(--xyy 0.22077 0.09899 0.03108)'),
        ('violet', 'color(--xyy 0.31788 0.21844 0.40317)'),
        ('white', 'color(--xyy 0.3127 0.329 1)'),
        ('gray', 'color(--xyy 0.3127 0.329 0.21586)'),
        ('black', 'color(--xyy 0.3127 0.329 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_xyy_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('xyy'), Color(color2))


class TestxyYPoperties(util.ColorAsserts, unittest.TestCase):
    """Test xyY."""

    def test_x(self):
        """Test `x`."""

        c = Color('color(--xyy 0.41931 0.50526 0.92781)')
        self.assertEqual(c['x'], 0.41931)
        c['x'] = 0.2
        self.assertEqual(c['x'], 0.2)

    def test_y(self):
        """Test `y`."""

        c = Color('color(--xyy 0.41931 0.50526 0.92781)')
        self.assertEqual(c['y'], 0.50526)
        c['y'] = 0.1
        self.assertEqual(c['y'], 0.1)

    def test_Y(self):
        """Test `Y`."""

        c = Color('color(--xyy 0.41931 0.50526 0.92781)')
        self.assertEqual(c['Y'], 0.92781)
        c['Y'] = 0.1
        self.assertEqual(c['Y'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--xyy 0.41931 0.50526 0.92781)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
