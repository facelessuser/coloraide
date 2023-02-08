"""Test HWB library."""
import unittest
from . import util
from coloraide import Color, NaN
import pytest


class TestHWB(util.ColorAssertsPyTest):
    """Test HWB."""

    COLORS = [
        ('red', 'color(--hwb 0 0 0)'),
        ('orange', 'color(--hwb 38.824 0 0)'),
        ('yellow', 'color(--hwb 60 0 0)'),
        ('green', 'color(--hwb 120 0 0.49804)'),
        ('blue', 'color(--hwb 240 0 0)'),
        ('indigo', 'color(--hwb 274.62 0 0.4902)'),
        ('violet', 'color(--hwb 300 0.5098 0.06667)'),
        ('white', 'color(--hwb none 1 0)'),
        ('gray', 'color(--hwb none 0.50196 0.49804)'),
        ('black', 'color(--hwb none 0 1)'),
        # Test color
        ('color(--hwb 270 0.3 0.5)', 'color(--hwb 270 0.3 0.5)'),
        ('color(--hwb 270 0.3 0.5 / 0.5)', 'color(--hwb 270 0.3 0.5 / 0.5)'),
        ('color(--hwb 50% 30% 50% / 50%)', 'color(--hwb 180 0.3 0.5 / 0.5)'),
        ('color(--hwb none none none / none)', 'color(--hwb none none none / none)'),
        # Test percent ranges
        ('color(--hwb 0% 0% 0%)', 'color(--hwb 0 0 none)'),
        ('color(--hwb 100% 100% 100%)', 'color(--hwb 360 1 1 / 1)'),
        ('color(--hwb -100% -100% -100%)', 'color(--hwb -360 -1 -1 / 1)')
    ]

    @pytest.mark.parametrize('color1,color2', COLORS)
    def test_colors(self, color1, color2):
        """Test colors."""

        self.assertColorEqual(Color(color1).convert('hwb'), Color(color2), color=True)


class TestHWBSerialize(util.ColorAssertsPyTest):
    """Test HWB serialization."""

    COLORS = [
        # Test hex no options
        ('hwb(270 30% 50%)', {}, 'hwb(270 30% 50%)'),
        # Test alpha
        ('hwb(270 30% 50% / 0.5)', {}, 'hwb(270 30% 50% / 0.5)'),
        ('hwb(270 30% 50%)', {'alpha': True}, 'hwb(270 30% 50% / 1)'),
        ('hwb(270 30% 50% / 0.5)', {'alpha': False}, 'hwb(270 30% 50%)'),
        # Test None
        ('hwb(none 30% 50%)', {}, 'hwb(0 30% 50%)'),
        ('hwb(none 30% 50%)', {'none': True}, 'hwb(none 30% 50%)'),
        # Test fit
        ('hwb(20 0% -55%)', {}, 'hwb(16.837 75.709% 0%)'),
        ('hwb(20 0% -55%)', {'fit': False}, 'hwb(20 0% -55%)'),
        # Test color
        ('hwb(none 30% 50% / 0.5)', {'color': True}, 'color(--hwb 0 0.3 0.5 / 0.5)'),
        ('hwb(none 30% 50%)', {'color': True, 'none': True}, 'color(--hwb none 0.3 0.5)'),
        ('hwb(0 30% 50%)', {'color': True, 'alpha': True}, 'color(--hwb 0 0.3 0.5 / 1)'),
        ('hwb(0 30% 50% / 0.5)', {'color': True, 'alpha': False}, 'color(--hwb 0 0.3 0.5)')
    ]

    @pytest.mark.parametrize('color1,options,color2', COLORS)
    def test_colors(self, color1, options, color2):
        """Test colors."""

        self.assertEqual(Color(color1).to_string(**options), color2)


class TestHWBProperties(util.ColorAsserts, unittest.TestCase):
    """Test HWB."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c['hue'], 120)
        c['hue'] = 110
        self.assertEqual(c['hue'], 110)

    def test_whiteness(self):
        """Test `whiteness`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c['whiteness'], 0.5)
        c['whiteness'] = 0.6
        self.assertEqual(c['whiteness'], 0.6)

    def test_blackness(self):
        """Test `blackness`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c['blackness'], 0.2)
        c['blackness'] = 0.1
        self.assertEqual(c['blackness'], 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c['alpha'], 1)
        c['alpha'] = 0.5
        self.assertEqual(c['alpha'], 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_real_achromatic_hue(self):
        """Test that we get the expected achromatic hue."""

        self.assertEqual(Color('white').convert('hwb')._space.achromatic_hue(), 0.0)

    def test_null_input(self):
        """Test null input."""

        c = Color('hwb', [NaN, 0.1, 0.2], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('hwb(none 100% 0% / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_max_white_black(self):
        """Test maximum lightness."""

        c = Color('hwb(270 20% 100% / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_to_hsv(self):
        """Test null from Lab conversion."""

        c1 = Color('color(--hsv 0 0% 50%)')
        c2 = c1.convert('hwb')
        self.assertColorEqual(c2, Color('hwb(0 50% 50%)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_from_hsv(self):
        """Test null from Lab conversion."""

        c1 = Color('hwb(0 50% 50%)')
        c2 = c1.convert('hsv')
        self.assertColorEqual(c2, Color('color(--hsv 0 0% 50%)'))
        self.assertTrue(c2.is_nan('hue'))
