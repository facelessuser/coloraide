"""Test Jzazbz library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestJzazbz(util.ColorAssertsPyTest):
    """Test Jzazbz."""

    COLORS = [
        ('red', 'color(--jzazbz 0.13438 0.11789 0.11188)'),
        ('orange', 'color(--jzazbz 0.16937 0.0312 0.12308)'),
        ('yellow', 'color(--jzazbz 0.2096 -0.02864 0.13479)'),
        ('green', 'color(--jzazbz 0.09203 -0.07454 0.07996)'),
        ('blue', 'color(--jzazbz 0.09577 -0.04085 -0.18585)'),
        ('indigo', 'color(--jzazbz 0.06146 0.03051 -0.09951)'),
        ('violet', 'color(--jzazbz 0.16771 0.06427 -0.05514)'),
        ('white', 'color(--jzazbz 0.22207 -0.00016 -0.00012)'),
        ('gray', 'color(--jzazbz 0.11827 -0.00012 -0.00008)'),
        ('black', 'color(--jzazbz 0 0 0)'),
        # Test color
        ('color(--jzazbz 0.5 0.1 -0.1)', 'color(--jzazbz 0.5 0.1 -0.1)'),
        ('color(--jzazbz 0.5 0.1 -0.1 / 0.5)', 'color(--jzazbz 0.5 0.1 -0.1 / 0.5)'),
        ('color(--jzazbz 50% 50% -50% / 50%)', 'color(--jzazbz 0.5 0.25 -0.25 / 0.5)'),
        ('color(--jzazbz none none none / none)', 'color(--jzazbz none none none / none)'),
        # Test percent ranges
        ('color(--jzazbz 0% 0% 0%)', 'color(--jzazbz 0 0 0)'),
        ('color(--jzazbz 100% 100% 100%)', 'color(--jzazbz 1 0.5 0.5)'),
        ('color(--jzazbz -100% -100% -100%)', 'color(--jzazbz -1 -0.5 -0.5)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('jzazbz'), Color(color2))


class TestJzazbzSerialize(util.ColorAssertsPyTest):
    """Test Jzazbz serialization."""

    COLORS = [
        # Test color
        ('color(--jzazbz 0.75 0.1 -0.1 / 0.5)', {}, 'color(--jzazbz 0.75 0.1 -0.1 / 0.5)'),
        # Test alpha
        ('color(--jzazbz 0.75 0.1 -0.1)', {'alpha': True}, 'color(--jzazbz 0.75 0.1 -0.1 / 1)'),
        ('color(--jzazbz 0.75 0.1 -0.1 / 0.5)', {'alpha': False}, 'color(--jzazbz 0.75 0.1 -0.1)'),
        # Test None
        ('color(--jzazbz none 0.1 -0.1)', {}, 'color(--jzazbz 0 0.1 -0.1)'),
        ('color(--jzazbz none 0.1 -0.1)', {'none': True}, 'color(--jzazbz none 0.1 -0.1)'),
        # Test Fit (not bound)
        ('color(--jzazbz 0.75 0.6 -0.1)', {}, 'color(--jzazbz 0.75 0.6 -0.1)'),
        ('color(--jzazbz 0.75 0.6 -0.1)', {'fit': False}, 'color(--jzazbz 0.75 0.6 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestJzazbzProperties(util.ColorAsserts, unittest.TestCase):
    """Test Jzazbz."""

    def test_jz(self):
        """Test `lightness`."""

        c = Color('color(--jzazbz 1 0.2 -0.3 / 1)')
        self.assertEqual(c['jz'], 1)
        c['jz'] = 0.2
        self.assertEqual(c['jz'], 0.2)

    def test_az(self):
        """Test `az`."""

        c = Color('color(--jzazbz 1 0.2 -0.3 / 1)')
        self.assertEqual(c['az'], 0.2)
        c['az'] = 0.1
        self.assertEqual(c['az'], 0.1)

    def test_bz(self):
        """Test `bz`."""

        c = Color('color(--jzazbz 1 0.2 -0.3 / 1)')
        self.assertEqual(c['bz'], -0.3)
        c['bz'] = 0.1
        self.assertEqual(c['bz'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--jzazbz 1 0.2 -0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)
