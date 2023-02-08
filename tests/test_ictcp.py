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
        ('black', 'color(--ictcp 0 0 0)'),
        # Test color
        ('color(--ictcp 0.5 0.1 -0.1)', 'color(--ictcp 0.5 0.1 -0.1)'),
        ('color(--ictcp 0.5 0.1 -0.1 / 0.5)', 'color(--ictcp 0.5 0.1 -0.1 / 0.5)'),
        ('color(--ictcp 50% 50% -50% / 50%)', 'color(--ictcp 0.5 0.25 -0.25 / 0.5)'),
        ('color(--ictcp none none none / none)', 'color(--ictcp none none none / none)'),
        # Test percent ranges
        ('color(--ictcp 0% 0% 0%)', 'color(--ictcp 0 0 0)'),
        ('color(--ictcp 100% 100% 100%)', 'color(--ictcp 1 0.5 0.5)'),
        ('color(--ictcp -100% -100% -100%)', 'color(--ictcp -1 -0.5 -0.5)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_igpgtg_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('ictcp'), Color(color2))


class TestICtCpSerialize(util.ColorAssertsPyTest):
    """Test ICtCp serialization."""

    COLORS = [
        # Test color
        ('color(--ictcp 0.75 0.1 -0.1 / 0.5)', {}, 'color(--ictcp 0.75 0.1 -0.1 / 0.5)'),
        # Test alpha
        ('color(--ictcp 0.75 0.1 -0.1)', {'alpha': True}, 'color(--ictcp 0.75 0.1 -0.1 / 1)'),
        ('color(--ictcp 0.75 0.1 -0.1 / 0.5)', {'alpha': False}, 'color(--ictcp 0.75 0.1 -0.1)'),
        # Test None
        ('color(--ictcp none 0.1 -0.1)', {}, 'color(--ictcp 0 0.1 -0.1)'),
        ('color(--ictcp none 0.1 -0.1)', {'none': True}, 'color(--ictcp none 0.1 -0.1)'),
        # Test Fit (not bound)
        ('color(--ictcp 0.75 0.6 -0.1)', {}, 'color(--ictcp 0.75 0.6 -0.1)'),
        ('color(--ictcp 0.75 0.6 -0.1)', {'fit': False}, 'color(--ictcp 0.75 0.6 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


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
