"""Test XYZ D65 library."""
import unittest
from . import util
from coloraide import Color
import pytest


class TestXYZD65(util.ColorAssertsPyTest):
    """Test XYZ D65."""

    COLORS = [
        ('red', 'color(xyz-d65 0.41239 0.21264 0.01933)'),
        ('orange', 'color(xyz-d65 0.54694 0.48173 0.06418)'),
        ('yellow', 'color(xyz-d65 0.76998 0.92781 0.13853)'),
        ('green', 'color(xyz-d65 0.07719 0.15438 0.02573)'),
        ('blue', 'color(xyz-d65 0.18048 0.07219 0.95053)'),
        ('indigo', 'color(xyz-d65 0.0693 0.03108 0.21355)'),
        ('violet', 'color(xyz-d65 0.58672 0.40317 0.85583)'),
        ('white', 'color(xyz-d65 0.95046 1 1.0891)'),
        ('gray', 'color(xyz-d65 0.20517 0.21586 0.23508)'),
        ('black', 'color(xyz-d65 0 0 0)'),
        # Test alternate CSS identifier
        ('color(xyz 0.95046 1 1.0891)', 'color(xyz-d65 0.95046 1 1.0891)'),
        # Test CSS color
        ('color(xyz-d65 0 0.50196 0)', 'color(xyz-d65 0 0.50196 0)'),
        ('color(xyz-d65 0 0.50196 0 / 0.5)', 'color(xyz-d65 0 0.50196 0 / 0.5)'),
        ('color(xyz-d65 50% 50% 50% / 50%)', 'color(xyz-d65 0.5 0.5 0.5 / 0.5)'),
        ('color(xyz-d65 none none none / none)', 'color(xyz-d65 none none none / none)'),
        # Test range
        ('color(xyz-d65 0% 0% 0%)', 'color(xyz-d65 0 0 0)'),
        ('color(xyz-d65 100% 100% 100%)', 'color(xyz-d65 1 1 1)'),
        ('color(xyz-d65 -100% -100% -100%)', 'color(xyz-d65 -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('xyz-d65'), Color(color2))


class TestXYZD65Serialize(util.ColorAssertsPyTest):
    """Test XYZ D65 serialization."""

    COLORS = [
        # Test color
        ('color(xyz-d65 0 0.3 0.75 / 0.5)', {}, 'color(xyz-d65 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(xyz-d65 0 0.3 0.75)', {'alpha': True}, 'color(xyz-d65 0 0.3 0.75 / 1)'),
        ('color(xyz-d65 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(xyz-d65 0 0.3 0.75)'),
        # Test None
        ('color(xyz-d65 none 0.3 0.75)', {}, 'color(xyz-d65 0 0.3 0.75)'),
        ('color(xyz-d65 none 0.3 0.75)', {'none': True}, 'color(xyz-d65 none 0.3 0.75)'),
        # Test Fit (not bound)
        ('color(xyz-d65 1.2 0.2 0)', {}, 'color(xyz-d65 1.2 0.2 0)'),
        ('color(xyz-d65 1.2 0.2 0)', {'fit': False}, 'color(xyz-d65 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestXYZD65Properties(util.ColorAsserts, unittest.TestCase):
    """Test XYZ D65."""

    def test_x(self):
        """Test `x`."""

        c = Color('color(xyz 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['x'], 0.1)
        c['x'] = 0.2
        self.assertEqual(c['x'], 0.2)

    def test_y(self):
        """Test `y`."""

        c = Color('color(xyz 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['y'], 0.2)
        c['y'] = 0.1
        self.assertEqual(c['y'], 0.1)

    def test_z(self):
        """Test `z`."""

        c = Color('color(xyz 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['z'], 0.3)
        c['z'] = 0.1
        self.assertEqual(c['z'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(xyz 0.1 0.2 0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
