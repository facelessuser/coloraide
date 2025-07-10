"""Test ICtCp library."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestICtCp(util.ColorAssertsPyTest):
    """Test ICtCp."""

    COLORS = [
        ('red', 'ictcp(0.42788 -0.1157 0.27873)'),
        ('orange', 'ictcp(0.50498 -0.20797 0.11073)'),
        ('yellow', 'ictcp(0.56983 -0.25169 0.03788)'),
        ('green', 'ictcp(0.39138 -0.24061 -0.04423)'),
        ('blue', 'ictcp(0.35598 0.26933 -0.16137)'),
        ('indigo', 'ictcp(0.2795 0.23671 -0.00097)'),
        ('violet', 'ictcp(0.49386 0.13661 0.05832)'),
        ('white', 'ictcp(0.58069 0 0)'),
        ('gray', 'ictcp(0.42781 0 0)'),
        ('black', 'ictcp(0 0 0)'),
        # Test color
        ('ictcp(0.5 0.1 -0.1)', 'ictcp(0.5 0.1 -0.1)'),
        ('ictcp(0.5 0.1 -0.1 / 0.5)', 'ictcp(0.5 0.1 -0.1 / 0.5)'),
        ('ictcp(50% 50% -50% / 50%)', 'ictcp(0.5 0.25 -0.25 / 0.5)'),
        ('ictcp(none none none / none)', 'ictcp(none none none / none)'),
        # Test percent ranges
        ('ictcp(0% 0% 0%)', 'ictcp(0 0 0)'),
        ('ictcp(100% 100% 100%)', 'ictcp(1 0.5 0.5)'),
        ('ictcp(-100% -100% -100%)', 'ictcp(-1 -0.5 -0.5)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('ictcp'), Color(color2))


class TestICtCpSerialize(util.ColorAssertsPyTest):
    """Test ICtCp serialization."""

    COLORS = [
        # Test color
        ('ictcp(0.75 0.1 -0.1 / 0.5)', {}, 'ictcp(0.75 0.1 -0.1 / 0.5)'),
        # Test alpha
        ('ictcp(0.75 0.1 -0.1)', {'alpha': True}, 'ictcp(0.75 0.1 -0.1 / 1)'),
        ('ictcp(0.75 0.1 -0.1 / 0.5)', {'alpha': False}, 'ictcp(0.75 0.1 -0.1)'),
        # Test None
        ('ictcp(none 0.1 -0.1)', {}, 'ictcp(0 0.1 -0.1)'),
        ('ictcp(none 0.1 -0.1)', {'none': True}, 'ictcp(none 0.1 -0.1)'),
        # Test Fit (not bound)
        ('ictcp(0.75 0.6 -0.1)', {}, 'ictcp(0.75 0.6 -0.1)'),
        ('ictcp(0.75 0.6 -0.1)', {'fit': False}, 'ictcp(0.75 0.6 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestICtCpProperties(util.ColorAsserts, unittest.TestCase):
    """Test ICtCp."""

    def test_names(self):
        """Test Lab-ish names."""

        c = Color('ictcp(1 0.2 -0.3 / 1)')
        self.assertEqual(c._space.lightness_name(), 'i')

    def test_i(self):
        """Test `i`."""

        c = Color('ictcp(1 0.2 -0.3 / 1)')
        self.assertEqual(c['i'], 1)
        c['i'] = 0.2
        self.assertEqual(c['i'], 0.2)

    def test_ct(self):
        """Test `ct`."""

        c = Color('ictcp(1 0.2 -0.3 / 1)')
        self.assertEqual(c['ct'], 0.2)
        c['ct'] = 0.1
        self.assertEqual(c['ct'], 0.1)

    def test_cp(self):
        """Test `cp`."""

        c = Color('ictcp(1 0.2 -0.3 / 1)')
        self.assertEqual(c['cp'], -0.3)
        c['cp'] = 0.1
        self.assertEqual(c['cp'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('ictcp(1 0.2 -0.3 / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)

    def test_labish_names(self):
        """Test `labish_names`."""

        c = Color('ictcp(1 0.2 -0.3 / 1)')
        self.assertEqual(c._space.names(), ('i', 'ct', 'cp'))
