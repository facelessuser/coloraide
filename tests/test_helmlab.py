"""Test Helmlab."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestHelmlab(util.ColorAssertsPyTest):
    """Test Helmlab."""

    COLORS = [
        ('red', 'color(--helmlab 0.7867 0.52648 -0.20295)'),
        ('orange', 'color(--helmlab 0.97103 0.50434 0.27591)'),
        ('yellow', 'color(--helmlab 1.0591 0.1304 0.49885)'),
        ('green', 'color(--helmlab 0.55229 -0.14689 0.4932)'),
        ('blue', 'color(--helmlab 0.54113 -0.37993 -0.80738)'),
        ('indigo', 'color(--helmlab 0.42572 -0.06253 -0.31316)'),
        ('violet', 'color(--helmlab 0.95228 0.03627 -0.36351)'),
        ('white', 'color(--helmlab 1.1436 0 0)'),
        ('gray', 'color(--helmlab 0.73661 0.00001 0)'),
        ('black', 'color(--helmlab 0 0 0)'),
        ('color(srgb 1.01 1.01 1.01)', 'color(--helmlab 1.1489 0 0)'),
        ('color(srgb 1e-3 1e-3 1e-3)', 'color(--helmlab 0.02563 0.02551 -0.00179)'),
        # Test color
        ('color(--helmlab 0.5 0.1 -0.1)', 'color(--helmlab 0.5 0.1 -0.1)'),
        ('color(--helmlab 0.5 0.1 -0.1 / 0.5)', 'color(--helmlab 0.5 0.1 -0.1 / 0.5)'),
        ('color(--helmlab 50% 50% -50% / 50%)', 'color(--helmlab 0.57181 0.5 -0.5 / 0.5)'),
        ('color(--helmlab none none none / none)', 'color(--helmlab none none none / none)'),
        # Test percent ranges
        ('color(--helmlab 0% 0% 0%)', 'color(--helmlab 0 0 0)'),
        ('color(--helmlab 100% 100% 100%)', 'color(--helmlab 1.1436 1 1)'),
        ('color(--helmlab -100% -100% -100%)', 'color(--helmlab -1.1436 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('helmlab'), Color(color2))


class TestHelmlabSerialize(util.ColorAssertsPyTest):
    """Test Helmlab serialization."""

    COLORS = [
        # Test color
        ('color(--helmlab 0.1 0.75 -0.1 / 0.5)', {}, 'color(--helmlab 0.1 0.75 -0.1 / 0.5)'),
        # Test alpha
        ('color(--helmlab 0.1 0.75 -0.1)', {'alpha': True}, 'color(--helmlab 0.1 0.75 -0.1 / 1)'),
        ('color(--helmlab 0.1 0.75 -0.1 / 0.5)', {'alpha': False}, 'color(--helmlab 0.1 0.75 -0.1)'),
        # Test None
        ('color(--helmlab none 0.75 -0.1)', {}, 'color(--helmlab 0 0.75 -0.1)'),
        ('color(--helmlab none 0.75 -0.1)', {'none': True}, 'color(--helmlab none 0.75 -0.1)'),
        # Test Fit (not bound)
        ('color(--helmlab 1.2 0.75 -0.1)', {}, 'color(--helmlab 1.2 0.75 -0.1)'),
        ('color(--helmlab 1.2 0.75 -0.1)', {'fit': False}, 'color(--helmlab 1.2 0.75 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHelmlabPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Helmlab."""

    def test_l(self):
        """Test `l`."""

        c = Color('color(--helmlab -0.02 0.7 0.04)')
        self.assertEqual(c['l'], -0.02)
        c['l'] = 0.1
        self.assertEqual(c['l'], 0.1)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--helmlab -0.02 0.7 0.04)')
        self.assertEqual(c['a'], 0.7)
        c['a'] = 0.2
        self.assertEqual(c['a'], 0.2)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--helmlab -0.02 0.7 0.04)')
        self.assertEqual(c['b'], 0.04)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--helmlab -0.02 0.7 0.04)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)

    def test_labish_names(self):
        """Test `labish_names`."""

        c = Color('color(--helmlab -0.02 0.7 0.03 / 1)')
        self.assertEqual(c._space.names(), ('l', 'a', 'b'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('helmlab', [0.3, 0, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmlab', [0.3, 0.0000001, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmlab', [NaN, 0.0000001, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmlab', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('helmlab', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('helmlab', [0, 0.1, -0.2]).is_achromatic(), False)
        self.assertEqual(Color('helmlab', [NaN, 0, -0.1]).is_achromatic(), False)
        self.assertEqual(Color('helmlab', [0.3, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmlab', [NaN, NaN, 0]).is_achromatic(), True)
