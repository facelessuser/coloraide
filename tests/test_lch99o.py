"""Test DIN99o LCH library."""
import unittest
from . import util
from coloraide import Color, NaN


class TestLch99oInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test DIN99o LCH."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("lch99o", [20, 10, 130]), Color('color(--lch99o 20% 10 130)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("lch99o", [20, 10, 130])), Color('color(--lch99o 20% 10 130)'))

    def test_space(self):
        """Test space input and space output format."""

        args = {}

        color = "color(--lch99o 20% 10 130)"
        din99o = Color(color)
        self.assertEqual('color(--lch99o 20 10 130)', din99o.to_string(**args))

        color = "color(--lch99o 20% 10 130 / 1)"
        din99o = Color(color)
        self.assertEqual("color(--lch99o 20 10 130)", din99o.to_string(**args))

        color = "color(--lch99o 20% 10 130 / 0.2)"
        din99o = Color(color)
        self.assertEqual("color(--lch99o 20 10 130 / 0.2)", din99o.to_string(**args))

    def test_percent(self):
        """Test that percents work properly."""

        color = "color(--lch99o 20% 10 130 / 100%)"
        din99o = Color(color)
        self.assertEqual("color(--lch99o 20 10 130)", din99o.to_string())

        color = "color(--lch99o 20% 10 130 / 20%)"
        din99o = Color(color)
        self.assertEqual("color(--lch99o 20 10 130 / 0.2)", din99o.to_string())

    def test_no_alpha(self):
        """Test no alpha."""

        color = "color(--lch99o 20% 10 130 / 0.2)"
        din99o = Color(color)
        self.assertEqual("color(--lch99o 20 10 130)", din99o.to_string(alpha=False))

    def test_force_alpha(self):
        """Test force alpha."""

        color = "color(--lch99o 20% 10 130 / 1)"
        din99o = Color(color)
        self.assertEqual("color(--lch99o 20 10 130 / 1)", din99o.to_string(alpha=True))

    def test_precision(self):
        """Test precision."""

        color = 'color(--lch99o 20.1234567% 10.1234567 130.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(--lch99o 20.123 10.123 130.12)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(--lch99o 20.1 10.1 130)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(--lch99o 20 10 130)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(--lch99o 20.12345669999999842048055143095552921295166015625 10.1234567000000001968373908312059938907623291015625 130.123456699999991315053193829953670501708984375)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--lch99o 20% 200 120)').to_string(),
            'color(--lch99o 20 200 120)'
        )

        self.assertEqual(
            Color('color(--lch99o 20% 200 120)').to_string(fit="clip"),
            'color(--lch99o 20 200 120)'
        )

        self.assertEqual(
            Color('color(--lch99o 20% 200 120)').to_string(fit=False),
            'color(--lch99o 20 200 120)'
        )


class TestLch99oProperties(util.ColorAsserts, unittest.TestCase):
    """Test LCH99o."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--lch99o 90% 50 120 / 1)')
        self.assertEqual(c.lightness, 90)
        c.lightness = 80
        self.assertEqual(c.lightness, 80)

    def test_chroma(self):
        """Test `chroma`."""

        c = Color('color(--lch99o 90% 50 120 / 1)')
        self.assertEqual(c.chroma, 50)
        c.chroma = 40
        self.assertEqual(c.chroma, 40)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--lch99o 90% 50 120 / 1)')
        self.assertEqual(c.hue, 120)
        c.hue = 110
        self.assertEqual(c.hue, 110)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--lch99o 90% 50 120 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('lch99o', [90, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--lch99o 90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('color(--lch99o 90% 0.000000000009 120 / 1)').convert('din99o').convert('lch99o')
        self.assertTrue(c.is_nan('hue'))

    def test_from_din99o(self):
        """Test null from DIN99o conversion."""

        c1 = Color('color(--din99o 90% 0 0)')
        c2 = c1.convert('lch99o')
        self.assertColorEqual(c2, Color('color(--lch99o 90% 0 0)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to DIN99o LCH with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('lch99o')
                self.assertTrue(color2.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chorma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to lab."""

        self.assertColorEqual(
            Color('color(--lch99o 90% -10 120 / 1)').convert('din99o'),
            Color('color(--din99o 90% 0 0)')
        )
