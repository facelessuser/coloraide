"""Test XYZ library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestXYZD50(util.ColorAssertsPyTest):
    """Test XYZ D50."""

    COLORS = [
        ('red', 'color(xyz-d50 0.43607 0.22249 0.01392)'),
        ('orange', 'color(xyz-d50 0.58098 0.49223 0.05045)'),
        ('yellow', 'color(xyz-d50 0.82122 0.93938 0.11101)'),
        ('green', 'color(xyz-d50 0.08314 0.15475 0.02096)'),
        ('blue', 'color(xyz-d50 0.14308 0.06062 0.7141)'),
        ('indigo', 'color(xyz-d50 0.06262 0.02919 0.16039)'),
        ('violet', 'color(xyz-d50 0.58114 0.40209 0.64413)'),
        ('white', 'color(xyz-d50 0.9643 1 0.8251)'),
        ('gray', 'color(xyz-d50 0.20815 0.21586 0.17811)'),
        ('black', 'color(xyz-d50 0 0 0)'),
        # Test CSS color
        ('color(xyz-d50 0 0.50196 0)', 'color(xyz-d50 0 0.50196 0)'),
        ('color(xyz-d50 0 0.50196 0 / 0.5)', 'color(xyz-d50 0 0.50196 0 / 0.5)'),
        ('color(xyz-d50 50% 50% 50% / 50%)', 'color(xyz-d50 0.5 0.5 0.5 / 0.5)'),
        ('color(xyz-d50 none none none / none)', 'color(xyz-d50 none none none / none)'),
        # Test range
        ('color(xyz-d50 0% 0% 0%)', 'color(xyz-d50 0 0 0)'),
        ('color(xyz-d50 100% 100% 100%)', 'color(xyz-d50 1 1 1)'),
        ('color(xyz-d50 -100% -100% -100%)', 'color(xyz-d50 -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('xyz-d50'), Color(color2))


class TestXYZD50Serialize(util.ColorAssertsPyTest):
    """Test XYZ D50 serialization."""

    COLORS = [
        # Test color
        ('color(xyz-d50 0 0.3 0.75 / 0.5)', {}, 'color(xyz-d50 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(xyz-d50 0 0.3 0.75)', {'alpha': True}, 'color(xyz-d50 0 0.3 0.75 / 1)'),
        ('color(xyz-d50 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(xyz-d50 0 0.3 0.75)'),
        # Test None
        ('color(xyz-d50 none 0.3 0.75)', {}, 'color(xyz-d50 0 0.3 0.75)'),
        ('color(xyz-d50 none 0.3 0.75)', {'none': True}, 'color(xyz-d50 none 0.3 0.75)'),
        # Test Fit (not bound)
        ('color(xyz-d50 1.2 0.2 0)', {}, 'color(xyz-d50 1.2 0.2 0)'),
        ('color(xyz-d50 1.2 0.2 0)', {'fit': False}, 'color(xyz-d50 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestXYZProperties(util.ColorAsserts, unittest.TestCase):
    """Test XYZ."""

    def test_x(self):
        """Test `x`."""

        c = Color('color(xyz-d50 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['x'], 0.1)
        c['x'] = 0.2
        self.assertEqual(c['x'], 0.2)

    def test_y(self):
        """Test `y`."""

        c = Color('color(xyz-d50 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['y'], 0.2)
        c['y'] = 0.1
        self.assertEqual(c['y'], 0.1)

    def test_z(self):
        """Test `z`."""

        c = Color('color(xyz-d50 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['z'], 0.3)
        c['z'] = 0.1
        self.assertEqual(c['z'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(xyz-d50 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
