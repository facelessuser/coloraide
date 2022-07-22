"""Test oRGB."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestoRGB(util.ColorAssertsPyTest):
    """Test oRGB."""

    COLORS = [
        ('red', 'color(--orgb 0.299 0.00002 0.99998)'),
        ('orange', 'color(--orgb 0.67882 0.75654 0.4464)'),
        ('yellow', 'color(--orgb 0.886 1 0)'),
        ('green', 'color(--orgb 0.29465 0.00001 -0.50195)'),
        ('blue', 'color(--orgb 0.114 -1 0)'),
        ('indigo', 'color(--orgb 0.14606 -0.39733 0.19643)'),
        ('violet', 'color(--orgb 0.68472 -0.29948 0.29947)'),
        ('white', 'color(--orgb 1 0 0)'),
        ('gray', 'color(--orgb 0.50196 0 0)'),
        ('black', 'color(--orgb 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_orgb_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('orgb'), Color(color2))


class TestoRGBPoperties(util.ColorAsserts, unittest.TestCase):
    """Test oRGB."""

    def test_l(self):
        """Test `l`."""

        c = Color('color(--orgb 1 0.5 0.5)')
        self.assertEqual(c['l'], 1)
        c['l'] = 0.2
        self.assertEqual(c['l'], 0.2)

    def test_cyb(self):
        """Test `cyb`."""

        c = Color('color(--orgb 1 0.5 0.5)')
        self.assertEqual(c['cyb'], 0.5)
        c['cyb'] = 0.1
        self.assertEqual(c['cyb'], 0.1)

    def test_crg(self):
        """Test `crg`."""

        c = Color('color(--orgb 1 0.5 0.5)')
        self.assertEqual(c['crg'], 0.5)
        c['crg'] = 0.1
        self.assertEqual(c['crg'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--orgb 1 0.5 0.5)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
