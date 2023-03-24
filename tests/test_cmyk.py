"""Test CMYK."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestCMYK(util.ColorAssertsPyTest):
    """Test CMYK."""

    COLORS = [
        ('red', 'color(--cmyk 0 1 1 0)'),
        ('orange', 'color(--cmyk 0 0.35294 1 0)'),
        ('yellow', 'color(--cmyk 0 0 1 0)'),
        ('green', 'color(--cmyk 1 0 1 0.49804)'),
        ('blue', 'color(--cmyk 1 1 0 0)'),
        ('indigo', 'color(--cmyk 0.42308 1 0 0.4902)'),
        ('violet', 'color(--cmyk 0 0.45378 0 0.06667)'),
        ('white', 'color(--cmyk 0 0 0 0)'),
        ('gray', 'color(--cmyk 0 0 0 0.49804)'),
        ('black', 'color(--cmyk 0 0 0 1)'),
        # Test CSS color
        ('color(--cmyk 0 0.50196 0 0)', 'color(--cmyk 0 0.50196 0 0)'),
        ('color(--cmyk 0 0.50196 0 0 / 0.5)', 'color(--cmyk 0 0.50196 0 0 / 0.5)'),
        ('color(--cmyk 50% 50% 50% 50%/ 50%)', 'color(--cmyk 0.5 0.5 0.5 0.5 / 0.5)'),
        ('color(--cmyk none none none none / none)', 'color(--cmyk none none none none / none)'),
        # Test range
        ('color(--cmyk 0% 0% 0% 0%)', 'color(--cmyk 0 0 0 0)'),
        ('color(--cmyk 100% 100% 100% 100%)', 'color(--cmyk 1 1 1 1)'),
        ('color(--cmyk -100% -100% -100% -100%)', 'color(--cmyk -1 -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_cmyk_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cmyk'), Color(color2))


class TestCMYKSerialize(util.ColorAssertsPyTest):
    """Test CMYK serialization."""

    COLORS = [
        # Test color
        ('color(--cmyk 0 0.3 0.75 0.5 / 0.5)', {}, 'color(--cmyk 0 0.3 0.75 0.5 / 0.5)'),
        # Test alpha
        ('color(--cmyk 0 0.3 0.75 0.5)', {'alpha': True}, 'color(--cmyk 0 0.3 0.75 0.5 / 1)'),
        ('color(--cmyk 0 0.3 0.75 0.5 / 0.5)', {'alpha': False}, 'color(--cmyk 0 0.3 0.75 0.5)'),
        # Test None
        ('color(--cmyk none 0.3 0.75 0.5)', {}, 'color(--cmyk 0 0.3 0.75 0.5)'),
        ('color(--cmyk none 0.3 0.75 0.5)', {'none': True}, 'color(--cmyk none 0.3 0.75 0.5)'),
        # Test Fit
        ('color(--cmyk 1.2 0.2 0 0.5)', {}, 'color(--cmyk 1 0.2 0 0.5)'),
        ('color(--cmyk 1.2 0.2 0 0.5)', {'fit': False}, 'color(--cmyk 1.2 0.2 0 0.5)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestCMYKPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CMYK."""

    def test_c(self):
        """Test `c`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['c'], 0)
        c['c'] = 0.2
        self.assertEqual(c['c'], 0.2)

    def test_m(self):
        """Test `m`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['m'], 0)
        c['m'] = 0.1
        self.assertEqual(c['m'], 0.1)

    def test_y(self):
        """Test `y`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['y'], 1)
        c['y'] = 0.1
        self.assertEqual(c['y'], 0.1)

    def test_k(self):
        """Test `k`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['k'], 0)
        c['k'] = 0.1
        self.assertEqual(c['k'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cmyk 0 0 1 0)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('cmyk', [0.3, 0.3, 0.3, 0.3]).is_achromatic(), True)
        self.assertEqual(Color('cmyk', [0.3000001, 0.3, 0.3, 0.3]).is_achromatic(), True)
        self.assertEqual(Color('cmyk', [0.3, 0.3, 0.3, NaN]).is_achromatic(), True)
        self.assertEqual(Color('cmyk', [0.4, 0.3, 0.3, 1.0]).is_achromatic(), True)
        self.assertEqual(Color('cmyk', [NaN, 0.3, 0.0, 1.0]).is_achromatic(), True)
        self.assertEqual(Color('cmyk', [0.4, 0.3, 0.3, 0.3]).is_achromatic(), False)
        self.assertEqual(Color('cmyk', [NaN, 0.3, 0.3, 0.3]).is_achromatic(), False)
