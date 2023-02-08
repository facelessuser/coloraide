"""Test Hunter Lab."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestHunterLab(util.ColorAssertsPyTest):
    """Test Hunter Lab."""

    COLORS = [
        ('red', 'color(--hunter-lab 46.113 82.672 28.408)'),
        ('orange', 'color(--hunter-lab 69.407 23.266 40.946)'),
        ('yellow', 'color(--hunter-lab 96.323 -21.054 55.869)'),
        ('green', 'color(--hunter-lab 39.291 -32.086 22.368)'),
        ('blue', 'color(--hunter-lab 26.869 75.478 -200.29)'),
        ('indigo', 'color(--hunter-lab 17.629 40.896 -62.916)'),
        ('violet', 'color(--hunter-lab 63.496 58.109 -40.51)'),
        ('white', 'color(--hunter-lab 100 0 0)'),
        ('gray', 'color(--hunter-lab 46.461 0 0)'),
        ('black', 'color(--hunter-lab 0 0 0)'),
        # Test color
        ('color(--hunter-lab 50 10 -10)', 'color(--hunter-lab 50 10 -10)'),
        ('color(--hunter-lab 50 10 -10 / 0.5)', 'color(--hunter-lab 50 10 -10 / 0.5)'),
        ('color(--hunter-lab 50% 50% -50% / 50%)', 'color(--hunter-lab 50 105 -105 / 0.5)'),
        ('color(--hunter-lab none none none / none)', 'color(--hunter-lab none none none / none)'),
        # Test percent ranges
        ('color(--hunter-lab 0% 0% 0%)', 'color(--hunter-lab 0 0 0)'),
        ('color(--hunter-lab 100% 100% 100%)', 'color(--hunter-lab 100 210 210)'),
        ('color(--hunter-lab -100% -100% -100%)', 'color(--hunter-lab -100 -210 -210)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hunter-lab'), Color(color2))


class TestHunterLabSerialize(util.ColorAssertsPyTest):
    """Test Hunter Lab serialization."""

    COLORS = [
        # Test color
        ('color(--hunter-lab 75 10 -10 / 0.5)', {}, 'color(--hunter-lab 75 10 -10 / 0.5)'),
        # Test alpha
        ('color(--hunter-lab 75 10 -10)', {'alpha': True}, 'color(--hunter-lab 75 10 -10 / 1)'),
        ('color(--hunter-lab 75 10 -10 / 0.5)', {'alpha': False}, 'color(--hunter-lab 75 10 -10)'),
        # Test None
        ('color(--hunter-lab none 10 -10)', {}, 'color(--hunter-lab 0 10 -10)'),
        ('color(--hunter-lab none 10 -10)', {'none': True}, 'color(--hunter-lab none 10 -10)'),
        # Test Fit (not bound)
        ('color(--hunter-lab 120 10 -10)', {}, 'color(--hunter-lab 120 10 -10)'),
        ('color(--hunter-lab 120 10 -10)', {'fit': False}, 'color(--hunter-lab 120 10 -10)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHunterLabPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Hunter Lab."""

    def test_l(self):
        """Test `l`."""

        c = Color('color(--hunter-lab 96.323 -21.06 55.728)')
        self.assertEqual(c['l'], 96.323)
        c['l'] = 0.2
        self.assertEqual(c['l'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--hunter-lab 96.323 -21.06 55.728)')
        self.assertEqual(c['a'], -21.06)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--hunter-lab 96.323 -21.06 55.728)')
        self.assertEqual(c['b'], 55.728)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hunter-lab 96.323 -21.06 55.728)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
