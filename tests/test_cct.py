"""Test CCT."""
import math
from coloraide.everything import ColorAll as Color
from coloraide import cmfs
from coloraide import cat
from . import util
import pytest
import unittest


class TestOhno2013Temp(util.ColorAssertsPyTest):
    """Test Ohno 2013."""

    @pytest.mark.parametrize('cct', list(range(1000, 100000, 100)))
    def test_cct(self, cct):
        """
        Test CCT methods.

        We test at a high resolution to make sure the spline implementation is working as good as without.
        """

        for duv in (-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03):
            cct2, duv2 = Color.blackbody(cct, duv, space=None).cct()
            assert math.isclose(cct2, cct, rel_tol=(0.00001 if cct < 86000 else 0.0001), abs_tol=0.000001)
            assert math.isclose(duv2, duv, rel_tol=0.000001, abs_tol=0.000001)


class TestRobertson1968(util.ColorAssertsPyTest):
    """Test Robertson 1968."""

    @pytest.mark.parametrize('cct', list(range(1667, 100000, 1000)))
    def test_cct(self, cct):
        """Test CCT methods."""

        for duv in (-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03):
            cct2, duv2 = Color.blackbody(cct, duv, space=None, method='robertson-1968').cct(method='robertson-1968')
            assert math.isclose(cct2, cct, rel_tol=0.00001, abs_tol=0.00001)
            assert math.isclose(duv2, duv, rel_tol=0.00001, abs_tol=0.00001)


class TestOhno2013Color(util.ColorAssertsPyTest):
    """Test Ohno 2013."""

    @pytest.mark.parametrize(
        'color',
        [
            'green',
            'yellow',
            'orange',
            'white',
            'gray',
            'pink',

        ]
    )
    def test_cct(self, color):
        """Test CCT methods."""

        cct, duv = Color(color).cct()
        c = Color.blackbody(cct, duv, space=None)
        cct2, duv2 = c.cct()
        assert math.isclose(cct, cct2, rel_tol=0.00001, abs_tol=0.00001)
        assert math.isclose(duv, duv2, rel_tol=0.00001, abs_tol=0.00001)


class TestRobertson1968Color(util.ColorAssertsPyTest):
    """Test Robertson 1968."""

    @pytest.mark.parametrize(
        'color',
        [
            'green',
            'yellow',
            'orange',
            'white',
            'gray',
            'pink',

        ]
    )
    def test_cct(self, color):
        """Test CCT methods."""

        cct, duv = Color(color).cct(method='robertson-1968')
        c = Color.blackbody(cct, duv, space=None, method='robertson-1968')
        cct2, duv2 = c.cct(method='robertson-1968')
        assert math.isclose(cct, cct2, rel_tol=0.00001, abs_tol=0.00001)
        assert math.isclose(duv, duv2, rel_tol=0.00001, abs_tol=0.00001)


class TestCCTSpecificCases(util.ColorAsserts, unittest.TestCase):
    """Test CCT specific cases."""

    def test_bad_algorithm(self):
        """Test bad algorithm inputs."""

        with self.assertRaises(ValueError):
            Color.blackbody(2000, method='bad')

        with self.assertRaises(ValueError):
            Color('blue').cct(method='bad')

    def test_outside_gamut(self):
        """Test temperature outside of gamut."""

        self.assertColorEqual(
            Color.blackbody(1500),
            Color('color(srgb-linear 1 0.14969 0)')
        )

    def test_robertson_1968_invert_slope(self):
        """Test colors on the side of the locus where the slope inverts from negative to positive."""

        self.assertEqual(
            Color('color(xyz-d65 1.4899 1 0.05398 / 1)').cct(method='robertson-1968'),
            [1500.0170599230767, 4.871531092560021e-07]
        )

    def test_output_space(self):
        """Test output space."""

        self.assertColorEqual(
            Color.blackbody(2000, out_space='display-p3'),
            Color('color(display-p3 0.93958 0.56696 0.22947)')
        )

    def test_normalization_space(self):
        """Test normalization space."""

        self.assertColorEqual(
            Color.blackbody(2000, space='display-p3'),
            Color('color(display-p3 1 0.6107 0.25811)')
        )

    def test_no_normalization_space(self):
        """Test normalization space."""

        self.assertColorEqual(
            Color.blackbody(2000, space=None),
            Color('color(xyz-d65 1.2743 1 0.14523)')
        )

    def test_ohno_alternate_cmfs(self):
        """Test alternate CMFs."""

        from coloraide.temperature.ohno_2013 import Ohno2013

        class Custom(Color):
            ...

        Custom.register(
            Ohno2013(cmfs.cie_1964_10deg, cat.WHITES['10deg']['D65']),
            overwrite=True
        )

        srgbl = Custom.blackbody(5000)
        self.assertColorEqual(srgbl, Color('color(srgb-linear 1 0.77908 0.61805)'))
        cct, duv = srgbl.cct()
        assert math.isclose(cct, 5000.005435878293, rel_tol=1e-11, abs_tol=1e-11)
        assert math.isclose(duv, 2.771032069214595e-08, rel_tol=1e-11, abs_tol=1e-11)

    def test_ohno_exact(self):
        """Test exact CMFs."""

        cct1, duv1 = Color('orange').cct()
        assert math.isclose(cct1, 2424.1146637385255, rel_tol=1e-11, abs_tol=1e-11)
        assert math.isclose(duv1, 0.008069417642630583, rel_tol=1e-11, abs_tol=1e-11)
        cct2, duv2 = Color('orange').cct(exact=True)
        assert math.isclose(cct2, 2424.1146637385255, rel_tol=1e-11, abs_tol=1e-11)
        assert math.isclose(duv2, 0.008069417642630583, rel_tol=1e-11, abs_tol=1e-11)
