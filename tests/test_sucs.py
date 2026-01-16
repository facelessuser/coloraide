"""Test sUCS."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
import pytest


class TestSUCS(util.ColorAssertsPyTest):
    """Test sUCS."""

    COLORS = [
        ('red', 'color(--sucs 54.706 55.669 29.937)'),
        ('orange', 'color(--sucs 74.256 44.701 67.919)'),
        ('yellow', 'color(--sucs 96.251 49.565 101.84)'),
        ('green', 'color(--sucs 43.283 36.032 134.25)'),
        ('blue', 'color(--sucs 31.275 54.027 250.27)'),
        ('indigo', 'color(--sucs 23.401 32.158 290.85)'),
        ('violet', 'color(--sucs 69.723 38.839 325.3)'),
        ('white', 'color(--sucs 100 0 0)'),
        ('gray', 'color(--sucs 51.724 0 0)'),
        ('black', 'color(--sucs 0 0 0)'),
        # Test color
        ('color(--sucs 50 10 50)', 'color(--sucs 50 10 50)'),
        ('color(--sucs 50 10 50 / 0.5)', 'color(--sucs 50 10 50 / 0.5)'),
        ('color(--sucs 50% 50% 50 / 50%)', 'color(--sucs 50 32.5 50 / 0.5)'),
        ('color(--sucs none none none / none)', 'color(--sucs none none none / none)'),
        # Test percent ranges
        ('color(--sucs 0% 0% 50)', 'color(--sucs 0 0 50)'),
        ('color(--sucs 100% 100% 50)', 'color(--sucs 100 65 50)'),
        ('color(--sucs -100% -100% 50)', 'color(--sucs -100 -65 50)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('sucs'), Color(color2))


class TestSUCSSerialize(util.ColorAssertsPyTest):
    """Test sUCS serialization."""

    COLORS = [
        # Test color
        ('color(--sucs 75 10 50 / 0.5)', {}, 'color(--sucs 75 10 50 / 0.5)'),
        # Test alpha
        ('color(--sucs 75 10 50)', {'alpha': True}, 'color(--sucs 75 10 50 / 1)'),
        ('color(--sucs 75 10 50 / 0.5)', {'alpha': False}, 'color(--sucs 75 10 50)'),
        # Test None
        ('color(--sucs none 10 50)', {}, 'color(--sucs 0 10 50)'),
        ('color(--sucs none 10 50)', {'none': True}, 'color(--sucs none 10 50)'),
        # Test Fit (not bound)
        ('color(--sucs 120 10 50)', {}, 'color(--sucs 120 10 50)'),
        ('color(--sucs 120 10 50)', {'fit': False}, 'color(--sucs 120 10 50)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestSUCSPoperties(util.ColorAsserts, unittest.TestCase):
    """Test sUCS."""

    def test_names(self):
        """Test LCh-ish names."""

        c = Color('color(--sucs 96.323 21.06 55.728)')
        self.assertEqual(c._space.names(), ('i', 'c', 'h'))
        self.assertEqual(c._space.radial_name(), 'c')
        self.assertEqual(c._space.hue_name(), 'h')
        self.assertEqual(c._space.lightness_name(), 'i')

    def test_i(self):
        """Test `i`."""

        c = Color('color(--sucs 96.323 21.06 55.728)')
        self.assertEqual(c['i'], 96.323)
        c['i'] = 0.2
        self.assertEqual(c['i'], 0.2)

    def test_c(self):
        """Test `c`."""

        c = Color('color(--sucs 96.323 21.06 55.728)')
        self.assertEqual(c['c'], 21.06)
        c['c'] = 0.1
        self.assertEqual(c['c'], 0.1)

    def test_h(self):
        """Test `h`."""

        c = Color('color(--sucs 96.323 21.06 55.728)')
        self.assertEqual(c['h'], 55.728)
        c['h'] = 0.1
        self.assertEqual(c['h'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--sucs 96.323 21.06 55.728)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)

    def test_null_normalization_negative_chroma(self):
        """Test minimum saturation."""

        c = Color('color(--sucs 90% -10 120 / 1)').normalize()
        self.assertColorEqual(c, Color('color(--sucs 90% 7.9804 300)'))
