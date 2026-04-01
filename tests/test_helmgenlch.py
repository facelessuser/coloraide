"""Test Helmgenlch library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
from coloraide import NaN
import pytest


class TestHelmgenlch(util.ColorAssertsPyTest):
    """Test Helmgenlch."""

    COLORS = [
        ('red', 'color(--helmgenlch 0.56358 0.3398 32.171)'),
        ('orange', 'color(--helmgenlch 0.75771 0.25919 72.872)'),
        ('yellow', 'color(--helmgenlch 0.96486 0.32495 104.76)'),
        ('green', 'color(--helmgenlch 0.44109 0.25314 133.94)'),
        ('blue', 'color(--helmgenlch 0.36553 0.48713 265.18)'),
        ('indigo', 'color(--helmgenlch 0.23764 0.278 295.32)'),
        ('violet', 'color(--helmgenlch 0.72132 0.2569 320.07)'),
        ('white', 'color(--helmgenlch 1 0 0)'),
        ('gray', 'color(--helmgenlch 0.53175 0 0)'),
        ('black', 'color(--helmgenlch 0 0 none)'),
        # Test color
        ('color(--helmgenlch 1.0 0.5 270)', 'color(--helmgenlch 1 0.5 270)'),
        ('color(--helmgenlch 1.0 0.5 270 / 0.5)', 'color(--helmgenlch 1 0.5 270 / 0.5)'),
        ('color(--helmgenlch 50% 50% 180 / 50%)', 'color(--helmgenlch 0.5 0.2 180 / 0.5)'),
        ('color(--helmgenlch none none none / none)', 'color(--helmgenlch none none none / none)'),
        # Test percent ranges
        ('color(--helmgenlch 0% 0% 0)', 'color(--helmgenlch 0 0 none)'),
        ('color(--helmgenlch 100% 100% 360)', 'color(--helmgenlch 1 0.4 360)'),
        ('color(--helmgenlch -100% -100% -360)', 'color(--helmgenlch -1 -0.4 -360)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('helmgenlch'), Color(color2))


class TestHelmgenlchSerialize(util.ColorAssertsPyTest):
    """Test Helmgenlch serialization."""

    COLORS = [
        # Test color
        ('color(--helmgenlch 0.75 0.5 50 / 0.5)', {}, 'color(--helmgenlch 0.75 0.5 50 / 0.5)'),
        # Test alpha
        ('color(--helmgenlch 0.75 0.5 50)', {'alpha': True}, 'color(--helmgenlch 0.75 0.5 50 / 1)'),
        ('color(--helmgenlch 0.75 0.5 50 / 0.5)', {'alpha': False}, 'color(--helmgenlch 0.75 0.5 50)'),
        # Test None
        ('color(--helmgenlch none 0.5 50)', {}, 'color(--helmgenlch 0 0.5 50)'),
        ('color(--helmgenlch none 0.5 50)', {'none': True}, 'color(--helmgenlch none 0.5 50)'),
        # Test Fit (not bound)
        ('color(--helmgenlch 0.75 0.50 50)', {}, 'color(--helmgenlch 0.75 0.5 50)'),
        ('color(--helmgenlch 0.75 0.50 50)', {'fit': False}, 'color(--helmgenlch 0.75 0.5 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHelmgenlchProperties(util.ColorAsserts, unittest.TestCase):
    """Test Helmgenlch."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--helmgenlch 90% 0.5 120 / 1)')
        self.assertEqual(c['lightness'], 0.9)
        c['lightness'] = 0.3
        self.assertEqual(c['lightness'], 0.3)

    def test_chroma(self):
        """Test `chroma`."""

        c = Color('color(--helmgenlch 90% 0.5 120 / 1)')
        self.assertEqual(c['chroma'], 0.5)
        c['chroma'] = 0.2
        self.assertEqual(c['chroma'], 0.2)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--helmgenlch 90% 0.5 120 / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--helmgenlch 90% 0.5 120 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('helmgenlch', [0.75, 0.2, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--helmgenlch 0.75 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('color(--helmgenlch 0.75 0.000000000009 120 / 1)').convert('helmgen').convert('helmgenlch')
        self.assertTrue(c.is_nan('hue'))

    def test_from_helmgen(self):
        """Test null from Helmgen conversion."""

        c1 = Color('color(--helmgen 90% 0 0)')
        c2 = c1.convert('helmgenlch')
        self.assertColorEqual(c2, Color('color(--helmgenlch 90% 0 0)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color('color(--helmgenlch 90% 0 120 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to Helmgenlch with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('helmgenlch')
                self.assertTrue(color2.is_nan('hue'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('helmgenlch', [0.3, 0, 270]).is_achromatic(), True)
        self.assertEqual(Color('helmgenlch', [0.3, 0.0000001, 270]).is_achromatic(), True)
        self.assertEqual(Color('helmgenlch', [NaN, 0.0000001, 270]).is_achromatic(), True)
        self.assertEqual(Color('helmgenlch', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('helmgenlch', [0, 0.4, 270]).is_achromatic(), False)
        self.assertEqual(Color('helmgenlch', [NaN, 0.1, 270]).is_achromatic(), False)
        self.assertEqual(Color('helmgenlch', [0.3, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('helmgenlch', [NaN, NaN, 270]).is_achromatic(), True)
