"""Test Helmgen."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestHelmgen(util.ColorAssertsPyTest):
    """Test Helmgen."""

    COLORS = [
        ('red', 'color(--helmgen 0.56358 0.28763 0.18093)'),
        ('orange', 'color(--helmgen 0.75771 0.07633 0.24769)'),
        ('yellow', 'color(--helmgen 0.96486 -0.0828 0.31422)'),
        ('green', 'color(--helmgen 0.44109 -0.17567 0.18227)'),
        ('blue', 'color(--helmgen 0.36553 -0.04097 -0.4854)'),
        ('indigo', 'color(--helmgen 0.23764 0.11887 -0.2513)'),
        ('violet', 'color(--helmgen 0.72132 0.19702 -0.16488)'),
        ('white', 'color(--helmgen 1 0 0)'),
        ('gray', 'color(--helmgen 0.53175 0 0)'),
        ('black', 'color(--helmgen 0 0 0)'),
        ('color(srgb 1.01 1.01 1.01)', 'color(--helmgen 1.0077 0 0)'),
        ('color(srgb 1e-3 1e-3 1e-3)', 'color(--helmgen 0.00074 0 0)'),
        # Test color
        ('color(--helmgen 0.5 0.1 -0.1)', 'color(--helmgen 0.5 0.1 -0.1)'),
        ('color(--helmgen 0.5 0.1 -0.1 / 0.5)', 'color(--helmgen 0.5 0.1 -0.1 / 0.5)'),
        ('color(--helmgen 50% 50% -50% / 50%)', 'color(--helmgen 0.5 0.2 -0.2 / 0.5)'),
        ('color(--helmgen none none none / none)', 'color(--helmgen none none none / none)'),
        # Test percent ranges
        ('color(--helmgen 0% 0% 0%)', 'color(--helmgen 0 0 0)'),
        ('color(--helmgen 100% 100% 100%)', 'color(--helmgen 1 0.4 0.4)'),
        ('color(--helmgen -100% -100% -100%)', 'color(--helmgen -1 -0.4 -0.4)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('helmgen'), Color(color2))


class TestHelmgenSerialize(util.ColorAssertsPyTest):
    """Test Helmgen serialization."""

    COLORS = [
        # Test color
        ('color(--helmgen 0.1 0.75 -0.1 / 0.5)', {}, 'color(--helmgen 0.1 0.75 -0.1 / 0.5)'),
        # Test alpha
        ('color(--helmgen 0.1 0.75 -0.1)', {'alpha': True}, 'color(--helmgen 0.1 0.75 -0.1 / 1)'),
        ('color(--helmgen 0.1 0.75 -0.1 / 0.5)', {'alpha': False}, 'color(--helmgen 0.1 0.75 -0.1)'),
        # Test None
        ('color(--helmgen none 0.75 -0.1)', {}, 'color(--helmgen 0 0.75 -0.1)'),
        ('color(--helmgen none 0.75 -0.1)', {'none': True}, 'color(--helmgen none 0.75 -0.1)'),
        # Test Fit (not bound)
        ('color(--helmgen 1.2 0.75 -0.1)', {}, 'color(--helmgen 1.2 0.75 -0.1)'),
        ('color(--helmgen 1.2 0.75 -0.1)', {'fit': False}, 'color(--helmgen 1.2 0.75 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHelmgenPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Helmgen."""

    def test_l(self):
        """Test `l`."""

        c = Color('color(--helmgen -0.02 0.7 0.04)')
        self.assertEqual(c['l'], -0.02)
        c['l'] = 0.1
        self.assertEqual(c['l'], 0.1)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--helmgen -0.02 0.7 0.04)')
        self.assertEqual(c['a'], 0.7)
        c['a'] = 0.2
        self.assertEqual(c['a'], 0.2)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--helmgen -0.02 0.7 0.04)')
        self.assertEqual(c['b'], 0.04)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--helmgen -0.02 0.7 0.04)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)

    def test_labish_names(self):
        """Test `labish_names`."""

        c = Color('color(--helmgen -0.02 0.7 0.03 / 1)')
        self.assertEqual(c._space.names(), ('l', 'a', 'b'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('helmgen', [0.3, 0, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmgen', [0.3, 0.0000001, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmgen', [NaN, 0.0000001, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmgen', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('helmgen', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('helmgen', [0, 0.1, -0.2]).is_achromatic(), False)
        self.assertEqual(Color('helmgen', [NaN, 0, -0.1]).is_achromatic(), False)
        self.assertEqual(Color('helmgen', [0.3, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('helmgen', [NaN, NaN, 0]).is_achromatic(), True)
