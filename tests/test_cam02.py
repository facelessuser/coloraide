"""Test CAM02 JMh."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
from coloraide.spaces.cam02 import cam_to_xyz, xyz_to_cam, CAM02JMh
from collections import namedtuple
import pytest

CAM02Coords = namedtuple("CAM02Coords", "J C h s Q M H")


class TestCAM02JMh(util.ColorAssertsPyTest):
    """Test CAM02 JMh."""

    COLORS = [
        ('red', 'color(--cam02-jmh 46.931 80.436 32.157)'),
        ('orange', 'color(--cam02-jmh 68.929 48.62 72.359)'),
        ('yellow', 'color(--cam02-jmh 95.676 58.265 106.15)'),
        ('green', 'color(--cam02-jmh 34.257 49.872 136.73)'),
        ('blue', 'color(--cam02-jmh 21.07 65.435 257.91)'),
        ('indigo', 'color(--cam02-jmh 15.132 40.436 297.88)'),
        ('violet', 'color(--cam02-jmh 63.028 43.615 326.36)'),
        ('white', 'color(--cam02-jmh 100 2.2891 210.74)'),
        ('gray', 'color(--cam02-jmh 43.042 1.5013 210.74)'),
        ('black', 'color(--cam02-jmh 0 0 0)'),
        # Test color
        ('color(--cam02-jmh 50 30 270)', 'color(--cam02-jmh 50 30 270)'),
        ('color(--cam02-jmh 50 30 270 / 0.5)', 'color(--cam02-jmh 50 30 270 / 0.5)'),
        ('color(--cam02-jmh 50% 50% 100 / 50%)', 'color(--cam02-jmh 50 60 100 / 0.5)'),
        ('color(--cam02-jmh none none none / none)', 'color(--cam02-jmh none none none / none)'),
        # Test percent ranges
        ('color(--cam02-jmh 0% 0% 0)', 'color(--cam02-jmh 0 0 0)'),
        ('color(--cam02-jmh 100% 100% 100)', 'color(--cam02-jmh 100 120 100 / 1)'),
        ('color(--cam02-jmh -100% -100% 100)', 'color(--cam02-jmh -100 -120 100 / 1)'),
        # Test miscellaneous cases
        ('color(--cam02-jmh -10 none 270)', 'color(--cam02-jmh -10 0 270)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cam02-jmh'), Color(color2))


class TestCAM02JMhPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM02 JMh properties."""

    def test_names(self):
        """Test LCh-ish names."""

        c = Color('color(--cam02-jmh 97.139 75.504 111.05)')
        self.assertEqual(c._space.names(), ('j', 'm', 'h'))
        self.assertEqual(c._space.radial_name(), 'm')
        self.assertEqual(c._space.lightness_name(), 'j')

    def test_h(self):
        """Test `h`."""

        c = Color('color(--cam02-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['h'], 111.05)
        c['h'] = 270
        self.assertEqual(c['h'], 270)

    def test_m(self):
        """Test `m`."""

        m = Color('color(--cam02-jmh 97.139 75.504 111.05)')
        self.assertEqual(m['m'], 75.504)
        m['m'] = 30
        self.assertEqual(m['m'], 30)

    def test_j(self):
        """Test `j`."""

        c = Color('color(--cam02-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['j'], 97.139)
        c['j'] = 50
        self.assertEqual(c['j'], 50)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cam02-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('cam02-jmh', [30, 20, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--cam02-jmh 30 20 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum chroma."""

        c = Color(Color('cam02-jmh', [20, 0, 270]).to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_negative_chroma(self):
        """Test negative chroma."""

        c = Color(Color('cam02-jmh', [20, -5, 270]).to_string()).normalize()
        self.assertTrue(c.get('hue'), 270 + 180)


class TestSpecialCases(util.ColorAsserts, unittest.TestCase):
    """Test special cases."""

    def test_zero_lightness_high_chroma(self):
        """Test cases of zero lightness and high chroma."""

        c = Color('color(--cam02-jmh 0 20 30)')
        c2 = c.convert('srgb')
        self.assertEqual(c2.in_gamut(tolerance=0), False)
        self.assertColorEqual(c2, Color('rgb(0.09155 0.03446 -0.94032)'))


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(
            Color('srgb', [0.000000001] * 3).convert('cam02-jmh').set('m', lambda x: x + 1e-8).is_achromatic(),
            True
        )
        self.assertEqual(Color('cam02-jmh', [NaN, 0.00001, 270]).is_achromatic(), True)
        self.assertEqual(Color('cam02-jmh', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('cam02-jmh', [0, 50, 270]).is_achromatic(), False)
        self.assertEqual(Color('cam02-jmh', [NaN, 50, 270]).is_achromatic(), False)
        self.assertEqual(Color('cam02-jmh', [20, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('cam02-jmh', [NaN, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('cam02-jmh', [20, -1.3, 90]).is_achromatic(), False)


class TestCAM02ApperanceModel(util.ColorAsserts, unittest.TestCase):
    """Test CAM02 appearance model."""

    COORDS = CAM02Coords(
        46.93086365686991, 111.26496487989309, 32.15681099742935, 97.42727846269904,
        84.74027273883304, 80.43609894994033, 15.381850282413149
    )

    def test_no_lightness(self):
        """Test conversion failure when no equivalent lightness."""

        with self.assertRaises(ValueError):
            cam_to_xyz(C=self.COORDS.C, h=self.COORDS.h, env=CAM02JMh.ENV)

    def test_no_chroma(self):
        """Test conversion failure when no equivalent chroma."""

        with self.assertRaises(ValueError):
            cam_to_xyz(J=self.COORDS.J, h=self.COORDS.h, env=CAM02JMh.ENV)

    def test_no_hue(self):
        """Test conversion failure when no equivalent hue."""

        with self.assertRaises(ValueError):
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, env=CAM02JMh.ENV)

    def test_no_environment(self):
        """Test no test no environment."""

        with self.assertRaises(ValueError):
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h)

    def test_lightness_convert(self):
        """Test convert lightness."""

        for a, b in zip(
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM02JMh.ENV),
            cam_to_xyz(Q=self.COORDS.Q, C=self.COORDS.C, h=self.COORDS.h, env=CAM02JMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_chroma_convert(self):
        """Test convert chroma."""

        for a, b in zip(
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM02JMh.ENV),
            cam_to_xyz(Q=self.COORDS.Q, s=self.COORDS.s, h=self.COORDS.h, env=CAM02JMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM02JMh.ENV),
            cam_to_xyz(Q=self.COORDS.Q, M=self.COORDS.M, h=self.COORDS.h, env=CAM02JMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_Q_zero_high_colorfulness(self):
        """Test Q as zero with high colorfulness."""

        for a, b in zip(
            cam_to_xyz(Q=0, M=self.COORDS.M, h=self.COORDS.h, env=CAM02JMh.ENV),
            [-3.960080148e-05, -6.36245037e-06, -0.00027447009634]
        ):
            self.assertCompare(a, b, 14)

    def test_Q_zero_low_colorfulness(self):
        """Test Q as zero with zero colorfulness."""

        for a, b in zip(
            cam_to_xyz(Q=0, M=0, h=self.COORDS.h, env=CAM02JMh.ENV),
            [0, 0, 0]
        ):
            self.assertCompare(a, b, 14)

    def test_hue_convert(self):
        """Test convert hue."""

        for a, b in zip(
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=CAM02JMh.ENV),
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, H=self.COORDS.H, env=CAM02JMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_hue_quadrature(self):
        """Test conversion to and from test_hue_quadrature."""

        xyz = cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, H=self.COORDS.H, env=CAM02JMh.ENV)
        coords = xyz_to_cam(xyz, CAM02JMh.ENV, True)
        self.assertCompare(self.COORDS.H, coords[-1], 13)

    def test_hue_quadrature_low_end(self):
        """Exercise when the hue quadrature is on the low end."""

        xyz = Color('pink').convert('xyz-d65')
        coords = CAM02Coords(*xyz_to_cam(xyz.coords(), CAM02JMh.ENV, True))
        self.assertCompare(387.1356, coords[-1])
        xyz2 = cam_to_xyz(J=coords.J, M=coords.M, H=coords.H, env=CAM02JMh.ENV)
        for a, b in zip(xyz, xyz2):
            self.assertCompare(a, b, 14)
