"""Test DIN99o LCh library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
from coloraide import NaN
import pytest


class TestLCh99o(util.ColorAssertsPyTest):
    """Test LCh99o."""

    COLORS = [
        ('red', 'color(--lch99o 57.289 49.915 37.692)'),
        ('orange', 'color(--lch99o 77.855 43.543 67.811)'),
        ('yellow', 'color(--lch99o 97.552 45.069 100.28)'),
        ('green', 'color(--lch99o 50.336 39.561 139.69)'),
        ('blue', 'color(--lch99o 36.03 51.485 308.34)'),
        ('indigo', 'color(--lch99o 23.324 40.1 317.51)'),
        ('violet', 'color(--lch99o 73.015 38.904 331.74)'),
        ('white', 'color(--lch99o 100 0 none)'),
        ('gray', 'color(--lch99o 57.63 0 none)'),
        ('black', 'color(--lch99o 0 0 none)'),
        # Test color
        ('color(--lch99o 100 30 270)', 'color(--lch99o 100 30 270)'),
        ('color(--lch99o 100 30 270 / 0.5)', 'color(--lch99o 100 30 270 / 0.5)'),
        ('color(--lch99o 50% 50% 50% / 50%)', 'color(--lch99o 50 30 180 / 0.5)'),
        ('color(--lch99o none none none / none)', 'color(--lch99o none none none / none)'),
        # Test percent ranges
        ('color(--lch99o 0% 0% 0%)', 'color(--lch99o 0 0 none)'),
        ('color(--lch99o 100% 100% 100%)', 'color(--lch99o 100 60 360 / 1)'),
        ('color(--lch99o -100% -100% -100%)', 'color(--lch99o -100 0 -360 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('lch99o'), Color(color2))


class TestLCh99oSerialize(util.ColorAssertsPyTest):
    """Test LCh99o serialization."""

    COLORS = [
        # Test color
        ('color(--lch99o 75 30 50 / 0.5)', {}, 'color(--lch99o 75 30 50 / 0.5)'),
        # Test alpha
        ('color(--lch99o 75 30 50)', {'alpha': True}, 'color(--lch99o 75 30 50 / 1)'),
        ('color(--lch99o 75 30 50 / 0.5)', {'alpha': False}, 'color(--lch99o 75 30 50)'),
        # Test None
        ('color(--lch99o none 30 50)', {}, 'color(--lch99o 0 30 50)'),
        ('color(--lch99o none 30 50)', {'none': True}, 'color(--lch99o none 30 50)'),
        # Test Fit (not bound)
        ('color(--lch99o 75 60 50)', {}, 'color(--lch99o 75 60 50)'),
        ('color(--lch99o 75 60 50)', {'fit': False}, 'color(--lch99o 75 60 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestLCh99oProperties(util.ColorAsserts, unittest.TestCase):
    """Test LCh99o."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--lch99o 90% 50 120 / 1)')
        self.assertEqual(c['lightness'], 90)
        c['lightness'] = 80
        self.assertEqual(c['lightness'], 80)

    def test_chroma(self):
        """Test `chroma`."""

        c = Color('color(--lch99o 90% 50 120 / 1)')
        self.assertEqual(c['chroma'], 50)
        c['chroma'] = 40
        self.assertEqual(c['chroma'], 40)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--lch99o 90% 50 120 / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--lch99o 90% 50 120 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('lch99o', [90, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--lch99o 90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('color(--lch99o 90% 0.000000000009 120 / 1)').convert('din99o').convert('lch99o')
        self.assertTrue(c.is_nan('hue'))

    def test_from_din99o(self):
        """Test null from DIN99o conversion."""

        c1 = Color('color(--din99o 90% 0 0)')
        c2 = c1.convert('lch99o')
        self.assertColorEqual(c2, Color('color(--lch99o 90% 0 0)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to DIN99o LCh with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('lch99o')
                self.assertTrue(color2.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chorma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to lab."""

        self.assertColorEqual(
            Color('color(--lch99o 90% -10 120 / 1)').convert('din99o'),
            Color('color(--din99o 90% 0 0)')
        )
