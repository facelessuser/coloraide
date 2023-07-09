"""Test IPT."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color, NaN
import pytest


class TestIPT(util.ColorAssertsPyTest):
    """Test IPT."""

    COLORS = [
        ('red', 'color(--ipt 0.45616 0.62091 0.44282)'),
        ('orange', 'color(--ipt 0.64877 0.18903 0.5303)'),
        ('yellow', 'color(--ipt 0.85655 -0.1083 0.65147)'),
        ('green', 'color(--ipt 0.3933 -0.23454 0.27459)'),
        ('blue', 'color(--ipt 0.44429 -0.2372 -0.74849)'),
        ('indigo', 'color(--ipt 0.28317 0.09827 -0.31015)'),
        ('violet', 'color(--ipt 0.72886 0.31225 -0.24012)'),
        ('white', 'color(--ipt 0.99999 0.00007 -0.00004)'),
        ('gray', 'color(--ipt 0.51724 0.00003 -0.00002)'),
        ('black', 'color(--ipt 0 0 0)'),
        # Test color
        ('color(--ipt 0.5 0.1 -0.1)', 'color(--ipt 0.5 0.1 -0.1)'),
        ('color(--ipt 0.5 0.1 -0.1 / 0.5)', 'color(--ipt 0.5 0.1 -0.1 / 0.5)'),
        ('color(--ipt 50% 50% -50% / 50%)', 'color(--ipt 0.5 0.5 -0.5 / 0.5)'),
        ('color(--ipt none none none / none)', 'color(--ipt none none none / none)'),
        # Test percent ranges
        ('color(--ipt 0% 0% 0%)', 'color(--ipt 0 0 0)'),
        ('color(--ipt 100% 100% 100%)', 'color(--ipt 1 1 1)'),
        ('color(--ipt -100% -100% -100%)', 'color(--ipt -1 -1 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('ipt'), Color(color2))


class TestIPTSerialize(util.ColorAssertsPyTest):
    """Test IPT serialization."""

    COLORS = [
        # Test color
        ('color(--ipt 0.75 0.1 -0.1 / 0.5)', {}, 'color(--ipt 0.75 0.1 -0.1 / 0.5)'),
        # Test alpha
        ('color(--ipt 0.75 0.1 -0.1)', {'alpha': True}, 'color(--ipt 0.75 0.1 -0.1 / 1)'),
        ('color(--ipt 0.75 0.1 -0.1 / 0.5)', {'alpha': False}, 'color(--ipt 0.75 0.1 -0.1)'),
        # Test None
        ('color(--ipt none 0.1 -0.1)', {}, 'color(--ipt 0 0.1 -0.1)'),
        ('color(--ipt none 0.1 -0.1)', {'none': True}, 'color(--ipt none 0.1 -0.1)'),
        # Test Fit (not bound)
        ('color(--ipt 0.75 1.2 -0.1)', {}, 'color(--ipt 0.75 1.2 -0.1)'),
        ('color(--ipt 0.75 1.2 -0.1)', {'fit': False}, 'color(--ipt 0.75 1.2 -0.1)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestIPTPoperties(util.ColorAsserts, unittest.TestCase):
    """Test IPT."""

    def test_i(self):
        """Test `i`."""

        c = Color('color(--ipt 0.85654 -0.10831 0.65148)')
        self.assertEqual(c['i'], 0.85654)
        c['i'] = 0.2
        self.assertEqual(c['i'], 0.2)

    def test_p(self):
        """Test `p`."""

        c = Color('color(--ipt 0.85654 -0.10831 0.65148)')
        self.assertEqual(c['p'], -0.10831)
        c['p'] = 0.1
        self.assertEqual(c['p'], 0.1)

    def test_t(self):
        """Test `t`."""

        c = Color('color(--ipt 0.85654 -0.10831 0.65148)')
        self.assertEqual(c['t'], 0.65148)
        c['t'] = 0.1
        self.assertEqual(c['t'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--ipt 0.85654 -0.10831 0.65148)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestsAchromatic(util.ColorAsserts, unittest.TestCase):
    """Test achromatic."""

    def test_achromatic(self):
        """Test when color is achromatic."""

        self.assertEqual(Color('#464646').convert('ipt').is_achromatic(), True)
        self.assertEqual(Color('ipt', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('ipt', [0, NaN, NaN]).is_achromatic(), True)
        self.assertEqual(Color('ipt', [0, 0.3, -0.4]).is_achromatic(), False)
        self.assertEqual(Color('ipt', [NaN, 0, -0.3]).is_achromatic(), False)
        self.assertEqual(Color('ipt', [0.3, NaN, 0]).is_achromatic(), False)
        self.assertEqual(Color('ipt', [NaN, NaN, 0]).is_achromatic(), True)
        self.assertEqual(Color('ipt', [-0.5, NaN, NaN]).is_achromatic(), True)
