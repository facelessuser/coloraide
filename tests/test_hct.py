"""Test HCT."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestHCT(util.ColorAssertsPyTest):
    """Test HCT."""

    COLORS = [
        ('red', 'color(--hct 27.41 113.36 53.237)'),
        ('orange', 'color(--hct 71.257 60.528 74.934)'),
        ('yellow', 'color(--hct 111.05 75.504 97.139)'),
        ('green', 'color(--hct 142.23 71.136 46.228)'),
        ('blue', 'color(--hct 282.76 87.228 32.301)'),
        ('indigo', 'color(--hct 310.96 60.765 20.47)'),
        ('violet', 'color(--hct 331.49 65.001 69.695)'),
        ('white', 'color(--hct 209.54 2.8716 100)'),
        ('gray', 'color(--hct 209.54 1.8977 53.585)'),
        ('black', 'color(--hct 209.55 0 0)'),
        # Test color
        ('color(--hct 270 30 100)', 'color(--hct 270 30 100)'),
        ('color(--hct 270 30 100 / 0.5)', 'color(--hct 270 30 100 / 0.5)'),
        ('color(--hct 50% 50% 50% / 50%)', 'color(--hct 180 72.5 50 / 0.5)'),
        ('color(--hct none none none / none)', 'color(--hct none none none / none)'),
        # Test percent ranges
        ('color(--hct 0% 0% 0%)', 'color(--hct 0 0 none)'),
        ('color(--hct 100% 100% 100%)', 'color(--hct 360 145 100 / 1)'),
        ('color(--hct -100% -100% -100%)', 'color(--hct -360 0 0 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hct'), Color(color2))


class TestHCTSerialize(util.ColorAssertsPyTest):
    """Test HCT serialization."""

    COLORS = [
        # Test color
        ('color(--hct 50 30 75 / 0.5)', {}, 'color(--hct 50 30 75 / 0.5)'),
        # Test alpha
        ('color(--hct 50 30 75)', {'alpha': True}, 'color(--hct 50 30 75 / 1)'),
        ('color(--hct 50 30 75 / 0.5)', {'alpha': False}, 'color(--hct 50 30 75)'),
        # Test None
        ('color(--hct 50 30 none)', {}, 'color(--hct 50 30 0)'),
        ('color(--hct 50 30 none)', {'none': True}, 'color(--hct 50 30 none)'),
        # Test Fit (not bound)
        ('color(--hct 50 230 75)', {}, 'color(--hct 50 230 75)'),
        ('color(--hct 50 230 75)', {'fit': False}, 'color(--hct 50 230 75)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHCTMisc(util.ColorAsserts, unittest.TestCase):
    """Test miscellaneous cases."""

    def test_wide_gamut(self):
        """Test wide gamut conversion logic."""

        c1 = Color('hct', (330.2920013462662, 484.58580542051413, 91.57114928085913))
        c2 = c1.convert('xyy').convert('hct')
        self.assertColorEqual(c1, c2)


class TestHCTPoperties(util.ColorAsserts, unittest.TestCase):
    """Test HCT properties."""

    def test_names(self):
        """Test LCh-ish names."""

        self.assertEqual(Color('color(--hct 111.05 75.504 97.139)')._space.names(), ('t', 'c', 'h'))

    def test_h(self):
        """Test `h`."""

        c = Color('color(--hct 111.05 75.504 97.139)')
        self.assertEqual(c['h'], 111.05)
        c['h'] = 270
        self.assertEqual(c['h'], 270)

    def test_c(self):
        """Test `c`."""

        c = Color('color(--hct 111.05 75.504 97.139)')
        self.assertEqual(c['c'], 75.504)
        c['c'] = 30
        self.assertEqual(c['c'], 30)

    def test_t(self):
        """Test `t`."""

        c = Color('color(--hct 111.05 75.504 97.139)')
        self.assertEqual(c['t'], 97.139)
        c['t'] = 50
        self.assertEqual(c['t'], 50)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hct 111.05 75.504 97.139)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('hct', [NaN, 20, 30], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--hct none 20 30 / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color(Color('white').convert('hct').to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

        c = Color(Color('gray').convert('hct').to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

        c = Color(Color('darkgray').convert('hct').to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to HCT with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('hct')
                self.assertTrue(color2.is_nan('hue'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('#222222').convert('hct').is_achromatic(), True)
        self.assertEqual(
            Color('srgb', [0.000000001] * 3).convert('hct').set('c', lambda x: x + 1e-8).is_achromatic(),
            True
        )
        self.assertEqual(Color('hct', [270, 0.00001, NaN]).is_achromatic(), True)
        self.assertEqual(Color('hct', [270, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('hct', [270, 50, 0]).is_achromatic(), True)
        self.assertEqual(Color('hct', [270, 50, NaN]).is_achromatic(), True)
        self.assertEqual(Color('hct', [270, NaN, 20]).is_achromatic(), False)
        self.assertEqual(Color('hct', [270, NaN, NaN]).is_achromatic(), True)
