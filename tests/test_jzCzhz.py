"""Test JzCzhz library."""
import unittest
from . import util
from coloraide import Color, NaN


class TestJzCzhzInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test JzCzhz."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("jzczhz", [0.22, 0.5, 270]), Color('color(--jzczhz 22% 0.5 270)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("jzczhz", [0.22, 0.5, 270])), Color('color(--jzczhz 22% 0.5 270)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--jzczhz 0.22 0.5 270)"

        self.assertEqual(Color(color).to_string(**args), 'color(--jzczhz 0.22 0.5 270)')

        color = "color(--jzczhz 0.22 0.5 270 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--jzczhz 0.22 0.5 270 / 0.5)')

        color = "color(--jzczhz 22% 0.5 270 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--jzczhz 0.22 0.5 270 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(--jzczhz 0.22 0.5 270 / 0.5)"
        jzczhz = Color(color)
        self.assertEqual("color(--jzczhz 0.22 0.5 270)", jzczhz.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(--jzczhz 0.22 0.5 270 / 100%)"
        jzczhz = Color(color)
        self.assertEqual("color(--jzczhz 0.22 0.5 270 / 1)", jzczhz.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--jzczhz 0.123456 0.123456 0.123456)'
        self.assertEqual(Color(color).to_string(), 'color(--jzczhz 0.12346 0.12346 0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(--jzczhz 0.123 0.123 0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(--jzczhz 0 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(--jzczhz 0.12345599999999999629718416827017790637910366058349609 0.12345599999999999629718416827017790637910366058349609 0.12345599999999999629718416827017790637910366058349609)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--jzczhz 0.22 200 270)').to_string(),
            'color(--jzczhz 0.22 200 270)'
        )

        self.assertEqual(
            Color('color(--jzczhz 0.22 200 270)').to_string(fit="clip"),
            'color(--jzczhz 0.22 200 270)'
        )

        self.assertEqual(
            Color('color(--jzczhz 0.22 200 270)').to_string(fit=False),
            'color(--jzczhz 0.22 200 270)'
        )


class TestJzCzhzProperties(util.ColorAsserts, unittest.TestCase):
    """Test JzCzhz."""

    def test_jz(self):
        """Test `jz`."""

        c = Color('color(--jzczhz 0.22 0.5 270 / 1)')
        self.assertEqual(c.jz, 0.22)
        c.jz = 0.2
        self.assertEqual(c.jz, 0.2)

    def test_cz(self):
        """Test `chroma`."""

        c = Color('color(--jzczhz 0.22 0.5 270 / 1)')
        self.assertEqual(c.chroma, 0.5)
        c.chroma = 0.1
        self.assertEqual(c.chroma, 0.1)

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--jzczhz 0.22 0.5 270 / 1)')
        self.assertEqual(c.hue, 270)
        c.hue = 0.1
        self.assertEqual(c.hue, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--jzczhz 0.22 0.5 270 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('jzczhz', [90, 50, NaN], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_none_input(self):
        """Test `none` null."""

        c = Color('color(--jzczhz 90% 0 none / 1)')
        self.assertTrue(c.is_nan('hue'))

    def test_near_zero_null(self):
        """
        Test very near zero null.

        This is a fix up to help give more sane hues
        when chroma is very close to zero.
        """

        c = Color('color(--jzczhz 90% 0.00009 120 / 1)').convert('jzazbz').convert('jzczhz')
        self.assertTrue(c.is_nan('hue'))

    def test_null_normalization_min_chroma(self):
        """Test minimum saturation."""

        c = Color('color(--jzczhz 90% 0 120 / 1)').normalize()
        self.assertTrue(c.is_nan('hue'))

    def test_from_jzazbz(self):
        """Test null from Lab conversion."""

        c1 = Color('color(--jzazbz 90% 0 0)')
        c2 = c1.convert('jzczhz')
        self.assertColorEqual(c2, Color('color(--jzczhz 90% 0 0)'))
        self.assertTrue(c2.is_nan('hue'))

    def test_achromatic_hue(self):
        """Test that all RGB-ish colors convert to Oklch with a null hue."""

        for space in ('srgb', 'display-p3', 'rec2020', 'a98-rgb', 'prophoto-rgb'):
            for x in range(0, 256):
                color = Color('color({space} {num:f} {num:f} {num:f})'.format(space=space, num=x / 255))
                color2 = color.convert('jzczhz')
                self.assertTrue(color2.is_nan('hue'))


class TestQuirks(util.ColorAsserts, unittest.TestCase):
    """Test quirks."""

    def test_chorma_less_than_zero_convert(self):
        """Test handling of negative chroma when converting to Oklab."""

        self.assertColorEqual(
            Color('color(--jzczhz 90% -10 120 / 1)').convert('jzazbz'), Color('color(--jzazbz 0.9 0 0)')
        )
