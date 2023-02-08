"""Test CAM16 JMh."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestCAM16JMh(util.ColorAssertsPyTest):
    """Test CAM16 JMh."""

    COLORS = [
        ('red', 'color(--cam16-jmh 46.026 81.254 27.393)'),
        ('orange', 'color(--cam16-jmh 68.056 43.51 71.293)'),
        ('yellow', 'color(--cam16-jmh 94.682 54.5 111.15)'),
        ('green', 'color(--cam16-jmh 33.976 50.934 142.3)'),
        ('blue', 'color(--cam16-jmh 25.066 62.442 282.75)'),
        ('indigo', 'color(--cam16-jmh 16.046 43.278 310.9)'),
        ('violet', 'color(--cam16-jmh 63.507 46.779 331.39)'),
        ('white', 'color(--cam16-jmh 100 2.2369 0)'),
        ('gray', 'color(--cam16-jmh 43.042 1.467 0)'),
        ('black', 'color(--cam16-jmh 0 0 0)'),
        # Test color
        ('color(--cam16-jmh 50 30 270)', 'color(--cam16-jmh 50 30 270)'),
        ('color(--cam16-jmh 50 30 270 / 0.5)', 'color(--cam16-jmh 50 30 270 / 0.5)'),
        ('color(--cam16-jmh 50% 50% 50% / 50%)', 'color(--cam16-jmh 50 52.5 180 / 0.5)'),
        ('color(--cam16-jmh none none none / none)', 'color(--cam16-jmh none none none / none)'),
        # Test percent ranges
        ('color(--cam16-jmh 0% 0% 0%)', 'color(--cam16-jmh 0 0 0)'),
        ('color(--cam16-jmh 100% 100% 100%)', 'color(--cam16-jmh 100 105 360 / 1)'),
        ('color(--cam16-jmh -100% -100% -100%)', 'color(--cam16-jmh 0 0 -360 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam16-jmh'), Color(color2))


class TestCAM16JMhRevere(util.ColorAssertsPyTest):
    """Test CAM16 JMh conversions in reverse."""

    COLORS = [
        # CAM16 has a specific limit for a given lightness that determines
        # when a color is achromatic. This is specific to when `discounting=False`.
        # Anything below the limit will start giving you non-achromatic colors
        # again. Internally, we catch this handle them as achromatic.
        ('color(--cam16-jmh 0.5 0 0)', 'rgb(0.24033 0.23714 0.23654)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('srgb'), Color(color2))


class TestCAM16JMhPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM16 JMh properties."""

    def test_names(self):
        """Test LCh-ish names."""

        self.assertEqual(Color('color(--cam16-jmh 97.139 75.504 111.05)')._space.lchish_names(), ('j', 'm', 'h'))

    def test_h(self):
        """Test `h`."""

        c = Color('color(--cam16-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['h'], 111.05)
        c['h'] = 270
        self.assertEqual(c['h'], 270)

    def test_c(self):
        """Test `m`."""

        c = Color('color(--cam16-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['m'], 75.504)
        c['m'] = 30
        self.assertEqual(c['m'], 30)

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam16-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['j'], 97.139)
        c['j'] = 50
        self.assertEqual(c['j'], 50)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam16-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_real_achromatic_hue(self):
        """Test that we get the expected achromatic hue."""

        self.assertEqual(Color('white').convert('cam16-jmh')._space.achromatic_hue(), 209.5333344635329)

    def test_null_input(self):
        """Test null input."""

        c = Color('cam16-jmh', [30, 20, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--cam16-jmh 30 20 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color('color(--cam16-jmh 740 0.03 90 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

        c = Color('color(--cam16-jmh 30 0.03 90 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

        c = Color('color(--cam16-jmh 1 0.03 30)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to CAM16 JMh with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('cam16-jmh')
                self.assertTrue(color2.is_nan('hue'))
