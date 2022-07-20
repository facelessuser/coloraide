"""Test IPT."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestIPT(util.ColorAssertsPyTest):
    """Test IPT."""

    COLORS = [
        ('red', 'color(--ipt 0.45616 0.62086 0.44282)'),
        ('orange', 'color(--ipt 0.64877 0.189 0.5303)'),
        ('yellow', 'color(--ipt 0.85654 -0.10831 0.65148)'),
        ('green', 'color(--ipt 0.3933 -0.23454 0.27459)'),
        ('blue', 'color(--ipt 0.4443 -0.23713 -0.74847)'),
        ('indigo', 'color(--ipt 0.28318 0.09827 -0.31015)'),
        ('violet', 'color(--ipt 0.72886 0.31223 -0.24012)'),
        ('white', 'color(--ipt 0.99999 0.00007 -0.00004)'),
        ('gray', 'color(--ipt 0.51724 0.00003 -0.00002)'),
        ('black', 'color(--ipt 0 0 0)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_ipt_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('ipt'), Color(color2))


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
