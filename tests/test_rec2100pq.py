"""Test Rec. 2100 PQ."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestRec2100PQ(util.ColorAssertsPyTest):
    """Test Rec. 2100 PQ."""

    COLORS = [
        ('red', 'color(--rec2100pq 0.53255 0.32702 0.22007)'),
        ('orange', 'color(--rec2100pq 0.55101 0.49099 0.30009)'),
        ('yellow', 'color(--rec2100pq 0.57607 0.57949 0.36204)'),
        ('green', 'color(--rec2100pq 0.32936 0.41997 0.2299)'),
        ('blue', 'color(--rec2100pq 0.28965 0.19681 0.56919)'),
        ('indigo', 'color(--rec2100pq 0.30671 0.17168 0.42117)'),
        ('violet', 'color(--rec2100pq 0.53568 0.45048 0.55741)'),
        ('white', 'color(--rec2100pq 0.58069 0.58069 0.58069)'),
        ('gray', 'color(--rec2100pq 0.42781 0.42781 0.42781)'),
        ('black', 'color(--rec2100pq 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('rec2100pq'), Color(color2))


class TestRec2100PQPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Rec. 2100 PQ properties."""

    def test_r(self):
        """Test `r`."""

        c = Color('color(--rec2100pq 0.1 0.2 0.3)')
        self.assertEqual(c['r'], 0.1)
        c['r'] = 0.2
        self.assertEqual(c['r'], 0.2)

    def test_g(self):
        """Test `g`."""

        c = Color('color(--rec2100pq 0.1 0.2 0.3)')
        self.assertEqual(c['g'], 0.2)
        c['g'] = 0.1
        self.assertEqual(c['g'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--rec2100pq 0.1 0.2 0.3)')
        self.assertEqual(c['b'], 0.3)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--rec2100pq 0.1 0.2 0.3)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
