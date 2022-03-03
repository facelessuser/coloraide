"""Test Oklch library."""
import unittest
from . import util
from coloraide import NaN
from coloraide import Color as ColorOrig
from coloraide.spaces.oklch.css import Oklch


class Color(ColorOrig):
    """Utilize Oklab CSS (currently) experimental."""


Color.register(Oklch, overwrite=True)


class TestOklchInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test Oklch."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("oklch", [0.9, 0.5, 270]), Color('oklch(90% 0.5 270)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("oklch", [0.9, 0.5, 270])), Color('oklch(90% 0.5 270)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--oklch 0.9 0.5 270)"

        self.assertEqual(Color(color).to_string(**args), 'color(--oklch 0.9 0.5 270)')

        color = "color(--oklch 0.9 0.5 270 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--oklch 0.9 0.5 270 / 0.5)')

        color = "color(--oklch 90% 0.5 270 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--oklch 0.9 0.5 270 / 0.5)')

    def test_space(self):
        """Test space input and space output format."""

        args = {}

        color = "oklch(20% 0.1 130)"
        lch = Color(color)
        self.assertEqual(color, lch.to_string(**args))

        color = "oklch(20% 0.1 130 / 1)"
        lch = Color(color)
        self.assertEqual("oklch(20% 0.1 130)", lch.to_string(**args))

        color = "oklch(20% 0.1 130 / 0.2)"
        lch = Color(color)
        self.assertEqual(color, lch.to_string(**args))

    def test_percent(self):
        """Test that percents work properly."""

        args = {}

        color = "oklch(20% 0.1 130 / 100%)"
        lch = Color(color)
        self.assertEqual("oklch(20% 0.1 130)", lch.to_string(**args))

        color = "oklch(20% 0.1 130 / 20%)"
        lch = Color(color)
        self.assertEqual("oklch(20% 0.1 130 / 0.2)", lch.to_string(**args))

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "oklch(90% 0.5 270 / 0.5)"
        oklch = Color(color)
        self.assertEqual("oklch(90% 0.5 270)", oklch.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "oklch(90% 0.5 270 / 100%)"
        oklch = Color(color)
        self.assertEqual("oklch(90% 0.5 270 / 1)", oklch.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--oklch 0.123456 0.123456 0.123456)'
        self.assertEqual(Color(color).to_string(), 'oklch(12.346% 0.12346 0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'oklch(12.3% 0.123 0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'oklch(12% 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'oklch(12.3455999999999992411403582082130014896392822265625% 0.12345599999999999629718416827017790637910366058349609 0.12345599999999999629718416827017790637910366058349609)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('oklch(90% 200 270)').to_string(),
            'oklch(90% 200 270)'
        )

        self.assertEqual(
            Color('oklch(90% 200 270)').to_string(fit="clip"),
            'oklch(90% 200 270)'
        )

        self.assertEqual(
            Color('oklch(90% 200 270)').to_string(fit=False),
            'oklch(90% 200 270)'
        )


class TestOklchProperties(util.ColorAsserts, unittest.TestCase):
    """Test Oklch."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--oklch 0.9 0.5 270 / 1)')
        self.assertEqual(c.lightness, 0.9)
        c.lightness = 0.2
        self.assertEqual(c.lightness, 0.2)

    def test_chroma(self):
        """Test `chroma`."""

        c = Color('color(--oklch 0.9 0.5 270 / 1)')
        self.assertEqual(c.chroma, 0.5)
        c.chroma = 0.1
        self.assertEqual(c.chroma, 0.1)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--oklch 0.9 0.5 270 / 1)')
        self.assertEqual(c.hue, 270)
        c.hue = 0.1
        self.assertEqual(c.hue, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--oklch 0.9 0.5 270 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('oklch', [0.9, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--oklch 90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('color(--oklch 90% 0.0000009 120 / 1)').convert('srgb').convert('oklch')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color('oklch(90% 0 120 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_from_oklab(self):
        """Test null from Lab conversion."""

        c1 = Color('color(--oklab 90% 0 0)')
        c2 = c1.convert('oklch')
        self.assertColorEqual(c2, Color('color(--oklch 90% 0 0)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to Oklch with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('oklch')
                self.assertTrue(color2.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chorma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to Oklab."""

        self.assertColorEqual(Color('color(--oklch 90% -10 120 / 1)').convert('oklab'), Color('color(--oklab 0.9 0 0)'))
