"""Test CCT."""
import math
from coloraide.everything import ColorAll as Color
from coloraide import cmfs
from coloraide import temperature
from coloraide import cat
from . import util
import pytest
import unittest


class TestOhno2013Temp(util.ColorAssertsPyTest):
    """Test Ohno 2013."""

    @pytest.mark.parametrize('cct', list(range(1000, 100000, 100)))
    def test_cct(self, cct):
        """Test CCT methods."""

        for duv in (-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03):
            cct2, duv2 = Color.blackbody(cct, duv, space=None).cct()
            assert math.isclose(cct2, cct, rel_tol=(0.00001 if cct < 96000 else 0.0001), abs_tol=0.000001)
            assert math.isclose(duv2, duv, rel_tol=0.000001, abs_tol=0.000001)


class TestRobertson1968(util.ColorAssertsPyTest):
    """Test Ohno 2013."""

    @pytest.mark.parametrize('cct', list(range(1000, 100000, 100)))
    def test_cct(self, cct):
        """Test CCT methods."""

        for duv in (-0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03):
            cct2, duv2 = Color.blackbody(cct, duv, space=None, method='robertson-1968').cct(method='robertson-1968')
            assert math.isclose(cct2, cct, rel_tol=0.0001, abs_tol=0.00001)
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
        c = Color.blackbody(cct, duv)
        cct2, duv2 = c.cct()
        assert math.isclose(cct, cct2, abs_tol=0.05)
        assert math.isclose(duv, duv2, abs_tol=0.05)


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
        c = Color.blackbody(cct, duv, method='robertson-1968')
        cct2, duv2 = c.cct(method='robertson-1968')
        assert math.isclose(cct, cct2, abs_tol=0.05)
        assert math.isclose(duv, duv2, abs_tol=0.05)


class TestCCTSpecificCases(util.ColorAsserts, unittest.TestCase):
    """Test CCT specific cases."""

    def test_bad_algorithm(self):
        """Test bad algorithm inputs."""

        with self.assertRaises(ValueError):
            Color.blackbody(2000, method='bad')

        with self.assertRaises(ValueError):
            Color('blue').cct(method='bad')

    def test_output_space(self):
        """Test output space."""

        self.assertColorEqual(
            Color.blackbody(2000, out_space='display-p3'),
            Color('color(display-p3 0.93958 0.56696 0.22948)')
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
            Color('color(xyz-d65 1.2743 1 0.14524)')
        )

    def test_ohno_alternate_cmfs(self):
        """Test alternate CMFs."""

        bbody = temperature.BlackBodyCurve(cmfs=cmfs.cie_1964_10deg, white=cat.WHITES['10deg']['D65'])
        srgbl = Color.blackbody(5000, blackbody=bbody)
        self.assertColorEqual(srgbl, Color('color(srgb-linear 1 0.77909 0.61807)'))
        self.assertEqual(srgbl.cct(blackbody=bbody), [5000.005435889316, 2.770957661628331e-08])

    def test_ohno_exact(self):
        """Test alternate CMFs."""

        cct1 = Color('orange').cct()
        self.assertEqual(cct1, [2424.0755046224285, 0.008069417819174918])
        cct2 = Color('orange').cct(exact=True)
        self.assertEqual(cct2, [2424.0755046224285, 0.008069417819174918])
