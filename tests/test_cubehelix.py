"""Test Cubehelix."""
import unittest
from . import util
from coloraide.everything import ColorAll as Color
from coloraide import NaN
import pytest


class TestCubehelix(util.ColorAssertsPyTest):
    """Test Cubehelix."""

    COLORS = [
        ('red', 'color(--cubehelix 351.81 1.9489 0.3)'),
        ('orange', 'color(--cubehelix 36.577 1.7357 0.68176)'),
        ('yellow', 'color(--cubehelix 56.942 4.6144 0.89)'),
        ('green', 'color(--cubehelix 109.96 1.1194 0.29616)'),
        ('blue', 'color(--cubehelix 236.94 4.6144 0.11)'),
        ('indigo', 'color(--cubehelix 268.23 1.7028 0.14431)'),
        ('violet', 'color(--cubehelix 289.96 0.90999 0.68345)'),
        ('white', 'color(--cubehelix 0 0 1)'),
        ('gray', 'color(--cubehelix 0 0 0.50196)'),
        ('black', 'color(--cubehelix 0 0 0)'),
        # Test color
        ('color(--cubehelix 270 0.3 0.5)', 'color(--cubehelix 270 0.3 0.5)'),
        ('color(--cubehelix 270 0.3 0.5 / 0.5)', 'color(--cubehelix 270 0.3 0.5 / 0.5)'),
        ('color(--cubehelix 180 50% 50% / 50%)', 'color(--cubehelix 180 2.3072 0.5 / 0.5)'),
        ('color(--cubehelix none none none / none)', 'color(--cubehelix 0 0 0 / 0)'),
        # Test percent ranges
        ('color(--cubehelix 0 0% 0%)', 'color(--cubehelix 0 0 0)'),
        ('color(--cubehelix 360 100% 100%)', 'color(--cubehelix 360 4.6144 1)'),
        ('color(--cubehelix -360 -100% -100%)', 'color(--cubehelix -360 -4.6144 -1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_hsi_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('cubehelix'), Color(color2))


class TestCubehelixSerialize(util.ColorAssertsPyTest):
    """Test Cubehelix serialization."""

    COLORS = [
        # Test color
        ('color(--cubehelix 50 0.3 0.5 / 0.5)', {}, 'color(--cubehelix 50 0.3 0.5 / 0.5)'),
        # Test alpha
        ('color(--cubehelix 50 0.3 0.5)', {'alpha': True}, 'color(--cubehelix 50 0.3 0.5 / 1)'),
        ('color(--cubehelix 50 0.3 0.5 / 0.5)', {'alpha': False}, 'color(--cubehelix 50 0.3 0.5)'),
        # Test None
        ('color(--cubehelix 50 0.3 none)', {}, 'color(--cubehelix 50 0.3 0)'),
        ('color(--cubehelix 50 0.3 none)', {'none': True}, 'color(--cubehelix 50 0.3 none)'),
        # Test Fit (not bound)
        ('color(--cubehelix 50 5 0.5)', {}, 'color(--cubehelix 54.832 0.93022 0.4529)'),
        ('color(--cubehelix 50 5 0.5)', {'fit': False}, 'color(--cubehelix 50 5 0.5)'),
        ('color(--cubehelix 171.81 -1.9489 0.3)', {}, 'color(--cubehelix 351.81 1.9489 0.3)'),
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestMiscCubehelix(util.ColorAsserts, unittest.TestCase):
    """Test miscellaneous Cubehelix cases."""

    def test_normalize_negative_saturation(self):
        """Test normalization of negative saturation."""

        self.assertColorEqual(
            Color('color(--cubehelix 171.81 -1.9489 0.3)').normalize(),
            Color('color(--cubehelix 351.81 1.9489 0.3)')
        )


class TestCubehelixPoperties(util.ColorAsserts, unittest.TestCase):
    """Test Cubehelix."""

    def test_names(self):
        """Test HSV-ish names."""

        self.assertEqual(Color('color(--cubehelix 60 1 0.66667)')._space.names(), ('h', 's', 'l'))

    def test_h(self):
        """Test `h`."""

        c = Color('color(--cubehelix 60 1 0.66667)')
        self.assertEqual(c['h'], 60)
        c['h'] = 0.2
        self.assertEqual(c['h'], 0.2)

    def test_s(self):
        """Test `s`."""

        c = Color('color(--cubehelix 60 1 0.66667)')
        self.assertEqual(c['s'], 1)
        c['s'] = 0.1
        self.assertEqual(c['s'], 0.1)

    def test_l(self):
        """Test `l`."""

        c = Color('color(--cubehelix 60 1 0.66667)')
        self.assertEqual(c['l'], 0.66667)
        c['l'] = 0.1
        self.assertEqual(c['l'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--cubehelix 60 1 0.66667)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('cubehelix', [NaN, 0.5, 1], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--cubehelix none 0% 75% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_sat(self):
        """Test minimum saturation."""

        c = Color('color(--cubehelix 270 0% 75% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_intensity(self):
        """Test minimum intensity."""

        c = Color('color(--cubehelix 270 20% 0% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))
