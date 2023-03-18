"""Test LChuv library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
from coloraide import NaN
import pytest


class TestLChuv(util.ColorAssertsPyTest):
    """Test LChuv."""

    COLORS = [
        ('red', 'color(--lchuv 53.237 179.04 12.177)'),
        ('orange', 'color(--lchuv 74.934 105.26 44.683)'),
        ('yellow', 'color(--lchuv 97.139 107.09 85.874)'),
        ('green', 'color(--lchuv 46.228 71.548 127.72)'),
        ('blue', 'color(--lchuv 32.301 130.69 265.87)'),
        ('indigo', 'color(--lchuv 20.47 62.163 279.33)'),
        ('violet', 'color(--lchuv 69.695 84.743 307.72)'),
        ('white', 'color(--lchuv 100 0 none)'),
        ('gray', 'color(--lchuv 53.585 0 none)'),
        ('black', 'color(--lchuv 0 0 none)'),
        # Test color
        ('color(--lchuv 100 30 270)', 'color(--lchuv 100 30 270)'),
        ('color(--lchuv 100 30 270 / 0.5)', 'color(--lchuv 100 30 270 / 0.5)'),
        ('color(--lchuv 50% 50% 50% / 50%)', 'color(--lchuv 50 110 180 / 0.5)'),
        ('color(--lchuv none none none / none)', 'color(--lchuv none none none / none)'),
        # Test percent ranges
        ('color(--lchuv 0% 0% 0%)', 'color(--lchuv 0 0 none)'),
        ('color(--lchuv 100% 100% 100%)', 'color(--lchuv 100 220 360 / 1)'),
        ('color(--lchuv -100% -100% -100%)', 'color(--lchuv -100 0 -360 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('lchuv'), Color(color2))


class TestLChuvSerialize(util.ColorAssertsPyTest):
    """Test LChuv serialization."""

    COLORS = [
        # Test color
        ('color(--lchuv 75 30 50 / 0.5)', {}, 'color(--lchuv 75 30 50 / 0.5)'),
        # Test alpha
        ('color(--lchuv 75 30 50)', {'alpha': True}, 'color(--lchuv 75 30 50 / 1)'),
        ('color(--lchuv 75 30 50 / 0.5)', {'alpha': False}, 'color(--lchuv 75 30 50)'),
        # Test None
        ('color(--lchuv none 30 50)', {}, 'color(--lchuv 0 30 50)'),
        ('color(--lchuv none 30 50)', {'none': True}, 'color(--lchuv none 30 50)'),
        # Test Fit (not bound)
        ('color(--lchuv 75 230 50)', {}, 'color(--lchuv 75 230 50)'),
        ('color(--lchuv 75 230 50)', {'fit': False}, 'color(--lchuv 75 230 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestLChuvD65Properties(util.ColorAsserts, unittest.TestCase):
    """Test LChuv."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--lchuv 90% 50 120 / 1)')
        self.assertEqual(c['lightness'], 90)
        c['lightness'] = 80
        self.assertEqual(c['lightness'], 80)

    def test_chroma(self):
        """Test `chroma`."""

        c = Color('color(--lchuv 90% 50 120 / 1)')
        self.assertEqual(c['chroma'], 50)
        c['chroma'] = 40
        self.assertEqual(c['chroma'], 40)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--lchuv 90% 50 120 / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--lchuv 90% 50 120 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_real_achromatic_hue(self):
        """Test that we get the expected achromatic hue."""

        self.assertEqual(Color('white').convert('lchuv')._space.achromatic_hue(), 0.0)

    def test_null_input(self):
        """Test null input."""

        c = Color('lchuv', [90, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--lchuv 90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('color(--lchuv 90% 0.000000000009 120 / 1)').convert('luv').convert('lchuv')
        self.assertTrue(c.is_nan('hue'))

    def test_from_luv(self):
        """Test null from Luv conversion."""

        c1 = Color('color(--luv 90% 0 0)')
        c2 = c1.convert('lchuv')
        self.assertColorEqual(c2, Color('color(--lchuv 90% 0 0)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color('color(--lchuv 90% 0 120 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to LChuv with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('lchuv')
                self.assertTrue(color2.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chorma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to lab."""

        self.assertColorEqual(Color('color(--lchuv 90% -10 120 / 1)').convert('luv'), Color('color(--luv 90% 0 0)'))
