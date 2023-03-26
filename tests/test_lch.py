"""Test LCh library."""
import unittest
from . import util
from coloraide import Color, NaN
import pytest


class TestLCh(util.ColorAssertsPyTest):
    """Test LCh."""

    COLORS = [
        ('red', 'color(--lch 54.291 106.84 40.858)'),
        ('orange', 'color(--lch 75.59 83.769 70.824)'),
        ('yellow', 'color(--lch 97.607 94.712 99.572)'),
        ('green', 'color(--lch 46.278 67.984 134.38)'),
        ('blue', 'color(--lch 29.568 131.2 301.36)'),
        ('indigo', 'color(--lch 19.715 71.818 310.91)'),
        ('violet', 'color(--lch 69.618 64.617 325.57)'),
        ('white', 'color(--lch 100 0 none)'),
        ('gray', 'color(--lch 53.585 0 none)'),
        ('black', 'color(--lch 0 0 none)'),
        # Test CSS
        ('lch(100 30 270)', 'color(--lch 100 30 270 / 1)'),
        ('lch(100 30 270 / 0.5)', 'color(--lch 100 30 270 / 0.5)'),
        ('lch(50% 30 270)', 'color(--lch 50 30 270 / 1)'),
        ('lch(50% 50% 270 / 50%)', 'color(--lch 50 75 270 / 0.5)'),
        ('lch(none none none / none)', 'color(--lch none none none / none)'),
        ('lch(1 30 50%)', None),
        ('lch(1, 30, 50)', None),
        ('lch(1 30)', None),
        ('lch(1deg 30 270)', None),
        ('lch(1 30 270 50%)', None),
        # Test degrees
        ('lch(75 20 180deg)', 'color(--lch 75 20 180 / 1)'),
        ('lch(75 20 0.5turn)', 'color(--lch 75 20 180 / 1)'),
        ('lch(75 20 3.14159rad)', 'color(--lch 75 20 180 / 1)'),
        ('lch(75 20 200grad)', 'color(--lch 75 20 180 / 1)'),
        # Test color
        ('color(--lch 100 30 270)', 'color(--lch 100 30 270)'),
        ('color(--lch 100 30 270 / 0.5)', 'color(--lch 100 30 270 / 0.5)'),
        ('color(--lch 50% 50% 50% / 50%)', 'color(--lch 50 75 180 / 0.5)'),
        ('color(--lch none none none / none)', 'color(--lch none none none / none)'),
        # Test percent ranges
        ('color(--lch 0% 0% 0%)', 'color(--lch 0 0 none)'),
        ('color(--lch 100% 100% 100%)', 'color(--lch 100 150 360 / 1)'),
        ('color(--lch -100% -100% -100%)', 'color(--lch -100 0 -360 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        if color2 is None:
            with pytest.raises(ValueError):
                Color(color1)
        else:
            self.assertColorEqual(Color(color1).convert('lch'), Color(color2), color=True)


class TestLChSerialize(util.ColorAssertsPyTest):
    """Test LCh serialization."""

    COLORS = [
        # Test hex no options
        ('lch(75 30 50)', {}, 'lch(75 30 50)'),
        # Test alpha
        ('lch(75 30 50 / 0.5)', {}, 'lch(75 30 50 / 0.5)'),
        ('lch(75 30 50)', {'alpha': True}, 'lch(75 30 50 / 1)'),
        ('lch(75 30 50 / 0.5)', {'alpha': False}, 'lch(75 30 50)'),
        # Test percent
        ('lch(50 75 180)', {'percent': True}, 'lch(50% 50% 180)'),
        ('lch(50 75 180 / 0.5)', {'percent': True, 'alpha': True}, 'lch(50% 50% 180 / 0.5)'),
        # Test None
        ('lch(none 30 50)', {}, 'lch(0 30 50)'),
        ('lch(none 30 50)', {'none': True}, 'lch(none 30 50)'),
        # Test fit (not bound)
        ('lch(20 160 0)', {}, 'lch(20 160 0)'),
        ('lch(20 160 0)', {'fit': False}, 'lch(20 160 0)'),
        # Test color
        ('lch(none 30 50 / 0.5)', {'color': True}, 'color(--lch 0 30 50 / 0.5)'),
        ('lch(none 30 50)', {'color': True, 'none': True}, 'color(--lch none 30 50)'),
        ('lch(0 30 50)', {'color': True, 'alpha': True}, 'color(--lch 0 30 50 / 1)'),
        ('lch(0 30 50 / 0.5)', {'color': True, 'alpha': False}, 'color(--lch 0 30 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestLChProperties(util.ColorAsserts, unittest.TestCase):
    """Test LCh."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--lch 90% 50 120 / 1)')
        self.assertEqual(c['lightness'], 90)
        c['lightness'] = 80
        self.assertEqual(c['lightness'], 80)

    def test_chroma(self):
        """Test `chroma`."""

        c = Color('color(--lch 90% 50 120 / 1)')
        self.assertEqual(c['chroma'], 50)
        c['chroma'] = 40
        self.assertEqual(c['chroma'], 40)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--lch 90% 50 120 / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--lch 90% 50 120 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('lch', [90, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('lch(90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('lch(90% 0.000000000009 120 / 1)').convert('lab').convert('lch')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color('lch(90% 0 120 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_from_lab(self):
        """Test null from Lab conversion."""

        c1 = Color('lab(90% 0 0)')
        c2 = c1.convert('lch')
        self.assertColorEqual(c2, Color('lch(90% 0 0)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to LCh with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('lch')
                self.assertTrue(color2.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chorma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to lab."""

        self.assertColorEqual(Color('lch(90% -10 120 / 1)').convert('lab'), Color('lab(90% 0 0)'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('lch', [30, 0, 270]).is_achromatic(), True)
        self.assertEqual(Color('lch', [30, 0.000001, 270]).is_achromatic(), True)
        self.assertEqual(Color('lch', [NaN, 0.00001, 270]).is_achromatic(), True)
        self.assertEqual(Color('lch', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('lch', [0, 100, 270]).is_achromatic(), False)
        self.assertEqual(Color('lch', [NaN, 20, 270]).is_achromatic(), False)
        self.assertEqual(Color('lch', [30, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('lch', [NaN, NaN, 270]).is_achromatic(), True)
