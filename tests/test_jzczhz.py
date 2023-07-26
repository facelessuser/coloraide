"""Test JzCzhz library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
from coloraide import NaN
import pytest


class TestJzCzhz(util.ColorAssertsPyTest):
    """Test JzCzhz."""

    COLORS = [
        ('red', 'color(--jzczhz 0.13438 0.16252 43.502)'),
        ('orange', 'color(--jzczhz 0.16937 0.12698 75.776)'),
        ('yellow', 'color(--jzczhz 0.2096 0.1378 102)'),
        ('green', 'color(--jzczhz 0.09203 0.10932 132.99)'),
        ('blue', 'color(--jzczhz 0.09577 0.19029 257.61)'),
        ('indigo', 'color(--jzczhz 0.06146 0.10408 287.05)'),
        ('violet', 'color(--jzczhz 0.16771 0.08468 319.37)'),
        ('white', 'color(--jzczhz 0.22207 0.0002 none)'),
        ('gray', 'color(--jzczhz 0.11827 0.00014 none)'),
        ('black', 'color(--jzczhz 0 0 none)'),
        # Test color
        ('color(--jzczhz 1 0.3 270)', 'color(--jzczhz 1 0.3 270)'),
        ('color(--jzczhz 1 0.3 270 / 0.5)', 'color(--jzczhz 1 0.3 270 / 0.5)'),
        ('color(--jzczhz 50% 50% 50% / 50%)', 'color(--jzczhz 0.5 0.25 180 / 0.5)'),
        ('color(--jzczhz none none none / none)', 'color(--jzczhz none none none / none)'),
        # Test percent ranges
        ('color(--jzczhz 0% 0% 0%)', 'color(--jzczhz 0 0 0)'),
        ('color(--jzczhz 100% 100% 100%)', 'color(--jzczhz 1 0.5 360 / 1)'),
        ('color(--jzczhz -100% -100% -100%)', 'color(--jzczhz 0 0 -360 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('jzczhz'), Color(color2))


class TestJzCzhzSerialize(util.ColorAssertsPyTest):
    """Test JzCzhz serialization."""

    COLORS = [
        # Test color
        ('color(--jzczhz 0.75 0.3 50 / 0.5)', {}, 'color(--jzczhz 0.75 0.3 50 / 0.5)'),
        # Test alpha
        ('color(--jzczhz 0.75 0.3 50)', {'alpha': True}, 'color(--jzczhz 0.75 0.3 50 / 1)'),
        ('color(--jzczhz 0.75 0.3 50 / 0.5)', {'alpha': False}, 'color(--jzczhz 0.75 0.3 50)'),
        # Test None
        ('color(--jzczhz none 0.3 50)', {}, 'color(--jzczhz 0 0.3 50)'),
        ('color(--jzczhz none 0.3 50)', {'none': True}, 'color(--jzczhz none 0.3 50)'),
        # Test Fit (not bound)
        ('color(--jzczhz 0.75 0.6 50)', {}, 'color(--jzczhz 0.75 0.6 50)'),
        ('color(--jzczhz 0.75 0.6 50)', {'fit': False}, 'color(--jzczhz 0.75 0.6 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestJzCzhzProperties(util.ColorAsserts, unittest.TestCase):
    """Test JzCzhz."""

    def test_jz(self):
        """Test `jz`."""

        c = Color('color(--jzczhz 0.22 0.5 270 / 1)')
        self.assertEqual(c['jz'], 0.22)
        c['jz'] = 0.2
        self.assertEqual(c['jz'], 0.2)

    def test_cz(self):
        """Test `chroma`."""

        c = Color('color(--jzczhz 0.22 0.5 270 / 1)')
        self.assertEqual(c['chroma'], 0.5)
        c['chroma'] = 0.1
        self.assertEqual(c['chroma'], 0.1)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--jzczhz 0.22 0.5 270 / 1)')
        self.assertEqual(c['hue'], 270)
        c['hue'] = 0.1
        self.assertEqual(c['hue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--jzczhz 0.22 0.5 270 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)

    def test_hue_name(self):
        """Test `hue_name`."""

        c = Color('color(--jzczhz 0.22 0.5 270 / 1)')
        self.assertEqual(c._space.hue_name(), 'hz')


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('jzczhz', [90, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--jzczhz 90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color(Color('white').convert('jzczhz').to_string(precision=6)).normalize()
        self.assertTrue(c.is_nan('hue'))

        c = Color(Color('gray').convert('jzczhz').to_string(precision=6)).normalize()
        self.assertTrue(c.is_nan('hue'))

        c = Color(Color('darkgray').convert('jzczhz').to_string(precision=6)).normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to OkLCh with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('jzczhz')
                self.assertTrue(color2.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chorma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to Jzazbz."""

        self.assertColorEqual(
            Color('color(--jzczhz 90% -10 120 / 1)').convert('jzazbz'), Color('color(--jzazbz 0.9 0 0)')
        )


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('#222222').convert('jzczhz').is_achromatic(), True)
        self.assertEqual(Color('#222222').convert('jzczhz').set('cz', lambda x: x + 1e-8).is_achromatic(), True)
        self.assertEqual(Color('srgb', [5.2, 5.2, 5.2]).convert('jzczhz').is_achromatic(), True)
        self.assertEqual(Color('jzczhz', [NaN, 0.00001, 270]).is_achromatic(), True)
        self.assertEqual(Color('jzczhz', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('jzczhz', [0, 0.5, 270]).is_achromatic(), True)
        self.assertEqual(Color('pink').convert('jzczhz').is_achromatic(), False)
        self.assertEqual(Color('jzczhz', [NaN, 0.5, 270]).is_achromatic(), True)
        self.assertEqual(Color('jzczhz', [0.2, NaN, 270]).is_achromatic(), False)
        self.assertEqual(Color('jzczhz', [NaN, NaN, 270]).is_achromatic(), True)
