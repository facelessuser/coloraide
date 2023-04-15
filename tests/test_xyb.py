"""Test XYB."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestXYB(util.ColorAssertsPyTest):
    """Test XYB."""

    COLORS = [
        ('red', 'color(--xyb 0.0281 0.48819 0.01157)'),
        ('orange', 'color(--xyb 0.01132 0.64596 -0.10359)'),
        ('yellow', 'color(--xyb 0 0.81867 -0.20719)'),
        ('green', 'color(--xyb -0.0091 0.36999 -0.17163)'),
        ('blue', 'color(--xyb 0 0.27813 0.38801)'),
        ('indigo', 'color(--xyb 0.00704 0.18547 0.18989)'),
        ('violet', 'color(--xyb 0.01268 0.60656 0.15033)'),
        ('white', 'color(--xyb 0 0.84531 0)'),
        ('gray', 'color(--xyb 0 0.44741 0)'),
        ('black', 'color(--xyb 0 0 0)'),
        # Test color
        ('color(--xyb 0.5 0.1 -0.1)', 'color(--xyb 0.5 0.1 -0.1)'),
        ('color(--xyb 0.5 0.1 -0.1 / 0.5)', 'color(--xyb 0.5 0.1 -0.1 / 0.5)'),
        ('color(--xyb 50% 50% -50% / 50%)', 'color(--xyb 0.225 0.4225 -0.225 / 0.5)'),
        ('color(--xyb none none none / none)', 'color(--xyb none none none / none)'),
        # Test percent ranges
        ('color(--xyb 0% 0% 0%)', 'color(--xyb 0 0 0)'),
        ('color(--xyb 100% 100% 100%)', 'color(--xyb 0.45 0.845 0.45)'),
        ('color(--xyb -100% -100% -100%)', 'color(--xyb -0.45 -0.845 -0.45)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('xyb'), Color(color2))


class TestXYBSerialize(util.ColorAssertsPyTest):
    """Test XYB serialization."""

    COLORS = [
        # Test color
        ('color(--xyb 0.1 0.75 -0.1 / 0.5)', {}, 'color(--xyb 0.1 0.75 -0.1 / 0.5)'),
        # Test alpha
        ('color(--xyb 0.1 0.75 -0.1)', {'alpha': True}, 'color(--xyb 0.1 0.75 -0.1 / 1)'),
        ('color(--xyb 0.1 0.75 -0.1 / 0.5)', {'alpha': False}, 'color(--xyb 0.1 0.75 -0.1)'),
        # Test None
        ('color(--xyb none 0.75 -0.1)', {}, 'color(--xyb 0 0.75 -0.1)'),
        ('color(--xyb none 0.75 -0.1)', {'none': True}, 'color(--xyb none 0.75 -0.1)'),
        # Test Fit (not bound)
        ('color(--xyb 1.2 0.75 -0.1)', {}, 'color(--xyb 1.2 0.75 -0.1)'),
        ('color(--xyb 1.2 0.75 -0.1)', {'fit': False}, 'color(--xyb 1.2 0.75 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestXYBPoperties(util.ColorAsserts, unittest.TestCase):
    """Test XYB."""

    def test_x(self):
        """Test `x`."""

        c = Color('color(--xyb -0.02 0.7 0.04)')
        self.assertEqual(c['x'], -0.02)
        c['x'] = 0.1
        self.assertEqual(c['x'], 0.1)

    def test_y(self):
        """Test `y`."""

        c = Color('color(--xyb -0.02 0.7 0.04)')
        self.assertEqual(c['y'], 0.7)
        c['y'] = 0.2
        self.assertEqual(c['y'], 0.2)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--xyb -0.02 0.7 0.04)')
        self.assertEqual(c['b'], 0.04)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--xyb -0.02 0.7 0.04)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)

    def test_labish_names(self):
        """Test `labish_names`."""

        c = Color('color(--xyb -0.02 0.7 0.03 / 1)')
        self.assertEqual(c._space.names(), ('y', 'x', 'b'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('#464646').convert('xyb').is_achromatic(), True)
        self.assertEqual(Color('xyb', [NaN, 0, NaN]).is_achromatic(), True)
        self.assertEqual(Color('xyb', [0.03, 0, -0.04]).is_achromatic(), False)
        self.assertEqual(Color('xyb', [0, NaN, -0.3]).is_achromatic(), False)
        self.assertEqual(Color('xyb', [NaN, 0.3, 0]).is_achromatic(), True)
        self.assertEqual(Color('xyb', [NaN, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('xyb', [NaN, -0.5, NaN]).is_achromatic(), True)
