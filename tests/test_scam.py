"""Test sCAM JMh."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
from coloraide.spaces.scam import scam_to_xyz, xyz_to_scam, sCAMJMh
from typing import NamedTuple
import pytest


class sCAMCoords(NamedTuple):
    """sCAM coordinates."""

    J: float
    C: float
    h: float
    Q: float
    M: float
    D: float
    V: float
    W: float
    K: float
    H: float


class TestSCAMJMh(util.ColorAssertsPyTest):
    """Test sCAM JMh."""

    COLORS = [
        ('red', 'color(--scam-jmh 54.635 15.852 29.937)'),
        ('orange', 'color(--scam-jmh 74.208 11.547 67.919)'),
        ('yellow', 'color(--scam-jmh 96.243 12.049 101.84)'),
        ('green', 'color(--scam-jmh 43.205 11.159 134.25)'),
        ('blue', 'color(--scam-jmh 31.197 19.885 250.27)'),
        ('indigo', 'color(--scam-jmh 23.328 12.625 290.85)'),
        ('violet', 'color(--scam-jmh 69.669 11.021 325.3)'),
        ('white', 'color(--scam-jmh 100 0 0)'),
        ('gray', 'color(--scam-jmh 51.651 0 0)'),
        ('black', 'color(--scam-jmh 0 0 0)'),
        # Test color
        ('color(--scam-jmh 50 30 270)', 'color(--scam-jmh 50 30 270)'),
        ('color(--scam-jmh 50 30 270 / 0.5)', 'color(--scam-jmh 50 30 270 / 0.5)'),
        ('color(--scam-jmh 50% 50% 100 / 50%)', 'color(--scam-jmh 50 12.5 100 / 0.5)'),
        ('color(--scam-jmh none none none / none)', 'color(--scam-jmh none none none / none)'),
        # Test percent ranges
        ('color(--scam-jmh 0% 0% 0)', 'color(--scam-jmh 0 0 0)'),
        ('color(--scam-jmh 100% 100% 100)', 'color(--scam-jmh 100 25 100)'),
        ('color(--scam-jmh -100% -100% 100)', 'color(--scam-jmh -100 -25 100)'),
        # Test miscellaneous cases
        ('color(--scam-jmh -10 none 270)', 'color(--scam-jmh -10 0 270)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('scam-jmh'), Color(color2))


class TestSCAMJMhPoperties(util.ColorAsserts, unittest.TestCase):
    """Test sCAM JMh properties."""

    def test_names(self):
        """Test LCh-ish names."""

        c = Color('color(--scam-jmh 97.139 75.504 111.05)')
        self.assertEqual(c._space.names(), ('j', 'm', 'h'))
        self.assertEqual(c._space.radial_name(), 'm')
        self.assertEqual(c._space.hue_name(), 'h')
        self.assertEqual(c._space.lightness_name(), 'j')

    def test_h(self):
        """Test `h`."""

        c = Color('color(--scam-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['h'], 111.05)
        c['h'] = 270
        self.assertEqual(c['h'], 270)

    def test_m(self):
        """Test `m`."""

        m = Color('color(--scam-jmh 97.139 75.504 111.05)')
        self.assertEqual(m['m'], 75.504)
        m['m'] = 30
        self.assertEqual(m['m'], 30)

    def test_j(self):
        """Test `j`."""

        c = Color('color(--scam-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['j'], 97.139)
        c['j'] = 50
        self.assertEqual(c['j'], 50)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--scam-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('scam-jmh', [30, 20, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--scam-jmh 30 20 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum chroma."""

        c = Color(Color('scam-jmh', [20, 0, 270]).convert('scam-jmh').to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_negative_chroma(self):
        """Test negative chroma."""

        c = Color(Color('scam-jmh', [20, -5, 270]).convert('scam-jmh').to_string()).normalize()
        self.assertTrue(c.get('hue'), 270 + 180)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(
            Color('srgb', [0.000000001] * 3).convert('cam16-jmh').set('m', lambda x: x + 1e-8).is_achromatic(),
            True
        )
        self.assertEqual(Color('scam-jmh', [NaN, 0.00001, 270]).is_achromatic(), True)
        self.assertEqual(Color('scam-jmh', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('scam-jmh', [0, 50, 270]).is_achromatic(), True)
        self.assertEqual(Color('scam-jmh', [NaN, 50, 270]).is_achromatic(), True)
        self.assertEqual(Color('scam-jmh', [20, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('scam-jmh', [NaN, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('scam-jmh', [20, -1.3, 90]).is_achromatic(), False)


class TestSCAMApperanceModel(util.ColorAsserts, unittest.TestCase):
    """Test sCAM appearance model."""

    COORDS = sCAMCoords(
        54.635215259160006, 55.6689281833851, 29.93650277259878, 184.71839737681037, 15.852250348849166,
        108.89322562877724, 110.82461568476299, -8.893225628777245, -10.824615684762989, 19.613811267787895
    )

    def test_no_lightness(self):
        """Test conversion failure when no equivalent lightness."""

        with self.assertRaises(ValueError):
            scam_to_xyz(C=self.COORDS.C, h=self.COORDS.h, env=sCAMJMh.ENV)

    def test_no_chroma(self):
        """Test conversion failure when no equivalent chroma."""

        with self.assertRaises(ValueError):
            scam_to_xyz(J=self.COORDS.J, h=self.COORDS.h, env=sCAMJMh.ENV)

    def test_no_hue(self):
        """Test conversion failure when no equivalent hue."""

        with self.assertRaises(ValueError):
            scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, env=sCAMJMh.ENV)

    def test_no_environment(self):
        """Test no test no environment."""

        with self.assertRaises(ValueError):
            scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h)

    def test_lightness_convert(self):
        """Test convert lightness."""

        for a, b in zip(
            scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=sCAMJMh.ENV),
            scam_to_xyz(Q=self.COORDS.Q, C=self.COORDS.C, h=self.COORDS.h, env=sCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_chroma_convert(self):
        """Test convert chroma."""

        for a, b in zip(
            scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=sCAMJMh.ENV),
            scam_to_xyz(Q=self.COORDS.Q, M=self.COORDS.M, h=self.COORDS.h, env=sCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=sCAMJMh.ENV),
            scam_to_xyz(Q=self.COORDS.Q, V=self.COORDS.V, h=self.COORDS.h, env=sCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=sCAMJMh.ENV),
            scam_to_xyz(Q=self.COORDS.Q, K=self.COORDS.K, h=self.COORDS.h, env=sCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=sCAMJMh.ENV),
            scam_to_xyz(Q=self.COORDS.Q, W=self.COORDS.W, h=self.COORDS.h, env=sCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_hue_convert(self):
        """Test convert hue."""

        for a, b in zip(
            scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=sCAMJMh.ENV),
            scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, H=self.COORDS.H, env=sCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_Qz_zero_high_colorfulness(self):
        """Test Qz as zero with high colorfulness."""

        for a, b in zip(
            scam_to_xyz(Q=0, M=self.COORDS.M, h=self.COORDS.h, env=sCAMJMh.ENV),
            [0.0, 0.0, 0.0]
        ):
            self.assertCompare(a, b, 14)

    def test_Qz_zero_low_colorfulness(self):
        """Test Qz as zero with zero colorfulness."""

        for a, b in zip(
            scam_to_xyz(Q=0, M=0, h=self.COORDS.h, env=sCAMJMh.ENV),
            [0, 0, 0]
        ):
            self.assertCompare(a, b, 14)

    def test_hue_quadrature(self):
        """Test conversion to and from test_hue_quadrature."""

        xyz = scam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, H=self.COORDS.H, env=sCAMJMh.ENV)
        coords = xyz_to_scam(xyz, sCAMJMh.ENV, True)
        self.assertCompare(self.COORDS.H, coords[-1], 12)

    def test_hue_quadrature_low_end(self):
        """Exercise when the hue quadrature is on the low end."""

        xyz = Color('pink').convert('xyz-d65')
        coords = sCAMCoords(*xyz_to_scam(xyz.coords(), sCAMJMh.ENV, True))
        self.assertCompare(393.28263, coords[-1])
        xyz2 = scam_to_xyz(J=coords.J, M=coords.M, H=coords.H, env=sCAMJMh.ENV)
        for a, b in zip(xyz, xyz2):
            self.assertCompare(a, b, 12)
