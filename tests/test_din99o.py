"""Test DIN99o library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestDIN99o(util.ColorAssertsPyTest):
    """Test DIN99o."""

    COLORS = [
        ('red', 'color(--din99o 57.289 39.498 30.518)'),
        ('orange', 'color(--din99o 77.855 16.444 40.318)'),
        ('yellow', 'color(--din99o 97.552 -8.046 44.345)'),
        ('green', 'color(--din99o 50.336 -30.169 25.591)'),
        ('blue', 'color(--din99o 36.03 31.935 -40.383)'),
        ('indigo', 'color(--din99o 23.324 29.57 -27.086)'),
        ('violet', 'color(--din99o 73.015 34.267 -18.421)'),
        ('white', 'color(--din99o 100 0 0)'),
        ('gray', 'color(--din99o 57.63 0 0)'),
        ('black', 'color(--din99o 0 0 0)'),
        # Test color
        ('color(--din99o 50 10 -10)', 'color(--din99o 50 10 -10)'),
        ('color(--din99o 50 10 -10 / 0.5)', 'color(--din99o 50 10 -10 / 0.5)'),
        ('color(--din99o 50% 50% -50% / 50%)', 'color(--din99o 50 27.5 -27.5 / 0.5)'),
        ('color(--din99o none none none / none)', 'color(--din99o none none none / none)'),
        # Test percent ranges
        ('color(--din99o 0% 0% 0%)', 'color(--din99o 0 0 0)'),
        ('color(--din99o 100% 100% 100%)', 'color(--din99o 100 55 55)'),
        ('color(--din99o -100% -100% -100%)', 'color(--din99o -100 -55 -55)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('din99o'), Color(color2))


class TestDIN99oSerialize(util.ColorAssertsPyTest):
    """Test DIN99o serialization."""

    COLORS = [
        # Test color
        ('color(--din99o 75 10 -10 / 0.5)', {}, 'color(--din99o 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--din99o 75 10 -10)', {'alpha': True}, 'color(--din99o 75 10 -10 / 1)'),
        ('color(--din99o 75 10 -10 / 0.5)', {'alpha': False}, 'color(--din99o 75 10 -10)'),
        # Test None
        ('color(--din99o none 10 -10)', {}, 'color(--din99o 0 10 -10)'),
        ('color(--din99o none 10 -10)', {'none': True}, 'color(--din99o none 10 -10)'),
        # Test Fit (not bound)
        ('color(--din99o 120 10 -10)', {}, 'color(--din99o 120 10 -10)'),
        ('color(--din99o 120 10 -10)', {'fit': False}, 'color(--din99o 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestDIN99oProperties(util.ColorAsserts, unittest.TestCase):
    """Test DIN99o."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--din99o 90% 50 -20 / 1)')
        self.assertEqual(c['lightness'], 90)
        c['lightness'] = 80
        self.assertEqual(c['lightness'], 80)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--din99o 90% 50 -20 / 1)')
        self.assertEqual(c['a'], 50)
        c['a'] = 40
        self.assertEqual(c['a'], 40)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--din99o 90% 50 -20 / 1)')
        self.assertEqual(c['b'], -20)
        c['b'] = -10
        self.assertEqual(c['b'], -10)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--din99o 90% 50 -20 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
