"""Test ICtCp library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestICtCp(util.ColorAssertsPyTest):
    """Test ICtCp."""

    COLORS = [
        ('red', 'color(--ictcp 0.42785 -0.11574 0.2788)'),
        ('orange', 'color(--ictcp 0.50497 -0.20797 0.11077)'),
        ('yellow', 'color(--ictcp 0.56981 -0.25166 0.0379)'),
        ('green', 'color(--ictcp 0.39138 -0.24057 -0.04421)'),
        ('blue', 'color(--ictcp 0.35607 0.26914 -0.16143)'),
        ('indigo', 'color(--ictcp 0.27954 0.23658 -0.00107)'),
        ('violet', 'color(--ictcp 0.49387 0.13657 0.05828)'),
        ('white', 'color(--ictcp 0.58069 0 0)'),
        ('gray', 'color(--ictcp 0.42781 0 0)'),
        ('black', 'color(--ictcp 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_igpgtg_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('ictcp'), Color(color2))


class TestICtCpProperties(util.ColorAsserts, unittest.TestCase):
    """Test ICtCp."""

    def test_i(self):
        """Test `i`."""

        c = Color('color(--ictcp 1 0.2 -0.3 / 1)')
        self.assertEqual(c['i'], 1)
        c['i'] = 0.2
        self.assertEqual(c['i'], 0.2)

    def test_ct(self):
        """Test `ct`."""

        c = Color('color(--ictcp 1 0.2 -0.3 / 1)')
        self.assertEqual(c['ct'], 0.2)
        c['ct'] = 0.1
        self.assertEqual(c['ct'], 0.1)

    def test_cp(self):
        """Test `cp`."""

        c = Color('color(--ictcp 1 0.2 -0.3 / 1)')
        self.assertEqual(c['cp'], -0.3)
        c['cp'] = 0.1
        self.assertEqual(c['cp'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--ictcp 1 0.2 -0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)

    def test_labish_names(self):
        """Test `labish_names`."""

        c = Color('color(--ictcp 1 0.2 -0.3 / 1)')
        self.assertEqual(c._space.labish_names(), ('i', 'cp', 'ct'))
