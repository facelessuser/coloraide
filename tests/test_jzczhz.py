"""Test JzCzhz library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
from coloraide import NaN
import pytest


class TestJzCzhz(util.ColorAssertsPyTest):
    """Test JzCzhz."""

    COLORS = [
        ('red', 'jzczhz(0.13438 0.16252 43.502)'),
        ('orange', 'jzczhz(0.16937 0.12698 75.776)'),
        ('yellow', 'jzczhz(0.2096 0.1378 102)'),
        ('green', 'jzczhz(0.09203 0.10932 132.99)'),
        ('blue', 'jzczhz(0.09577 0.19029 257.61)'),
        ('indigo', 'jzczhz(0.06146 0.10408 287.05)'),
        ('violet', 'jzczhz(0.16771 0.08468 319.37)'),
        ('white', 'jzczhz(0.22207 0.0002 216.08)'),
        ('gray', 'jzczhz(0.11827 0.00014 216.08)'),
        ('black', 'jzczhz(0 0 none)'),
        # Test color
        ('jzczhz(1 0.3 270)', 'jzczhz(1 0.3 270)'),
        ('jzczhz(1 0.3 270 / 0.5)', 'jzczhz(1 0.3 270 / 0.5)'),
        ('jzczhz(50% 50% 180 / 50%)', 'jzczhz(0.5 0.13 180 / 0.5)'),
        ('jzczhz(none none none / none)', 'jzczhz(none none none / none)'),
        # Test percent ranges
        ('jzczhz(0% 0% 0)', 'jzczhz(0 0 0)'),
        ('jzczhz(100% 100% 360)', 'jzczhz(1 0.26 360 / 1)'),
        ('jzczhz(-100% -100% -360)', 'jzczhz(-1 -0.26 -360 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('jzczhz'), Color(color2))


class TestJzCzhzSerialize(util.ColorAssertsPyTest):
    """Test JzCzhz serialization."""

    COLORS = [
        # Test color
        ('jzczhz(0.75 0.3 50 / 0.5)', {}, 'jzczhz(0.75 0.3 50 / 0.5)'),
        # Test alpha
        ('jzczhz(0.75 0.3 50)', {'alpha': True}, 'jzczhz(0.75 0.3 50 / 1)'),
        ('jzczhz(0.75 0.3 50 / 0.5)', {'alpha': False}, 'jzczhz(0.75 0.3 50)'),
        # Test None
        ('jzczhz(none 0.3 50)', {}, 'jzczhz(0 0.3 50)'),
        ('jzczhz(none 0.3 50)', {'none': True}, 'jzczhz(none 0.3 50)'),
        # Test Fit (not bound)
        ('jzczhz(0.75 0.6 50)', {}, 'jzczhz(0.75 0.6 50)'),
        ('jzczhz(0.75 0.6 50)', {'fit': False}, 'jzczhz(0.75 0.6 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestJzCzhzProperties(util.ColorAsserts, unittest.TestCase):
    """Test JzCzhz."""

    def test_names(self):
        """Test LCh-ish names."""

        c = Color('jzczhz(0.22 0.5 270 / 1)')
        self.assertEqual(c._space.names(), ('jz', 'cz', 'hz'))
        self.assertEqual(c._space.radial_name(), 'cz')
        self.assertEqual(c._space.hue_name(), 'hz')
        self.assertEqual(c._space.lightness_name(), 'jz')

    def test_jz(self):
        """Test `jz`."""

        c = Color('jzczhz(0.22 0.5 270 / 1)')
        self.assertEqual(c['jz'], 0.22)
        c['jz'] = 0.2
        self.assertEqual(c['jz'], 0.2)

    def test_cz(self):
        """Test `chroma`."""

        c = Color('jzczhz(0.22 0.5 270 / 1)')
        self.assertEqual(c['chroma'], 0.5)
        c['chroma'] = 0.1
        self.assertEqual(c['chroma'], 0.1)

    def test_hue(self):
        """Test `hue`."""

        c = Color('jzczhz(0.22 0.5 270 / 1)')
        self.assertEqual(c['hue'], 270)
        c['hue'] = 0.1
        self.assertEqual(c['hue'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('jzczhz(0.22 0.5 270 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)

    def test_hue_name(self):
        """Test `hue_name`."""

        c = Color('jzczhz(0.22 0.5 270 / 1)')
        self.assertEqual(c._space.hue_name(), 'hz')


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('jzczhz', [90, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('jzczhz(90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color(Color('jzczhz', [0.2, 0, 270]).convert('jzczhz').to_string(precision=6)).normalize()
        self.assertTrue(c.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chroma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to Jzazbz."""

        self.assertColorEqual(
            Color('jzczhz(90% -10 120 / 1)').convert('jzazbz'),
            Color('jzczhz(90% 10 300 / 1)').convert('jzazbz')
        )

    def test_to_negative_lightness(self):
        """Test conversion to negative lightness."""

        self.assertColorEqual(Color('jzazbz', [-0.5, 0, 0]).convert('jzczhz'), Color('jzczhz', [-0.5, 0, NaN]))

    def test_from_negative_lightness(self):
        """Test conversion to negative lightness."""

        self.assertColorEqual(Color('jzczhz', [-0.5, 0, 0]).convert('jzazbz'), Color('jzazbz', [-0.5, 0, 0]))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(
            Color('srgb', [0.000000001] * 3).convert('jzczhz').set('c', lambda x: x + 1e-8).is_achromatic(),
            True
        )
        self.assertEqual(Color('jzczhz', [NaN, 0.0, 270]).is_achromatic(), True)
        self.assertEqual(Color('jzczhz', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('jzczhz', [0, 0.5, 270]).is_achromatic(), False)
        self.assertEqual(Color('pink').convert('jzczhz').is_achromatic(), False)
        self.assertEqual(Color('jzczhz', [NaN, 0.5, 270]).is_achromatic(), False)
        self.assertEqual(Color('jzczhz', [0.2, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('jzczhz', [NaN, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('jzczhz', [-0.05, 0, 0]).is_achromatic(), True)
