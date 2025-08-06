"""Test Hellwig JMh."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
from coloraide.spaces.hellwig import cam_to_xyz, xyz_to_cam, HellwigJMh, HellwigHKJMh
from collections import namedtuple
import pytest

HellwigCoords = namedtuple("HellwigCoords", "J C h s Q M H")


class TestHellwigJMh(util.ColorAssertsPyTest):
    """Test Hellwig JMh."""

    COLORS = [
        ('red', 'color(--hellwig-jmh 46.026 47.347 27.393)'),
        ('orange', 'color(--hellwig-jmh 68.056 31.228 71.293)'),
        ('yellow', 'color(--hellwig-jmh 94.682 33.735 111.15)'),
        ('green', 'color(--hellwig-jmh 33.976 27.019 142.3)'),
        ('blue', 'color(--hellwig-jmh 25.066 63.023 282.75)'),
        ('indigo', 'color(--hellwig-jmh 16.046 32.429 310.9)'),
        ('violet', 'color(--hellwig-jmh 63.507 33.12 331.39)'),
        ('white', 'color(--hellwig-jmh 100 1.0387 209.53)'),
        ('gray', 'color(--hellwig-jmh 43.042 0.55653 209.54)'),
        ('black', 'color(--hellwig-jmh 0 0 0)'),
        # Test color
        ('color(--hellwig-jmh 50 30 270)', 'color(--hellwig-jmh 50 30 270)'),
        ('color(--hellwig-jmh 50 30 270 / 0.5)', 'color(--hellwig-jmh 50 30 270 / 0.5)'),
        ('color(--hellwig-jmh 50% 50% 100 / 50%)', 'color(--hellwig-jmh 50 35 100 / 0.5)'),
        ('color(--hellwig-jmh none none none / none)', 'color(--hellwig-jmh none none none / none)'),
        # Test percent ranges
        ('color(--hellwig-jmh 0% 0% 0)', 'color(--hellwig-jmh 0 0 0)'),
        ('color(--hellwig-jmh 100% 100% 100)', 'color(--hellwig-jmh 100 70 100 / 1)'),
        ('color(--hellwig-jmh -100% -100% 100)', 'color(--hellwig-jmh -100 -70 100 / 1)'),
        # Test miscellaneous cases
        ('color(--hellwig-jmh -10 none 270)', 'color(--hellwig-jmh -10 0 270)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hellwig-jmh'), Color(color2))


class TestHellwigJMhPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Hellwig JMh properties."""

    def test_names(self):
        """Test LCh-ish names."""

        c = Color('color(--hellwig-jmh 97.139 75.504 111.05)')
        self.assertEqual(c._space.names(), ('j', 'm', 'h'))
        self.assertEqual(c._space.lightness_name(), 'j')
        self.assertEqual(c._space.radial_name(), 'm')

    def test_h(self):
        """Test `h`."""

        c = Color('color(--hellwig-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['h'], 111.05)
        c['h'] = 270
        self.assertEqual(c['h'], 270)

    def test_m(self):
        """Test `m`."""

        m = Color('color(--hellwig-jmh 97.139 75.504 111.05)')
        self.assertEqual(m['m'], 75.504)
        m['m'] = 30
        self.assertEqual(m['m'], 30)

    def test_j(self):
        """Test `j`."""

        c = Color('color(--hellwig-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['j'], 97.139)
        c['j'] = 50
        self.assertEqual(c['j'], 50)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hellwig-jmh 97.139 75.504 111.05)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('hellwig-jmh', [30, 20, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--hellwig-jmh 30 20 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum chroma."""

        c = Color(Color('hellwig-jmh', [20, 0, 270]).to_string()).normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_negative_chroma(self):
        """Test negative chroma."""

        c = Color(Color('hellwig-jmh', [20, -5, 270]).to_string()).normalize()
        self.assertTrue(c.get('hue'), 270 + 180)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(
            Color('srgb', [0.000000001] * 3).convert('hellwig-jmh').set('m', lambda x: x + 1e-8).is_achromatic(),
            True
        )
        self.assertEqual(Color('hellwig-jmh', [NaN, 0.00001, 270]).is_achromatic(), True)
        self.assertEqual(Color('hellwig-jmh', [0, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('hellwig-jmh', [0, 50, 270]).is_achromatic(), False)
        self.assertEqual(Color('hellwig-jmh', [NaN, 50, 270]).is_achromatic(), False)
        self.assertEqual(Color('hellwig-jmh', [20, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('hellwig-jmh', [NaN, NaN, 270]).is_achromatic(), True)
        self.assertEqual(Color('hellwig-jmh', [20, -1.3, 90]).is_achromatic(), False)


class TestHellwigApperanceModel(util.ColorAsserts, unittest.TestCase):
    """Test Hellwig appearance model."""

    COORDS = HellwigCoords(
        46.02570140815224, 64.95847406394218, 27.3932565675869, 139.1190006974829, 34.03332581089115,
        47.34682277223029, 9.204194063758099
    )

    COORDS_HK = HellwigCoords(
        53.03748017532689, 64.95847406394218, 27.3932565675869, 139.1190006974829, 39.21812786705006,
        47.34682277223029, 9.204194063758099
    )

    def test_no_lightness(self):
        """Test conversion failure when no equivalent lightness."""

        with self.assertRaises(ValueError):
            cam_to_xyz(C=self.COORDS.C, h=self.COORDS.h, env=HellwigJMh.ENV)

    def test_no_chroma(self):
        """Test conversion failure when no equivalent chroma."""

        with self.assertRaises(ValueError):
            cam_to_xyz(J=self.COORDS.J, h=self.COORDS.h, env=HellwigJMh.ENV)

    def test_no_hue(self):
        """Test conversion failure when no equivalent hue."""

        with self.assertRaises(ValueError):
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, env=HellwigJMh.ENV)

    def test_no_environment(self):
        """Test no test no environment."""

        with self.assertRaises(ValueError):
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h)

    def test_lightness_convert(self):
        """Test convert lightness."""

        for a, b in zip(
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=HellwigJMh.ENV),
            cam_to_xyz(Q=self.COORDS.Q, C=self.COORDS.C, h=self.COORDS.h, env=HellwigJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=HellwigHKJMh.ENV),
            cam_to_xyz(Q=self.COORDS.Q, C=self.COORDS.C, h=self.COORDS.h, env=HellwigHKJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_chroma_convert(self):
        """Test convert chroma."""

        for a, b in zip(
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=HellwigJMh.ENV),
            cam_to_xyz(Q=self.COORDS.Q, s=self.COORDS.s, h=self.COORDS.h, env=HellwigJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

        for a, b in zip(
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=HellwigJMh.ENV),
            cam_to_xyz(Q=self.COORDS.Q, M=self.COORDS.M, h=self.COORDS.h, env=HellwigJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_Q_zero_high_colorfulness(self):
        """Test Q as zero with high colorfulness."""

        for a, b in zip(
            cam_to_xyz(Q=0, M=self.COORDS.M, h=self.COORDS.h, env=HellwigJMh.ENV),
            [-0.00561722983796, -0.00135510306102, -0.08167951639685]
        ):
            self.assertCompare(a, b, 14)

    def test_Q_zero_low_colorfulness(self):
        """Test Q as zero with zero colorfulness."""

        for a, b in zip(
            cam_to_xyz(Q=0, M=0, h=self.COORDS.h, env=HellwigJMh.ENV),
            [0, 0, 0]
        ):
            self.assertCompare(a, b, 14)

    def test_hue_convert(self):
        """Test convert hue."""

        for a, b in zip(
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, h=self.COORDS.h, env=HellwigJMh.ENV),
            cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, H=self.COORDS.H, env=HellwigJMh.ENV)
        ):
            self.assertCompare(a, b, 14)

    def test_hue_quadrature(self):
        """Test conversion to and from test_hue_quadrature."""

        xyz = cam_to_xyz(J=self.COORDS.J, C=self.COORDS.C, H=self.COORDS.H, env=HellwigJMh.ENV)
        coords = xyz_to_cam(xyz, HellwigJMh.ENV, True)
        self.assertCompare(self.COORDS.H, coords[-1], 13)

    def test_hue_quadrature_low_end(self):
        """Exercise when the hue quadrature is on the low end."""

        xyz = Color('pink').convert('xyz-d65')
        coords = HellwigCoords(*xyz_to_cam(xyz.coords(), HellwigJMh.ENV, True))
        self.assertCompare(386.08608, coords[-1])
        xyz2 = cam_to_xyz(J=coords.J, M=coords.M, H=coords.H, env=HellwigJMh.ENV)
        for a, b in zip(xyz, xyz2):
            self.assertCompare(a, b, 14)

    def test_hellwig_hk_saturation(self):
        """Hellwig with H-K effect cannot resolve with saturation."""

        with self.assertRaises(ValueError):
            cam_to_xyz(J=self.COORDS.J, s=self.COORDS.s, h=self.COORDS.h, env=HellwigHKJMh.ENV)
