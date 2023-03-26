"""Test CAM16 UCS."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestCAM16CAM16(util.ColorAssertsPyTest):
    """Test CAM16."""

    COLORS = [
        ('red', 'color(--cam16 46.026 72.143 37.385)'),
        ('orange', 'color(--cam16 68.056 13.955 41.212)'),
        ('yellow', 'color(--cam16 94.682 -19.662 50.83)'),
        ('green', 'color(--cam16 33.976 -40.301 31.147)'),
        ('blue', 'color(--cam16 25.066 13.785 -60.901)'),
        ('indigo', 'color(--cam16 16.046 28.336 -32.712)'),
        ('violet', 'color(--cam16 63.507 41.066 -22.402)'),
        ('white', 'color(--cam16 100 -1.9463 -1.1026)'),
        ('gray', 'color(--cam16 43.042 -1.2764 -0.72317)'),
        ('black', 'color(--cam16 0 0 0)'),
        # Test color
        ('color(--cam16 50 10 -10)', 'color(--cam16 50 10 -10)'),
        ('color(--cam16 50 10 -10 / 0.5)', 'color(--cam16 50 10 -10 / 0.5)'),
        ('color(--cam16 50% 50% -50% / 50%)', 'color(--cam16 50 45 -45 / 0.5)'),
        ('color(--cam16 none none none / none)', 'color(--cam16 none none none / none)'),
        # Test percent ranges
        ('color(--cam16 0% 0% 0%)', 'color(--cam16 0 0 0)'),
        ('color(--cam16 100% 100% 100%)', 'color(--cam16 100 90 90)'),
        ('color(--cam16 -100% -100% -100%)', 'color(--cam16 -100 -90 -90)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam16'), Color(color2))


class TestCAM16Serialize(util.ColorAssertsPyTest):
    """Test CAM16 serialization."""

    COLORS = [
        # Test color
        ('color(--cam16 75 10 -10 / 0.5)', {}, 'color(--cam16 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--cam16 75 10 -10)', {'alpha': True}, 'color(--cam16 75 10 -10 / 1)'),
        ('color(--cam16 75 10 -10 / 0.5)', {'alpha': False}, 'color(--cam16 75 10 -10)'),
        # Test None
        ('color(--cam16 none 10 -10)', {}, 'color(--cam16 0 10 -10)'),
        ('color(--cam16 none 10 -10)', {'none': True}, 'color(--cam16 none 10 -10)'),
        # Test Fit (not bound)
        ('color(--cam16 120 10 -10)', {}, 'color(--cam16 120 10 -10)'),
        ('color(--cam16 120 10 -10)', {'fit': False}, 'color(--cam16 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestCAM16Poperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM16."""

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam16 0.51332 0.92781 1.076)')
        self.assertEqual(c['j'], 0.51332)
        c['j'] = 0.2
        self.assertEqual(c['j'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--cam16 0.51332 0.92781 1.076)')
        self.assertEqual(c['a'], 0.92781)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--cam16 0.51332 0.92781 1.076)')
        self.assertEqual(c['b'], 1.076)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam16 0.51332 0.92781 1.076)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('#222222').convert('cam16').is_achromatic(), True)
        self.assertEqual(Color('srgb', [0.000000001] * 3).convert('cam16').set('j', NaN).is_achromatic(), True)
        self.assertEqual(Color('cam16', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('cam16', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('cam16', [0, 3, -4]).is_achromatic(), True)
        self.assertEqual(Color('cam16', [NaN, 0, -3]).is_achromatic(), True)
        self.assertEqual(Color('cam16', [30, NaN, 0]).is_achromatic(), False)
        self.assertEqual(Color('cam16', [NaN, NaN, 0]).is_achromatic(), True)
