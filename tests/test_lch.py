"""Test LCH library."""
import unittest
import math
from . import util
from coloraide import Color, NaN


class TestLCHInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test LCH."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("lch", [20, 10, 130]), Color('lch(20% 10 130)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("lch", [20, 10, 130])), Color('lch(20% 10 130)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--lch 20% 10 130)"

        self.assertEqual(Color(color).to_string(**args), 'color(--lch 20 10 130)')

        color = "color(--lch 20% 10 130 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--lch 20 10 130 / 0.5)')

        color = "color(--lch 20% 10 130 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--lch 20 10 130 / 0.5)')

    def test_comma(self):
        """Test comma input and comma output format."""

        args = {"comma": True}

        color = "lch(20%, 10, 130)"
        lch = Color(color)
        self.assertEqual(color, lch.to_string(**args))

        color = "lch(20%, 10, 130, 1)"
        lch = Color(color)
        self.assertEqual("lch(20%, 10, 130)", lch.to_string(**args))

        color = "lch(20%, 10, 130, 0.2)"
        lch = Color(color)
        self.assertEqual("lch(20%, 10, 130, 0.2)", lch.to_string(**args))

    def test_space(self):
        """Test space input and space output format."""

        args = {}

        color = "lch(20% 10 130)"
        lch = Color(color)
        self.assertEqual(color, lch.to_string(**args))

        color = "lch(20% 10 130 / 1)"
        lch = Color(color)
        self.assertEqual("lch(20% 10 130)", lch.to_string(**args))

        color = "lch(20% 10 130 / 0.2)"
        lch = Color(color)
        self.assertEqual(color, lch.to_string(**args))

    def test_percent(self):
        """Test that percents work properly."""

        args = {"comma": True}

        color = "lch(20%, 10, 130, 100%)"
        lch = Color(color)
        self.assertEqual("lch(20%, 10, 130)", lch.to_string(**args))

        color = "lch(20%, 10, 130, 20%)"
        lch = Color(color)
        self.assertEqual("lch(20%, 10, 130, 0.2)", lch.to_string(**args))

        args["comma"] = False

        color = "lch(20% 10 130 / 100%)"
        lch = Color(color)
        self.assertEqual("lch(20% 10 130)", lch.to_string(**args))

        color = "lch(20% 10 130 / 20%)"
        lch = Color(color)
        self.assertEqual("lch(20% 10 130 / 0.2)", lch.to_string(**args))

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"comma": True, "alpha": False}

        color = "lch(20%, 10, 130, 0.2)"
        lch = Color(color)
        self.assertEqual("lch(20%, 10, 130)", lch.to_string(**args))

        args["comma"] = False

        color = "lch(20% 10 130 / 0.2)"
        lch = Color(color)
        self.assertEqual("lch(20% 10 130)", lch.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"comma": True, "alpha": True}

        color = "lch(20%, 10, 130, 1)"
        lch = Color(color)
        self.assertEqual("lch(20%, 10, 130, 1)", lch.to_string(**args))

        args["comma"] = False

        color = "lch(20% 10 130 / 1)"
        lch = Color(color)
        self.assertEqual("lch(20% 10 130 / 1)", lch.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--lch 20.1234567% 10.1234567 130.1234567)'
        self.assertEqual(Color(color).to_string(), 'lch(20.123% 10.123 130.12)')
        self.assertEqual(Color(color).to_string(precision=3), 'lch(20.1% 10.1 130)')
        self.assertEqual(Color(color).to_string(precision=0), 'lch(20% 10 130)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'lch(20.12345669999999842048055143095552921295166015625% 10.1234567000000001968373908312059938907623291015625 130.123456699999991315053193829953670501708984375)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--lch 20% 200 120)').to_string(),
            'lch(20% 200 120)'
        )

        self.assertEqual(
            Color('color(--lch 20% 200 120)').to_string(fit="clip"),
            'lch(20% 200 120)'
        )

        self.assertEqual(
            Color('color(--lch 20% 200 120)').to_string(fit=False),
            'lch(20% 200 120)'
        )

    def test_hue_inputs(self):
        """Test hue inputs."""

        color = "lch(90%, 50, 90deg)"
        lch = Color(color)
        self.assertEqual("lch(90% 50 90)", lch.to_string())

        color = "lch(90%, 50, {:f}rad)".format(math.radians(90))
        lch = Color(color)
        self.assertEqual("lch(90% 50 90)", lch.to_string())

        color = "lch(90%, 50, 100grad)"
        lch = Color(color)
        self.assertEqual("lch(90% 50 90)", lch.to_string())

        color = "lch(90%, 50, 0.25turn)"
        lch = Color(color)
        self.assertEqual("lch(90% 50 90)", lch.to_string())


class TestLCHProperties(util.ColorAsserts, unittest.TestCase):
    """Test LCH."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--lch 90% 50 120 / 1)')
        self.assertEqual(c.lightness, 90)
        c.lightness = 80
        self.assertEqual(c.lightness, 80)

    def test_chroma(self):
        """Test `chroma`."""

        c = Color('color(--lch 90% 50 120 / 1)')
        self.assertEqual(c.chroma, 50)
        c.chroma = 40
        self.assertEqual(c.chroma, 40)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--lch 90% 50 120 / 1)')
        self.assertEqual(c.hue, 120)
        c.hue = 110
        self.assertEqual(c.hue, 110)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--lch 90% 50 120 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('lch', [90, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_auto_null(self):
        """Test auto null."""

        c = Color('lch(90% 0 120 / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('lch(90% 0.000000000009 120 / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_from_lab(self):
        """Test null from Lab conversion."""

        c1 = Color('lab(90% 0 0)')
        c2 = c1.convert('lch')
        self.assertColorEqual(c2, Color('lch(90% 0 0)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to LCH with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('lch')
                self.assertTrue(color2.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chorma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to lab."""

        self.assertColorEqual(Color('lch(90% -10 120 / 1)').convert('lab'), Color('lab(90% 0 0)'))
