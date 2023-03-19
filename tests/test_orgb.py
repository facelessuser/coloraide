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
        ('black', 'color(--orgb 0 0 0)'),
        # Test color
        ('color(--orgb 0.5 0.1 -0.1)', 'color(--orgb 0.5 0.1 -0.1)'),
        ('color(--orgb 0.5 0.1 -0.1 / 0.5)', 'color(--orgb 0.5 0.1 -0.1 / 0.5)'),
        ('color(--orgb 50% 50% -50% / 50%)', 'color(--orgb 0.5 0.5 -0.5 / 0.5)'),
        ('color(--orgb none none none / none)', 'color(--orgb none none none / none)'),
        # Test percent ranges
        ('color(--orgb 0% 0% 0%)', 'color(--orgb 0 0 0)'),
        ('color(--orgb 100% 100% 100%)', 'color(--orgb 1 1 1)'),
        ('color(--orgb -100% -100% -100%)', 'color(--orgb -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_orgb_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('orgb'), Color(color2))


class TestoRGBSerialize(util.ColorAssertsPyTest):
    """Test oRGB serialization."""

    COLORS = [
        # Test color
        ('color(--orgb 0.75 0.1 -0.1 / 0.5)', {}, 'color(--orgb 0.75 0.1 -0.1 / 0.5)'),
        # Test alpha
        ('color(--orgb 0.75 0.1 -0.1)', {'alpha': True}, 'color(--orgb 0.75 0.1 -0.1 / 1)'),
        ('color(--orgb 0.75 0.1 -0.1 / 0.5)', {'alpha': False}, 'color(--orgb 0.75 0.1 -0.1)'),
        # Test None
        ('color(--orgb none 0.1 -0.1)', {}, 'color(--orgb 0 0.1 -0.1)'),
        ('color(--orgb none 0.1 -0.1)', {'none': True}, 'color(--orgb none 0.1 -0.1)'),
        # Test Fit
        ('color(--orgb 0.75 1.2 -0.1)', {}, 'color(--orgb 0.76398 1 -0.05221)'),
        ('color(--orgb 0.75 1.2 -0.1)', {'fit': False}, 'color(--orgb 0.75 1.2 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


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

    def test_labish_names(self):
        """Test `labish_names`."""

        c = Color('color(--orgb 1 0.5 0.5)')
        self.assertEqual(c._space.names(), ('l', 'crg', 'cyb'))
