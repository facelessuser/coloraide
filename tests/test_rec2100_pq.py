"""Test Rec. 2100 PQ."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestRec2100PQ(util.ColorAssertsPyTest):
    """Test Rec. 2100 PQ."""

    COLORS = [
        ('red', 'color(--rec2100-pq 0.53255 0.32702 0.22007)'),
        ('orange', 'color(--rec2100-pq 0.55101 0.49099 0.30009)'),
        ('yellow', 'color(--rec2100-pq 0.57607 0.57949 0.36204)'),
        ('green', 'color(--rec2100-pq 0.32936 0.41997 0.2299)'),
        ('blue', 'color(--rec2100-pq 0.28965 0.19681 0.56919)'),
        ('indigo', 'color(--rec2100-pq 0.30671 0.17168 0.42117)'),
        ('violet', 'color(--rec2100-pq 0.53568 0.45048 0.55741)'),
        ('white', 'color(--rec2100-pq 0.58069 0.58069 0.58069)'),
        ('gray', 'color(--rec2100-pq 0.42781 0.42781 0.42781)'),
        ('black', 'color(--rec2100-pq 0 0 0)'),
        # Test CSS color
        ('color(--rec2100-pq 0 0.50196 0)', 'color(--rec2100-pq 0 0.50196 0)'),
        ('color(--rec2100-pq 0 0.50196 0 / 0.5)', 'color(--rec2100-pq 0 0.50196 0 / 0.5)'),
        ('color(--rec2100-pq 50% 50% 50% / 50%)', 'color(--rec2100-pq 0.5 0.5 0.5 / 0.5)'),
        ('color(--rec2100-pq none none none / none)', 'color(--rec2100-pq none none none / none)'),
        # Test range
        ('color(--rec2100-pq 0% 0% 0%)', 'color(--rec2100-pq 0 0 0)'),
        ('color(--rec2100-pq 100% 100% 100%)', 'color(--rec2100-pq 1 1 1)'),
        ('color(--rec2100-pq -100% -100% -100%)', 'color(--rec2100-pq -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('rec2100-pq'), Color(color2))


class TestRec2100PQSerialize(util.ColorAssertsPyTest):
    """Test Rec. 2100 PQ serialization."""

    COLORS = [
        # Test color
        ('color(--rec2100-pq 0 0.3 0.75 / 0.5)', {}, 'color(--rec2100-pq 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--rec2100-pq 0 0.3 0.75)', {'alpha': True}, 'color(--rec2100-pq 0 0.3 0.75 / 1)'),
        ('color(--rec2100-pq 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--rec2100-pq 0 0.3 0.75)'),
        # Test None
        ('color(--rec2100-pq none 0.3 0.75)', {}, 'color(--rec2100-pq 0 0.3 0.75)'),
        ('color(--rec2100-pq none 0.3 0.75)', {'none': True}, 'color(--rec2100-pq none 0.3 0.75)'),
        # Test Fit
        ('color(--rec2100-pq 1.2 0.2 0)', {}, 'color(--rec2100-pq 1 1 1)'),
        ('color(--rec2100-pq 1.2 0.2 0)', {'fit': False}, 'color(--rec2100-pq 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class Testrec2100PQPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Rec. 2100 PQ properties."""

    def test_r(self):
        """Test `r`."""

        c = Color('color(--rec2100-pq 0.1 0.2 0.3)')
        self.assertEqual(c['r'], 0.1)
        c['r'] = 0.2
        self.assertEqual(c['r'], 0.2)

    def test_g(self):
        """Test `g`."""

        c = Color('color(--rec2100-pq 0.1 0.2 0.3)')
        self.assertEqual(c['g'], 0.2)
        c['g'] = 0.1
        self.assertEqual(c['g'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--rec2100-pq 0.1 0.2 0.3)')
        self.assertEqual(c['b'], 0.3)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--rec2100-pq 0.1 0.2 0.3)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
