"""Test OkLrCh library."""
import unittest
from . import util
from coloraide import NaN
from coloraide.everything import ColorAll as Color
import pytest


class TestsOkLrCh(util.ColorAssertsPyTest):
    """Test OkLrCh."""

    COLORS = [
        # Test general conversion
        ('red', 'color(--oklrch 0.56808 0.25768 29.234)'),
        ('orange', 'color(--oklrch 0.75883 0.17103 70.67)'),
        ('yellow', 'color(--oklrch 0.9627 0.21101 109.77)'),
        ('green', 'color(--oklrch 0.44371 0.17686 142.5)'),
        ('blue', 'color(--oklrch 0.36657 0.31321 264.05)'),
        ('indigo', 'color(--oklrch 0.24043 0.17927 301.68)'),
        ('violet', 'color(--oklrch 0.7231 0.18612 327.21)'),
        ('white', 'color(--oklrch 1 0 none)'),
        ('gray', 'color(--oklrch 0.53571 0 0)'),
        ('black', 'color(--oklrch 0 0 none)'),
        # Test degrees
        ('color(--oklrch 0.75 0.2 180deg)', 'color(--oklrch 0.75 0.2 180 / 1)'),
        ('color(--oklrch 0.75 0.2 0.5turn)', 'color(--oklrch 0.75 0.2 180 / 1)'),
        ('color(--oklrch 0.75 0.2 3.14159rad)', 'color(--oklrch 0.75 0.2 180 / 1)'),
        ('color(--oklrch 0.75 0.2 200grad)', 'color(--oklrch 0.75 0.2 180 / 1)'),
        # Test color
        ('color(--oklrch 1 0.3 270)', 'color(--oklrch 1 0.3 270)'),
        ('color(--oklrch 1 0.3 270 / 0.5)', 'color(--oklrch 1 0.3 270 / 0.5)'),
        ('color(--oklrch 50% 50% 180 / 50%)', 'color(--oklrch 0.5 0.2 180 / 0.5)'),
        ('color(--oklrch none none none / none)', 'color(--oklrch none none none / none)'),
        # Test percent ranges
        ('color(--oklrch 0% 0% 0)', 'color(--oklrch 0 0 0)'),
        ('color(--oklrch 100% 100% 360)', 'color(--oklrch 1 0.4 360 / 1)'),
        ('color(--oklrch -100% -100% -360)', 'color(--oklrch -1 -0.4 -360 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        if color2 is None:
            with pytest.raises(ValueError):
                Color(color1)
        else:
            self.assertColorEqual(Color(color1).convert('oklrch'), Color(color2), color=True)


class TestOkLrChSerialize(util.ColorAssertsPyTest):
    """Test OkLrCh serialization."""

    COLORS = [
        # Test no options
        ('color(--oklrch 0.75 0.3 50)', {}, 'color(--oklrch 0.75 0.3 50)'),
        # Test alpha
        ('color(--oklrch 0.75 0.3 50 / 0.5)', {}, 'color(--oklrch 0.75 0.3 50 / 0.5)'),
        ('color(--oklrch 0.75 0.3 50)', {'alpha': True}, 'color(--oklrch 0.75 0.3 50 / 1)'),
        ('color(--oklrch 0.75 0.3 50 / 0.5)', {'alpha': False}, 'color(--oklrch 0.75 0.3 50)'),
        # Test percent
        ('color(--oklrch 0.5 0.2 180)', {'percent': True}, 'color(--oklrch 50% 50% 180)'),
        ('color(--oklrch 0.5 0.2 180 / 0.5)', {'percent': True, 'alpha': True}, 'color(--oklrch 50% 50% 180 / 0.5)'),
        # Test None
        ('color(--oklrch none 0.3 50)', {}, 'color(--oklrch 0 0.3 50)'),
        ('color(--oklrch none 0.3 50)', {'none': True}, 'color(--oklrch none 0.3 50)'),
        # Test fit (not bound)
        ('color(--oklrch 0.2 0.5 0)', {}, 'color(--oklrch 0.2 0.5 0)'),
        ('color(--oklrch 0.2 0.5 0)', {'fit': False}, 'color(--oklrch 0.2 0.5 0)'),
        # Test color
        ('color(--oklrch none 0.3 50 / 0.5)', {'color': True}, 'color(--oklrch 0 0.3 50 / 0.5)'),
        ('color(--oklrch none 0.3 50)', {'color': True, 'none': True}, 'color(--oklrch none 0.3 50)'),
        ('color(--oklrch 0 0.3 50)', {'color': True, 'alpha': True}, 'color(--oklrch 0 0.3 50 / 1)'),
        ('color(--oklrch 0 0.3 50 / 0.5)', {'color': True, 'alpha': False}, 'color(--oklrch 0 0.3 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestOkLrChProperties(util.ColorAsserts, unittest.TestCase):
    """Test OkLrCh."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--oklrch 0.9 0.5 270 / 1)')
        self.assertEqual(c['lightness'], 0.9)
        c['lightness'] = 0.2
        self.assertEqual(c['lightness'], 0.2)

    def test_chroma(self):
        """Test `chroma`."""

        c = Color('color(--oklrch 0.9 0.5 270 / 1)')
        self.assertEqual(c['chroma'], 0.5)
        c['chroma'] = 0.1
        self.assertEqual(c['chroma'], 0.1)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--oklrch 0.9 0.5 270 / 1)')
        self.assertEqual(c['hue'], 270)
        c['hue'] = 0.1
        self.assertEqual(c['hue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--oklrch 0.9 0.5 270 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('oklrch', [0.9, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--oklrch 90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('color(--oklrch 90% 0.00000009 120 / 1)').convert('srgb').convert('oklrch')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color('color(--oklrch 90% 0 120 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_from_oklab(self):
        """Test null from Lab conversion."""

        c1 = Color('color(--oklrab 90% 0 0)')
        c2 = c1.convert('oklrch')
        self.assertColorEqual(c2, Color('color(--oklrch 90% 0 none)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to OkLrCh with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('oklrch')
                self.assertTrue(color2.is_nan('hue'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('oklrch', [0.3, 0, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklrch', [0.3, 0.000001, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklrch', [NaN, 0.00001, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklrch', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklrch', [0, 1, 270]).is_achromatic(), False)
        self.assertEqual(Color('oklrch', [NaN, 0.2, 270]).is_achromatic(), False)
        self.assertEqual(Color('oklrch', [0.3, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('oklrch', [NaN, NaN, 270]).is_achromatic(), True)
