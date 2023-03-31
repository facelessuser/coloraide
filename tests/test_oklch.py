"""Test OkLCh library."""
import unittest
from . import util
from coloraide import NaN
from coloraide import Color
import pytest


class TestsOkLCh(util.ColorAssertsPyTest):
    """Test OkLCh."""

    COLORS = [
        # Test general conversion
        ('red', 'color(--oklch 0.62796 0.25768 29.234)'),
        ('orange', 'color(--oklch 0.79269 0.17103 70.67)'),
        ('yellow', 'color(--oklch 0.96798 0.21101 109.77)'),
        ('green', 'color(--oklch 0.51975 0.17686 142.5)'),
        ('blue', 'color(--oklch 0.45201 0.31321 264.05)'),
        ('indigo', 'color(--oklch 0.33898 0.17927 301.68)'),
        ('violet', 'color(--oklch 0.7619 0.18612 327.21)'),
        ('white', 'color(--oklch 1 0 none)'),
        ('gray', 'color(--oklch 0.59987 0 none)'),
        ('black', 'color(--oklch 0 0 none)'),
        # Test CSS
        ('oklch(1 0.3 270)', 'color(--oklch 1 0.3 270 / 1)'),
        ('oklch(1 0.3 270 / 0.5)', 'color(--oklch 1 0.3 270 / 0.5)'),
        ('oklch(50% 0.3 270)', 'color(--oklch 0.5 0.3 270 / 1)'),
        ('oklch(50% 50% 270 / 50%)', 'color(--oklch 0.5 0.2 270 / 0.5)'),
        ('oklch(none none none / none)', 'color(--oklch none none none / none)'),
        ('oklch(1 0.3 50%)', None),
        ('oklch(1, 0.3, 50)', None),
        # Test degrees
        ('oklch(0.75 0.2 180deg)', 'color(--oklch 0.75 0.2 180 / 1)'),
        ('oklch(0.75 0.2 0.5turn)', 'color(--oklch 0.75 0.2 180 / 1)'),
        ('oklch(0.75 0.2 3.14159rad)', 'color(--oklch 0.75 0.2 180 / 1)'),
        ('oklch(0.75 0.2 200grad)', 'color(--oklch 0.75 0.2 180 / 1)'),
        # Test color
        ('color(--oklch 1 0.3 270)', 'color(--oklch 1 0.3 270)'),
        ('color(--oklch 1 0.3 270 / 0.5)', 'color(--oklch 1 0.3 270 / 0.5)'),
        ('color(--oklch 50% 50% 50% / 50%)', 'color(--oklch 0.5 0.2 180 / 0.5)'),
        ('color(--oklch none none none / none)', 'color(--oklch none none none / none)'),
        # Test percent ranges
        ('color(--oklch 0% 0% 0%)', 'color(--oklch 0 0 0)'),
        ('color(--oklch 100% 100% 100%)', 'color(--oklch 1 0.4 360 / 1)'),
        ('color(--oklch -100% -100% -100%)', 'color(--oklch -1 0 -360 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        if color2 is None:
            with pytest.raises(ValueError):
                Color(color1)
        else:
            self.assertColorEqual(Color(color1).convert('oklch'), Color(color2), color=True)


class TestOkLChSerialize(util.ColorAssertsPyTest):
    """Test OkLCh serialization."""

    COLORS = [
        # Test hex no options
        ('oklch(0.75 0.3 50)', {}, 'oklch(0.75 0.3 50)'),
        # Test alpha
        ('oklch(0.75 0.3 50 / 0.5)', {}, 'oklch(0.75 0.3 50 / 0.5)'),
        ('oklch(0.75 0.3 50)', {'alpha': True}, 'oklch(0.75 0.3 50 / 1)'),
        ('oklch(0.75 0.3 50 / 0.5)', {'alpha': False}, 'oklch(0.75 0.3 50)'),
        # Test percent
        ('oklch(0.5 0.2 180)', {'percent': True}, 'oklch(50% 50% 180)'),
        ('oklch(0.5 0.2 180 / 0.5)', {'percent': True, 'alpha': True}, 'oklch(50% 50% 180 / 0.5)'),
        # Test None
        ('oklch(none 0.3 50)', {}, 'oklch(0 0.3 50)'),
        ('oklch(none 0.3 50)', {'none': True}, 'oklch(none 0.3 50)'),
        # Test fit (not bound)
        ('oklch(0.2 0.5 0)', {}, 'oklch(0.2 0.5 0)'),
        ('oklch(0.2 0.5 0)', {'fit': False}, 'oklch(0.2 0.5 0)'),
        # Test color
        ('oklch(none 0.3 50 / 0.5)', {'color': True}, 'color(--oklch 0 0.3 50 / 0.5)'),
        ('oklch(none 0.3 50)', {'color': True, 'none': True}, 'color(--oklch none 0.3 50)'),
        ('oklch(0 0.3 50)', {'color': True, 'alpha': True}, 'color(--oklch 0 0.3 50 / 1)'),
        ('oklch(0 0.3 50 / 0.5)', {'color': True, 'alpha': False}, 'color(--oklch 0 0.3 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestOkLChProperties(util.ColorAsserts, unittest.TestCase):
    """Test OkLCh."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--oklch 0.9 0.5 270 / 1)')
        self.assertEqual(c['lightness'], 0.9)
        c['lightness'] = 0.2
        self.assertEqual(c['lightness'], 0.2)

    def test_chroma(self):
        """Test `chroma`."""

        c = Color('color(--oklch 0.9 0.5 270 / 1)')
        self.assertEqual(c['chroma'], 0.5)
        c['chroma'] = 0.1
        self.assertEqual(c['chroma'], 0.1)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--oklch 0.9 0.5 270 / 1)')
        self.assertEqual(c['hue'], 270)
        c['hue'] = 0.1
        self.assertEqual(c['hue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--oklch 0.9 0.5 270 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('oklch', [0.9, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--oklch 90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('color(--oklch 90% 0.00000009 120 / 1)').convert('srgb').convert('oklch')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color('oklch(90% 0 120 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_from_oklab(self):
        """Test null from Lab conversion."""

        c1 = Color('color(--oklab 90% 0 0)')
        c2 = c1.convert('oklch')
        self.assertColorEqual(c2, Color('color(--oklch 90% 0 none)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to OkLCh with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('oklch')
                self.assertTrue(color2.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chorma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to Oklab."""

        self.assertColorEqual(Color('color(--oklch 90% -10 120 / 1)').convert('oklab'), Color('color(--oklab 0.9 0 0)'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('oklch', [0.3, 0, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklch', [0.3, 0.000001, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklch', [NaN, 0.00001, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklch', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklch', [0, 1, 270]).is_achromatic(), False)
        self.assertEqual(Color('oklch', [NaN, 0.2, 270]).is_achromatic(), False)
        self.assertEqual(Color('oklch', [0.3, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklch', [NaN, NaN, 270]).is_achromatic(), True)
