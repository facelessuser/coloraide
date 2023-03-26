"""Test CAM16 JMh."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
from coloraide.spaces.cam16_jmh import cam16_to_xyz_d65, CAM16JMh
from collections import namedtuple
import pytest

CAM16Coords = namedtuple("CAM16Coords", "J C h s Q M H")


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
        ('white', 'color(--cam16-jmh 100 2.2369 209.53)'),
        ('gray', 'color(--cam16-jmh 43.042 1.467 209.54)'),
        ('black', 'color(--cam16-jmh 0 0 209.54)'),
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


class TestCAM16JMhPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM16 JMh properties."""

    def test_names(self):
        """Test LCh-ish names."""

        self.assertEqual(Color('color(--cam16-jmh 97.139 75.504 111.05)')._space.names(), ('j', 'm', 'h'))

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

        c = Color(Color('white').convert('cam16-jmh').to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

        c = Color(Color('gray').convert('cam16-jmh').to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

        c = Color(Color('darkgray').convert('cam16-jmh').to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to CAM16 JMh with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('cam16-jmh')
                self.assertTrue(color2.is_nan('hue'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('#222222').convert('cam16-jmh').is_achromatic(), True)
        self.assertEqual(
            Color('srgb', [0.000000001] * 3).convert('cam16-jmh').set('m', lambda x: x + 1e-8).is_achromatic(),
            True
        )
        self.assertEqual(Color('cam16-jmh', [NaN, 0.00001, 270]).is_achromatic(), True)
        self.assertEqual(Color('cam16-jmh', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('cam16-jmh', [0, 50, 270]).is_achromatic(), True)
        self.assertEqual(Color('cam16-jmh', [NaN, 50, 270]).is_achromatic(), True)
        self.assertEqual(Color('cam16-jmh', [20, NaN, 270]).is_achromatic(), False)
        self.assertEqual(Color('cam16-jmh', [NaN, NaN, 270]).is_achromatic(), True)


class TestCAM16ApperanceModel(util.ColorAsserts, unittest.TestCase):
    """Test CAM16 appearance model."""

    COORDS = CAM16Coords(
        45.33435136131785, 45.26195932727762, 258.92464993097565,
        62.67686398624793, 83.29355481993107, 32.720950777696196, 310.5279473979526
    )

    def test_no_lightness(self):
        """Test conversion failure when no equivalent lightness."""

        with self.assertRaises(ValueError):
            cam16_to_xyz_d65(C=self.COORDS.C, h=self.COORDS.h, env=CAM16JMh.ENV)

    def test_no_chroma(self):
        """Test conversion failure when no equivalent chroma."""

        with self.assertRaises(ValueError):
            cam16_to_xyz_d65(J=self.COORDS.J, h=self.COORDS.h, env=CAM16JMh.ENV)

    def test_no_hue(self):
        """Test conversion failure when no equivalent hue."""

        with self.assertRaises(ValueError):
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, env=CAM16JMh.ENV)

    def test_no_environment(self):
        """Test no test no environment."""

        with self.assertRaises(ValueError):
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h)

    def test_lightness_convert(self):
        """Test convert lightness."""

        for a, b in zip(
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM16JMh.ENV),
            cam16_to_xyz_d65(Q=self.COORDS.Q, C=self.COORDS.C, h=self.COORDS.h, env=CAM16JMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_chroma_convert(self):
        """Test convert chroma."""

        for a, b in zip(
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM16JMh.ENV),
            cam16_to_xyz_d65(Q=self.COORDS.Q, s=self.COORDS.s, h=self.COORDS.h, env=CAM16JMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM16JMh.ENV),
            cam16_to_xyz_d65(Q=self.COORDS.Q, M=self.COORDS.M, h=self.COORDS.h, env=CAM16JMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_hue_convert(self):
        """Test convert hue."""

        for a, b in zip(
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM16JMh.ENV),
            cam16_to_xyz_d65(J=self.COORDS.J, C=self.COORDS.C, H=self.COORDS.H, env=CAM16JMh.ENV)
        ):
            self.assertCompare(a, b, 14)
