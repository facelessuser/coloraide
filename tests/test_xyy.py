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
        ('black', 'color(--xyy 0.3127 0.329 0)'),
        # Test CSS color
        ('color(--xyy 0 0.50196 0)', 'color(--xyy 0 0.50196 0)'),
        ('color(--xyy 0 0.50196 0 / 0.5)', 'color(--xyy 0 0.50196 0 / 0.5)'),
        ('color(--xyy 50% 50% 50% / 50%)', 'color(--xyy 0.5 0.5 0.5 / 0.5)'),
        ('color(--xyy none none none / none)', 'color(--xyy none none none / none)'),
        # Test range
        ('color(--xyy 0% 0% 0%)', 'color(--xyy 0 0 0)'),
        ('color(--xyy 100% 100% 100%)', 'color(--xyy 1 1 1)'),
        ('color(--xyy -100% -100% -100%)', 'color(--xyy -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('xyy'), Color(color2))


class TestxyYSerialize(util.ColorAssertsPyTest):
    """Test XYZ D65 serialization."""

    COLORS = [
        # Test color
        ('color(--xyy 0 0.3 0.75 / 0.5)', {}, 'color(--xyy 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--xyy 0 0.3 0.75)', {'alpha': True}, 'color(--xyy 0 0.3 0.75 / 1)'),
        ('color(--xyy 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--xyy 0 0.3 0.75)'),
        # Test None
        ('color(--xyy none 0.3 0.75)', {}, 'color(--xyy 0 0.3 0.75)'),
        ('color(--xyy none 0.3 0.75)', {'none': True}, 'color(--xyy none 0.3 0.75)'),
        # Test Fit (not bound)
        ('color(--xyy 1.2 0.2 0)', {}, 'color(--xyy 1.2 0.2 0)'),
        ('color(--xyy 1.2 0.2 0)', {'fit': False}, 'color(--xyy 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


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
