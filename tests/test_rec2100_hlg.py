"""Test Rec. 2100 HLG."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestRec2100HLG(util.ColorAssertsPyTest):
    """Test Rec. 2100 HLG."""

    COLORS = [
        ('red', 'color(--rec2100-hlg 0.65587 0.23436 0.11415)'),
        ('orange', 'color(--rec2100-hlg 0.69294 0.56608 0.19838)'),
        ('yellow', 'color(--rec2100-hlg 0.74128 0.74775 0.28808)'),
        ('green', 'color(--rec2100-hlg 0.2377 0.39721 0.12289)'),
        ('blue', 'color(--rec2100-hlg 0.18555 0.09504 0.72822)'),
        ('indigo', 'color(--rec2100-hlg 0.20682 0.07669 0.39979)'),
        ('violet', 'color(--rec2100-hlg 0.66226 0.46674 0.70549)'),
        ('white', 'color(--rec2100-hlg 0.75 0.75 0.75)'),
        ('gray', 'color(--rec2100-hlg 0.41423 0.41423 0.41423)'),
        ('black', 'color(--rec2100-hlg 0 0 0)'),
        # Test CSS color
        ('color(--rec2100-hlg 0 0.50196 0)', 'color(--rec2100-hlg 0 0.50196 0)'),
        ('color(--rec2100-hlg 0 0.50196 0 / 0.5)', 'color(--rec2100-hlg 0 0.50196 0 / 0.5)'),
        ('color(--rec2100-hlg 50% 50% 50% / 50%)', 'color(--rec2100-hlg 0.5 0.5 0.5 / 0.5)'),
        ('color(--rec2100-hlg none none none / none)', 'color(--rec2100-hlg none none none / none)'),
        # Test range
        ('color(--rec2100-hlg 0% 0% 0%)', 'color(--rec2100-hlg 0 0 0)'),
        ('color(--rec2100-hlg 100% 100% 100%)', 'color(--rec2100-hlg 1 1 1)'),
        ('color(--rec2100-hlg -100% -100% -100%)', 'color(--rec2100-hlg -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('rec2100-hlg'), Color(color2))


class TestRec2100HLGSerialize(util.ColorAssertsPyTest):
    """Test Rec. 2100 HLG serialization."""

    COLORS = [
        # Test color
        ('color(--rec2100-hlg 0 0.3 0.75 / 0.5)', {}, 'color(--rec2100-hlg 0 0.3 0.75 / 0.5)'),
        # Test alpha
        ('color(--rec2100-hlg 0 0.3 0.75)', {'alpha': True}, 'color(--rec2100-hlg 0 0.3 0.75 / 1)'),
        ('color(--rec2100-hlg 0 0.3 0.75 / 0.5)', {'alpha': False}, 'color(--rec2100-hlg 0 0.3 0.75)'),
        # Test None
        ('color(--rec2100-hlg none 0.3 0.75)', {}, 'color(--rec2100-hlg 0 0.3 0.75)'),
        ('color(--rec2100-hlg none 0.3 0.75)', {'none': True}, 'color(--rec2100-hlg none 0.3 0.75)'),
        # Test Fit
        ('color(--rec2100-hlg 1.2 0.2 0)', {}, 'color(--rec2100-hlg 1 0.94167 0.8953)'),
        ('color(--rec2100-hlg 1.2 0.2 0)', {'fit': False}, 'color(--rec2100-hlg 1.2 0.2 0)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class Testrec2100HLGPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Rec. 2100 HLG properties."""

    def test_r(self):
        """Test `r`."""

        c = Color('color(--rec2100-hlg 0.1 0.2 0.3)')
        self.assertEqual(c['r'], 0.1)
        c['r'] = 0.2
        self.assertEqual(c['r'], 0.2)

    def test_g(self):
        """Test `g`."""

        c = Color('color(--rec2100-hlg 0.1 0.2 0.3)')
        self.assertEqual(c['g'], 0.2)
        c['g'] = 0.1
        self.assertEqual(c['g'], 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--rec2100-hlg 0.1 0.2 0.3)')
        self.assertEqual(c['b'], 0.3)
        c['b'] = 0.1
        self.assertEqual(c['b'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--rec2100-hlg 0.1 0.2 0.3)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
