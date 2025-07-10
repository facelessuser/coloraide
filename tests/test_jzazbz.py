"""Test Jzazbz library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestJzazbz(util.ColorAssertsPyTest):
    """Test Jzazbz."""

    COLORS = [
        ('red', 'jzazbz(0.13438 0.11789 0.11188)'),
        ('orange', 'jzazbz(0.16937 0.0312 0.12308)'),
        ('yellow', 'jzazbz(0.2096 -0.02864 0.13479)'),
        ('green', 'jzazbz(0.09203 -0.07454 0.07996)'),
        ('blue', 'jzazbz(0.09577 -0.04085 -0.18585)'),
        ('indigo', 'jzazbz(0.06146 0.03051 -0.09951)'),
        ('violet', 'jzazbz(0.16771 0.06427 -0.05514)'),
        ('white', 'jzazbz(0.22207 -0.00016 -0.00012)'),
        ('gray', 'jzazbz(0.11827 -0.00012 -0.00008)'),
        ('black', 'jzazbz(0 0 0)'),
        # Test color
        ('jzazbz(0.5 0.1 -0.1)', 'jzazbz(0.5 0.1 -0.1)'),
        ('jzazbz(0.5 0.1 -0.1 / 0.5)', 'jzazbz(0.5 0.1 -0.1 / 0.5)'),
        ('jzazbz(50% 50% -50% / 50%)', 'jzazbz(0.5 0.105 -0.105 / 0.5)'),
        ('jzazbz(none none none / none)', 'jzazbz(none none none / none)'),
        # Test percent ranges
        ('jzazbz(0% 0% 0%)', 'jzazbz(0 0 0)'),
        ('jzazbz(100% 100% 100%)', 'jzazbz(1 0.21 0.21)'),
        ('jzazbz(-100% -100% -100%)', 'jzazbz(-1 -0.21 -0.21)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('jzazbz'), Color(color2))


class TestJzazbzSerialize(util.ColorAssertsPyTest):
    """Test Jzazbz serialization."""

    COLORS = [
        # Test color
        ('jzazbz(0.75 0.1 -0.1 / 0.5)', {}, 'jzazbz(0.75 0.1 -0.1 / 0.5)'),
        # Test alpha
        ('jzazbz(0.75 0.1 -0.1)', {'alpha': True}, 'jzazbz(0.75 0.1 -0.1 / 1)'),
        ('jzazbz(0.75 0.1 -0.1 / 0.5)', {'alpha': False}, 'jzazbz(0.75 0.1 -0.1)'),
        # Test None
        ('jzazbz(none 0.1 -0.1)', {}, 'jzazbz(0 0.1 -0.1)'),
        ('jzazbz(none 0.1 -0.1)', {'none': True}, 'jzazbz(none 0.1 -0.1)'),
        # Test Fit (not bound)
        ('jzazbz(0.75 0.6 -0.1)', {}, 'jzazbz(0.75 0.6 -0.1)'),
        ('jzazbz(0.75 0.6 -0.1)', {'fit': False}, 'jzazbz(0.75 0.6 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestJzazbzProperties(util.ColorAsserts, unittest.TestCase):
    """Test Jzazbz."""

    def test_names(self):
        """Test Lab-ish names."""

        c = Color('jzazbz(1 0.2 -0.3 / 1)')
        self.assertEqual(c._space.lightness_name(), 'jz')

    def test_jz(self):
        """Test `lightness`."""

        c = Color('jzazbz(1 0.2 -0.3 / 1)')
        self.assertEqual(c['jz'], 1)
        c['jz'] = 0.2
        self.assertEqual(c['jz'], 0.2)

    def test_az(self):
        """Test `az`."""

        c = Color('jzazbz(1 0.2 -0.3 / 1)')
        self.assertEqual(c['az'], 0.2)
        c['az'] = 0.1
        self.assertEqual(c['az'], 0.1)

    def test_bz(self):
        """Test `bz`."""

        c = Color('jzazbz(1 0.2 -0.3 / 1)')
        self.assertEqual(c['bz'], -0.3)
        c['bz'] = 0.1
        self.assertEqual(c['bz'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('jzazbz(1 0.2 -0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('jzazbz', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('jzazbz', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('jzazbz', [0, 0.3, -0.4]).is_achromatic(), False)
        self.assertEqual(Color('jzazbz', [NaN, 0, -0.3]).is_achromatic(), False)
        self.assertEqual(Color('jzazbz', [NaN, 0, 0]).is_achromatic(), True)
        self.assertEqual(Color('jzazbz', [0.3, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('jzazbz', [NaN, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('jzazbz', [-0.05, 0, 0]).is_achromatic(), True)
