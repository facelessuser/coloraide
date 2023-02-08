"""Test HSL library."""
from coloraide import NaN
import unittest
from . import util
from coloraide import Color
import pytest


class TestHSL(util.ColorAssertsPyTest):
    """Test HSL."""

    COLORS = [
        ('red', 'color(--hsl 0 1 0.5)'),
        ('orange', 'color(--hsl 38.824 1 0.5)'),
        ('yellow', 'color(--hsl 60 1 0.5)'),
        ('green', 'color(--hsl 120 1 0.25098)'),
        ('blue', 'color(--hsl 240 1 0.5)'),
        ('indigo', 'color(--hsl 274.62 1 0.2549)'),
        ('violet', 'color(--hsl 300 0.76056 0.72157)'),
        ('white', 'color(--hsl none 0 1)'),
        ('gray', 'color(--hsl none 0 0.50196)'),
        ('black', 'color(--hsl none 0 0)'),
        # Test legacy CSS
        ('hsl(270, 30%, 50%)', 'color(--hsl 270 0.3 0.5)'),
        ('hsl(270, 30%, 50%, 0.5)', 'color(--hsl 270 0.3 0.5 / 0.5)'),
        ('hsl(270, 30%, 50%, 50%)', 'color(--hsl 270 0.3 0.5 / 0.5)'),
        ('hsla(270, 30%, 50%)', 'color(--hsl 270 0.3 0.5)'),
        ('hsla(270, 30%, 50%, 0.5)', 'color(--hsl 270 0.3 0.5 / 0.5)'),
        ('hsla(270, 30%, 50%, 50%)', 'color(--hsl 270 0.3 0.5 / 0.5)'),
        ('hsl(none, 30%, 50%)', None),
        ('hsl(50%, 50%, 50%)', None),
        ('hsla(none, 30%, 50%)', None),
        ('hsla(50%, 50%, 50%)', None),
        # Test CSS
        ('hsl(270 30% 50%)', 'color(--hsl 270 0.3 0.5)'),
        ('hsl(270 30% 50% / 0.5)', 'color(--hsl 270 0.3 0.5 / 0.5)'),
        ('hsl(270 30% 50% / 50%)', 'color(--hsl 270 0.3 0.5 / 0.5)'),
        ('hsl(none none none / none)', 'color(--hsl none none none / none)'),
        ('hsla(270 30% 50%)', 'color(--hsl 270 0.3 0.5)'),
        ('hsla(270 30% 50% / 0.5)', 'color(--hsl 270 0.3 0.5 / 0.5)'),
        ('hsla(270 30% 50% / 50%)', 'color(--hsl 270 0.3 0.5 / 0.5)'),
        ('hsla(none none none / none)', 'color(--hsl none none none / none)'),
        ('hsl(50% 30 50)', None),
        # Test CSS color
        ('color(--hsl 270 0.3 0.5)', 'color(--hsl 270 0.3 0.5)'),
        ('color(--hsl 270 0.3 0.5 / 0.5)', 'color(--hsl 270 0.3 0.5 / 0.5)'),
        ('color(--hsl 50% 50% 50% / 50%)', 'color(--hsl 180 0.5 0.5 / 0.5)'),
        ('color(--hsl none none none / none)', 'color(--hsl none none none / none)'),
        # Test range
        ('color(--hsl 0% 0% 0%)', 'color(--hsl 0 0 0)'),
        ('color(--hsl 100% 100% 100%)', 'color(--hsl 360 1 1)'),
        ('color(--hsl -100% -100% -100%)', 'color(--hsl -360 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        if color2 is None:
            with pytest.raises(ValueError):
                Color(color1)
        else:
            self.assertColorEqual(Color(color1).convert('hsl'), Color(color2), color=True)


class TestHSLSerialize(util.ColorAssertsPyTest):
    """Test HSL serialization."""

    COLORS = [
        # Test hex no options
        ('hsl(270 30% 75%)', {}, 'hsl(270 30% 75%)'),
        # Test alpha
        ('hsl(270 30% 75% / 0.5)', {}, 'hsl(270 30% 75% / 0.5)'),
        ('hsl(270 30% 75%)', {'alpha': True}, 'hsl(270 30% 75% / 1)'),
        ('hsl(270 30% 75% / 0.5)', {'alpha': False}, 'hsl(270 30% 75%)'),
        # Test None
        ('hsl(none 30% 75%)', {}, 'hsl(0 30% 75%)'),
        ('hsl(none 30% 75%)', {'none': True}, 'hsl(none 30% 75%)'),
        # Test fit
        ('hsl(20 150% 75%)', {}, 'hsl(19.619 100% 76.43%)'),
        ('hsl(20 150% 75%)', {'fit': False}, 'hsl(20 150% 75%)'),
        # Test legacy
        ('hsl(270 30% 75%)', {'comma': True}, 'hsl(270, 30%, 75%)'),
        # Test legacy alpha
        ('hsl(270 30% 75% / 0.5)', {'comma': True}, 'hsla(270, 30%, 75%, 0.5)'),
        ('hsl(270 30% 75%)', {'comma': True, 'alpha': True}, 'hsla(270, 30%, 75%, 1)'),
        ('hsl(270 30% 75% / 0.5)', {'comma': True, 'alpha': False}, 'hsl(270, 30%, 75%)'),
        # Test legacy None
        ('hsl(none 30% 75%)', {'comma': True}, 'hsl(0, 30%, 75%)'),
        ('hsl(none 30% 75%)', {'comma': True, 'none': True}, 'hsl(0, 30%, 75%)'),
        # Test color
        ('hsl(none 30% 75% / 0.5)', {'color': True}, 'color(--hsl 0 0.3 0.75 / 0.5)'),
        ('hsl(none 30% 75%)', {'color': True, 'none': True}, 'color(--hsl none 0.3 0.75)'),
        ('hsl(0 30% 75%)', {'color': True, 'alpha': True}, 'color(--hsl 0 0.3 0.75 / 1)'),
        ('hsl(0 30% 75% / 0.5)', {'color': True, 'alpha': False}, 'color(--hsl 0 0.3 0.75)'),
        # Test Fit
        ('color(--hsl 0 -1.1 0.3)', {'color': True}, 'color(--hsl 180 1 0.3028)'),
        ('color(--hsl 0 -1.1 0.3)', {'color': True, 'fit': False}, 'color(--hsl 0 -1.1 0.3)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHSLProperties(util.ColorAsserts, unittest.TestCase):
    """Test HSL."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_saturation(self):
        """Test `saturation`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c['saturation'], 0.5)
        c['saturation'] = 0.6
        self.assertEqual(c['saturation'], 0.6)

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c['lightness'], 0.9)
        c['lightness'] = 0.8
        self.assertEqual(c['lightness'], 0.8)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hsl 120 50% 90% / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_real_achromatic_hue(self):
        """Test that we get the expected achromatic hue."""

        self.assertEqual(Color('white').convert('hsl')._space.achromatic_hue(), 0.0)

    def test_null_input(self):
        """Test null input."""

        c = Color('hsl', [NaN, 0.5, 1], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('hsl(none 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_sat(self):
        """Test minimum saturation."""

        c = Color('hsl(270 0% 75% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_max_light(self):
        """Test maximum lightness."""

        c = Color('hsl(270 20% 100% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_light(self):
        """Test minimum lightness."""

        c = Color('hsl(270 20% 0% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_corner_case_null(self):
        """Test corner case that produces null."""

        c = Color('color(srgb -2 0 2)').convert('hsl')
        self.assertTrue(c.is_nan('hue'))
