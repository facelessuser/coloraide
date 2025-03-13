"""Test Oklrab library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
from coloraide import NaN
import pytest


class TestsOklrab(util.ColorAssertsPyTest):
    """Test Oklrab."""

    COLORS = [
        # Test general conversion
        ('red', 'color(--oklrab 0.56808 0.22486 0.12585)'),
        ('orange', 'color(--oklrab 0.75883 0.05661 0.16138)'),
        ('yellow', 'color(--oklrab 0.9627 -0.07137 0.19857)'),
        ('green', 'color(--oklrab 0.44371 -0.1403 0.10768)'),
        ('blue', 'color(--oklrab 0.36657 -0.03246 -0.31153)'),
        ('indigo', 'color(--oklrab 0.24043 0.09416 -0.15255)'),
        ('violet', 'color(--oklrab 0.7231 0.15647 -0.1008)'),
        ('white', 'color(--oklrab 1 0 0)'),
        ('gray', 'color(--oklrab 0.53571 0 0)'),
        ('black', 'color(--oklrab 0 0 0)'),
        # Test color
        ('color(--oklrab 1 0.1 -0.1)', 'color(--oklrab 1 0.1 -0.1)'),
        ('color(--oklrab 1 0.1 -0.1 / 0.5)', 'color(--oklrab 1 0.1 -0.1 / 0.5)'),
        ('color(--oklrab 50% 50% -50% / 50%)', 'color(--oklrab 0.5 0.2 -0.2 / 0.5)'),
        ('color(--oklrab none none none / none)', 'color(--oklrab none none none / none)'),
        # Test percent ranges
        ('color(--oklrab 0% 0% 0%)', 'color(--oklrab 0 0 0)'),
        ('color(--oklrab 100% 100% 100%)', 'color(--oklrab 1 0.4 0.4)'),
        ('color(--oklrab -100% -100% -100%)', 'color(--oklrab -1 -0.4 -0.4)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        if color2 is None:
            with pytest.raises(ValueError):
                Color(color1)
        else:
            self.assertColorEqual(Color(color1).convert('oklrab'), Color(color2), color=True)


class TestOklrabSerialize(util.ColorAssertsPyTest):
    """Test Oklrab serialization."""

    COLORS = [
        # Test no options
        ('color(--oklrab 0.75 0.1 -0.1)', {}, 'color(--oklrab 0.75 0.1 -0.1)'),
        # Test alpha
        ('color(--oklrab 0.75 0.1 -0.1 / 0.5)', {}, 'color(--oklrab 0.75 0.1 -0.1 / 0.5)'),
        ('color(--oklrab 0.75 0.1 -0.1)', {'alpha': True}, 'color(--oklrab 0.75 0.1 -0.1 / 1)'),
        ('color(--oklrab 0.75 0.1 -0.1 / 0.5)', {'alpha': False}, 'color(--oklrab 0.75 0.1 -0.1)'),
        # Test percent
        ('color(--oklrab 0.5 0.2 -0.2)', {'percent': True}, 'color(--oklrab 50% 50% -50%)'),
        ('color(--oklrab 0.5 0.2 -0.2 / 0.5)', {'percent': True, 'alpha': True}, 'color(--oklrab 50% 50% -50% / 0.5)'),
        # Test None
        ('color(--oklrab none 0.1 -0.1)', {}, 'color(--oklrab 0 0.1 -0.1)'),
        ('color(--oklrab none 0.1 -0.1)', {'none': True}, 'color(--oklrab none 0.1 -0.1)'),
        # Test fit (not bound)
        ('color(--oklrab 0.2 0.5 0)', {}, 'color(--oklrab 0.2 0.5 0)'),
        ('color(--oklrab 0.2 0.5 0)', {'fit': False}, 'color(--oklrab 0.2 0.5 0)'),
        # Test color
        ('color(--oklrab none 0.1 -0.1 / 0.5)', {'color': True}, 'color(--oklrab 0 0.1 -0.1 / 0.5)'),
        ('color(--oklrab none 0.1 -0.1)', {'color': True, 'none': True}, 'color(--oklrab none 0.1 -0.1)'),
        ('color(--oklrab 0 0.1 -0.1)', {'color': True, 'alpha': True}, 'color(--oklrab 0 0.1 -0.1 / 1)'),
        ('color(--oklrab 0 0.1 -0.1 / 0.5)', {'color': True, 'alpha': False}, 'color(--oklrab 0 0.1 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestOklrabProperties(util.ColorAsserts, unittest.TestCase):
    """Test Oklab."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--oklrab 1 0.2 -0.3 / 1)')
        self.assertEqual(c['lightness'], 1)
        c['lightness'] = 0.2
        self.assertEqual(c['lightness'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--oklrab 1 0.2 -0.3 / 1)')
        self.assertEqual(c['a'], 0.2)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--oklrab 1 0.2 -0.3 / 1)')
        self.assertEqual(c['b'], -0.3)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--oklrab 1 0.2 -0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('oklrab', [0.3, 0, 0]).is_achromatic(), True)
        self.assertEqual(Color('oklrab', [-0.3, 0, 0]).is_achromatic(), True)
        self.assertEqual(Color('oklrab', [0.3, 0.0000001, 0]).is_achromatic(), True)
        self.assertEqual(Color('oklrab', [NaN, 0.0000001, 0]).is_achromatic(), True)
        self.assertEqual(Color('oklrab', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('oklrab', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('oklrab', [0, 0.3, -0.4]).is_achromatic(), False)
        self.assertEqual(Color('oklrab', [NaN, 0, -0.3]).is_achromatic(), False)
        self.assertEqual(Color('oklrab', [0.3, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('oklrab', [NaN, NaN, 0]).is_achromatic(), True)
