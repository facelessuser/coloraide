"""Test CAM16 UCS."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest
from collections import namedtuple

CAM16Coords = namedtuple("CAM16Coords", "J C h s Q M H")


class TestCAM16CAM16UCS(util.ColorAssertsPyTest):
    """Test CAM16 UCS."""

    COLORS = [
        ('red', 'color(--cam16-ucs 59.178 40.82 21.153)'),
        ('orange', 'color(--cam16-ucs 78.364 9.6945 28.629)'),
        ('yellow', 'color(--cam16-ucs 96.802 -12.779 33.037)'),
        ('green', 'color(--cam16-ucs 46.661 -26.746 20.671)'),
        ('blue', 'color(--cam16-ucs 36.252 8.5723 -37.87)'),
        ('indigo', 'color(--cam16-ucs 24.524 19.714 -22.758)'),
        ('violet', 'color(--cam16-ucs 74.738 27.949 -15.247)'),
        ('white', 'color(--cam16-ucs 100 -1.8983 -1.0754)'),
        ('gray', 'color(--cam16-ucs 56.23 -1.2555 -0.71134)'),
        ('black', 'color(--cam16-ucs 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam16-ucs'), Color(color2))


class TestCAM16UCSPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM16 UCS."""

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam16-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['j'], 0.51332)
        c['j'] = 0.2
        self.assertEqual(c['j'], 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--cam16-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['a'], 0.92781)
        c['a'] = 0.1
        self.assertEqual(c['a'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--cam16-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['b'], 1.076)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam16-ucs 0.51332 0.92781 1.076)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
