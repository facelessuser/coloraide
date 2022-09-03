"""Test gamut mapping fitting."""
import unittest
from coloraide.everything import ColorAll as Color
from . import util


class TestGamut(util.ColorAsserts, unittest.TestCase):
    """Test gamut mapping/fitting."""

    def test_in_gamut(self):
        """Test in gamut check."""

        self.assertTrue(Color('red').in_gamut())

    def test_out_of_gamut(self):
        """Test in gamut check."""

        self.assertFalse(Color('color(srgb 2 0 0)').in_gamut())

    def test_in_gamut_other_space(self):
        """Test if a color is in gamut in a different space."""

        self.assertTrue(Color('red').convert('lch').in_gamut('srgb'))

    def test_fit(self):
        """Test fit."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.clone().fit()
        self.assertIsNot(color, color2)
        self.assertTrue(color2.in_gamut())

    def test_fit_clip(self):
        """Test fit."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.clone().fit(method="clip")
        self.assertIsNot(color, color2)
        self.assertTrue(color2.in_gamut())
        color3 = color.clone().fit()
        self.assertColorNotEqual(color2, color3)

    def test_clip(self):
        """Test fit."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.clone().clip()
        self.assertIsNot(color, color2)
        self.assertTrue(color2.in_gamut())
        color3 = color.clone().fit()
        self.assertColorNotEqual(color2, color3)

    def test_clip_in_place(self):
        """Test clip in place."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.clip()
        self.assertIs(color, color2)
        self.assertTrue(color2.in_gamut())
        color3 = color.clone().fit()
        self.assertColorEqual(color2, color3)

    def test_clip_other_space(self):
        """Test clip other space."""

        color = Color('hsl(330 110% 50%)')
        self.assertFalse(color.in_gamut('srgb'))
        self.assertTrue(color.clip('srgb').in_gamut('srgb'))

    def test_clip_undefined(self):
        """Test that clip leaves undefined channels alone."""

        color = Color('rgb(none 255.1 -0.1)')
        self.assertFalse(color.in_gamut('srgb'))
        color2 = color.clone().clip('srgb')
        self.assertColorEqual(color2, Color('rgb(0 255 0)'))
        self.assertTrue(color2.in_gamut('srgb'))

    def test_sdr_extremes_low(self):
        """Test SDR extreme low case."""

        color = Color('hsl(none 0% -10%)')
        self.assertColorEqual(color.fit(), Color('hsl(0 0% 0%)'))

    def test_sdr_extremes_high(self):
        """Test SDR extreme high case."""

        color = Color('hsl(none 0% 110%)')
        self.assertColorEqual(color.fit(), Color('hsl(0 0% 100%)'))

    def test_hdr_extreme_high(self):
        """Test HDR extreme high case."""

        color = Color('color(--rec2100pq 1.01 0.2 0)')
        self.assertColorEqual(color.fit(), Color('color(--rec2100pq 1 0.63544 1)'))

    def test_hdr_extreme_low(self):
        """Test HDR extreme low case."""

        color = Color('color(--rec2100pq -0.3 -0.2 0)')
        self.assertColorEqual(color.fit(), Color('color(--rec2100pq 0.0 0.0 0.0)'))

    def test_bad_fit(self):
        """Test fit."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        with self.assertRaises(ValueError):
            color.fit(method="bad")

    def test_fit_in_place(self):
        """Test fit in place."""

        color = Color('color(srgb 2 0.5 0.5)')
        self.assertFalse(color.in_gamut())
        color2 = color.fit()
        self.assertIs(color, color2)
        self.assertTrue(color2.in_gamut())

    def test_fit_other_space(self):
        """Test fit in other space."""

        color = Color('hsl(330 110% 50%)')
        self.assertFalse(color.in_gamut('srgb'))
        self.assertTrue(color.fit('srgb').in_gamut('srgb'))

    def test_out_of_gamut_other_space(self):
        """Test if a color is in gamut in a different space."""

        self.assertFalse(Color('color(srgb 2 0 0)').convert('lch').in_gamut('srgb'))
