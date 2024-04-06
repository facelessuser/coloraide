"""Test ZCAM JMh."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
from coloraide.spaces.zcam_jmh import zcam_to_xyz_d65, xyz_d65_to_zcam, ZCAMJMh
from collections import namedtuple
import pytest

ZCAMCoords = namedtuple("ZCAMCoords", "Jz Cz hz Qz Mz Sz Vz Kz Wz Hz")


class TestZCAMJMh(util.ColorAssertsPyTest):
    """Test ZCAM JMh."""

    COLORS = [
        ('red', 'color(--zcam-jmh 51.197 43.776 42.477)'),
        ('orange', 'color(--zcam-jmh 71.271 32.313 75.038)'),
        ('yellow', 'color(--zcam-jmh 92.838 33.644 101.8)'),
        ('green', 'color(--zcam-jmh 38.754 31.201 133.24)'),
        ('blue', 'color(--zcam-jmh 43.495 55.652 258.81)'),
        ('indigo', 'color(--zcam-jmh 23.243 34.446 287.19)'),
        ('violet', 'color(--zcam-jmh 72.267 30.713 319.27)'),
        ('white', 'color(--zcam-jmh 100 0.35188 216.08)'),
        ('gray', 'color(--zcam-jmh 49.965 0.2662 216.08)'),
        ('black', 'color(--zcam-jmh 0 0 0)'),
        # Test color
        ('color(--zcam-jmh 50 30 270)', 'color(--zcam-jmh 50 30 270)'),
        ('color(--zcam-jmh 50 30 270 / 0.5)', 'color(--zcam-jmh 50 30 270 / 0.5)'),
        ('color(--zcam-jmh 50% 50% 100 / 50%)', 'color(--zcam-jmh 50 30 100 / 0.5)'),
        ('color(--zcam-jmh none none none / none)', 'color(--zcam-jmh none none none / none)'),
        # Test percent ranges
        ('color(--zcam-jmh 0% 0% 0)', 'color(--zcam-jmh 0 0 0)'),
        ('color(--zcam-jmh 100% 100% 100)', 'color(--zcam-jmh 100 60 100)'),
        ('color(--zcam-jmh -100% -100% 100)', 'color(--zcam-jmh -100 -60 100)'),
        # Test miscellaneous cases
        ('color(--zcam-jmh -10 none 270)', 'color(--zcam-jmh -10 0 270)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('zcam-jmh'), Color(color2))


class TestZCAMJMhPoperties(util.ColorAsserts, unittest.TestCase):
    """Test CAM16 JMh properties."""

    def test_names(self):
        """Test LCh-ish names."""

        c = Color('color(--zcam-jmh 97.139 75.504 111.05)')
        self.assertEqual(c._space.names(), ('jz', 'mz', 'hz'))
        self.assertEqual(c._space.radial_name(), 'mz')
        self.assertEqual(c._space.hue_name(), 'hz')

    def test_hz(self):
        """Test `hz`."""

        c = Color('color(--zcam-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['hz'], 111.05)
        c['h'] = 270
        self.assertEqual(c['hz'], 270)

    def test_mz(self):
        """Test `mz`."""

        m = Color('color(--zcam-jmh 97.139 75.504 111.05)')
        self.assertEqual(m['mz'], 75.504)
        m['m'] = 30
        self.assertEqual(m['mz'], 30)

    def test_jz(self):
        """Test `jz`."""

        c = Color('color(--zcam-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['jz'], 97.139)
        c['j'] = 50
        self.assertEqual(c['jz'], 50)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--zcam-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('zcam-jmh', [30, 20, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--zcam-jmh 30 20 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum chroma."""

        c = Color(Color('zcam-jmh', [20, 0, 270]).convert('zcam-jmh').to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_negative_chroma(self):
        """Test negative chroma."""

        c = Color(Color('zcam-jmh', [20, -5, 270]).convert('zcam-jmh').to_string()).normalize()
        self.assertTrue(c.get('hue'), 270 + 180)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(
            Color('srgb', [0.000000001] * 3).convert('cam16-jmh').set('m', lambda x: x + 1e-8).is_achromatic(),
            True
        )
        self.assertEqual(Color('zcam-jmh', [NaN, 0.00001, 270]).is_achromatic(), True)
        self.assertEqual(Color('zcam-jmh', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('zcam-jmh', [0, 50, 270]).is_achromatic(), True)
        self.assertEqual(Color('zcam-jmh', [NaN, 50, 270]).is_achromatic(), True)
        self.assertEqual(Color('zcam-jmh', [20, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('zcam-jmh', [NaN, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('zcam-jmh', [20, -1.3, 90]).is_achromatic(), False)


class TestZCAMApperanceModel(util.ColorAsserts, unittest.TestCase):
    """Test ZCAM appearance model."""

    COORDS = ZCAMCoords(
        43.49495951236768, 37.06625840802933, 258.81201346495345, 65.3037302338701, 55.651619566827854,
        42.37206156525153, 69.86903277997048, 9.197104532689465, 32.422436320330604, 311.82891934461054
    )

    def test_no_lightness(self):
        """Test conversion failure when no equivalent lightness."""

        with self.assertRaises(ValueError):
            zcam_to_xyz_d65(Cz=self.COORDS.Cz, hz=self.COORDS.hz, env=ZCAMJMh.ENV)

    def test_no_chroma(self):
        """Test conversion failure when no equivalent chroma."""

        with self.assertRaises(ValueError):
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, hz=self.COORDS.hz, env=ZCAMJMh.ENV)

    def test_no_hue(self):
        """Test conversion failure when no equivalent hue."""

        with self.assertRaises(ValueError):
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, env=ZCAMJMh.ENV)

    def test_no_environment(self):
        """Test no test no environment."""

        with self.assertRaises(ValueError):
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, hz=self.COORDS.hz)

    def test_lightness_convert(self):
        """Test convert lightness."""

        for a, b in zip(
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, hz=self.COORDS.hz, env=ZCAMJMh.ENV),
            zcam_to_xyz_d65(Qz=self.COORDS.Qz, Cz=self.COORDS.Cz, hz=self.COORDS.hz, env=ZCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_chroma_convert(self):
        """Test convert chroma."""

        for a, b in zip(
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, hz=self.COORDS.hz, env=ZCAMJMh.ENV),
            zcam_to_xyz_d65(Qz=self.COORDS.Qz, Sz=self.COORDS.Sz, hz=self.COORDS.hz, env=ZCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, hz=self.COORDS.hz, env=ZCAMJMh.ENV),
            zcam_to_xyz_d65(Qz=self.COORDS.Qz, Mz=self.COORDS.Mz, hz=self.COORDS.hz, env=ZCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, hz=self.COORDS.hz, env=ZCAMJMh.ENV),
            zcam_to_xyz_d65(Qz=self.COORDS.Qz, Vz=self.COORDS.Vz, hz=self.COORDS.hz, env=ZCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, hz=self.COORDS.hz, env=ZCAMJMh.ENV),
            zcam_to_xyz_d65(Qz=self.COORDS.Qz, Kz=self.COORDS.Kz, hz=self.COORDS.hz, env=ZCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, hz=self.COORDS.hz, env=ZCAMJMh.ENV),
            zcam_to_xyz_d65(Qz=self.COORDS.Qz, Wz=self.COORDS.Wz, hz=self.COORDS.hz, env=ZCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_hue_convert(self):
        """Test convert hue."""

        for a, b in zip(
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, hz=self.COORDS.hz, env=ZCAMJMh.ENV),
            zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, Hz=self.COORDS.Hz, env=ZCAMJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_hue_quadrature(self):
        """Test conversion to and from test_hue_quadrature."""

        xyz = zcam_to_xyz_d65(Jz=self.COORDS.Jz, Cz=self.COORDS.Cz, Hz=self.COORDS.Hz, env=ZCAMJMh.ENV)
        coords = xyz_d65_to_zcam(xyz, ZCAMJMh.ENV, True)
        self.assertCompare(self.COORDS.Hz, coords[-1], 12)

    def test_hue_quadrature_low_end(self):
        """Exercise when the hue quadrature is on the low end."""

        xyz = Color('pink').convert('xyz-d65')
        coords = ZCAMCoords(*xyz_d65_to_zcam(xyz.coords(), ZCAMJMh.ENV, True))
        self.assertCompare(387.07995, coords[-1])
        xyz2 = zcam_to_xyz_d65(Jz=coords.Jz, Mz=coords.Mz, Hz=coords.Hz, env=ZCAMJMh.ENV)
        for a, b in zip(xyz, xyz2):
            self.assertCompare(a, b, 12)
