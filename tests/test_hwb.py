"""Test HWB library."""
import unittest
import math
from . import util
from coloraide import Color, NaN


class TestHWBInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test HWB."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("hwb", [20, 0.1, 0.75]), Color('hwb(20 10% 75%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("hwb", [20, 0.1, 0.75])), Color('hwb(20 10% 75%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--hwb 20 10% 75%)"

        self.assertEqual(Color(color).to_string(**args), 'color(--hwb 20 0.1 0.75)')

        color = "color(--hwb 20 0.1 0.75 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--hwb 20 0.1 0.75 / 0.5)')

        color = "color(--hwb 20 10% 75% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--hwb 20 0.1 0.75 / 0.5)')

    def test_comma(self):
        """Test comma input and comma output format."""

        args = {"comma": True}

        color = "hwb(20, 10%, 75%)"
        hwb = Color(color)
        self.assertEqual(color, hwb.to_string(**args))

        color = "hwb(20, 10%, 75%, 1)"
        hwb = Color(color)
        self.assertEqual("hwb(20, 10%, 75%)", hwb.to_string(**args))

        color = "hwb(20, 10%, 75%, 0.2)"
        hwb = Color(color)
        self.assertEqual("hwb(20, 10%, 75%, 0.2)", hwb.to_string(**args))

    def test_space(self):
        """Test space input and space output format."""

        args = {}

        color = "hwb(20 10% 75%)"
        hwb = Color(color)
        self.assertEqual(color, hwb.to_string(**args))

        color = "hwb(20 10% 75% / 1)"
        hwb = Color(color)
        self.assertEqual("hwb(20 10% 75%)", hwb.to_string(**args))

        color = "hwb(20 10% 75% / 0.2)"
        hwb = Color(color)
        self.assertEqual(color, hwb.to_string(**args))

    def test_percent(self):
        """Test that percents work properly."""

        args = {"comma": True}

        color = "hwb(20, 10%, 75%, 100%)"
        hwb = Color(color)
        self.assertEqual("hwb(20, 10%, 75%)", hwb.to_string(**args))

        color = "hwb(20, 10%, 75%, 20%)"
        hwb = Color(color)
        self.assertEqual("hwb(20, 10%, 75%, 0.2)", hwb.to_string(**args))

        args["comma"] = False

        color = "hwb(20 10% 75% / 100%)"
        hwb = Color(color)
        self.assertEqual("hwb(20 10% 75%)", hwb.to_string(**args))

        color = "hwb(20 10% 75% / 20%)"
        hwb = Color(color)
        self.assertEqual("hwb(20 10% 75% / 0.2)", hwb.to_string(**args))

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"comma": True, "alpha": False}

        color = "hwb(20, 10%, 75%, 0.2)"
        hwb = Color(color)
        self.assertEqual("hwb(20, 10%, 75%)", hwb.to_string(**args))

        args["comma"] = False

        color = "hwb(20 10% 75% / 0.2)"
        hwb = Color(color)
        self.assertEqual("hwb(20 10% 75%)", hwb.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"comma": True, "alpha": True}

        color = "hwb(20, 10%, 75%, 1)"
        hwb = Color(color)
        self.assertEqual("hwb(20, 10%, 75%, 1)", hwb.to_string(**args))

        args["comma"] = False

        color = "hwb(20 10% 75% / 1)"
        hwb = Color(color)
        self.assertEqual("hwb(20 10% 75% / 1)", hwb.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--hwb 20.1234567 10.1234567% 75.1234567%)'
        self.assertEqual(Color(color).to_string(), 'hwb(20.123 10.123% 75.123%)')
        self.assertEqual(Color(color).to_string(precision=3), 'hwb(20.1 10.1% 75.1%)')
        self.assertEqual(Color(color).to_string(precision=0), 'hwb(20 10% 75%)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'hwb(20.12345669999999842048055143095552921295166015625 10.1234567000000001968373908312059938907623291015625% 75.1234567000000055259079090319573879241943359375%)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--hwb 20 0% -55%)').to_string(),
            'hwb(14.271 82.776% 0%)'
        )

        self.assertEqual(
            Color('color(--hwb 20 0% -55%)').to_string(fit="clip"),
            'hwb(20 0% 0%)'
        )

        self.assertEqual(
            Color('color(--hwb 20 0% -55%)').to_string(fit=False),
            'hwb(20 0% -55%)'
        )

    def test_hue_inputs(self):
        """Test hue inputs."""

        color = "hwb(90deg, 50%, 20%)"
        hwb = Color(color)
        self.assertEqual("hwb(90 50% 20%)", hwb.to_string())

        color = "hwb({:f}rad, 50%, 20%)".format(math.radians(90))
        hwb = Color(color)
        self.assertEqual("hwb(90 50% 20%)", hwb.to_string())

        color = "hwb(100grad, 50%, 20%)"
        hwb = Color(color)
        self.assertEqual("hwb(90 50% 20%)", hwb.to_string())

        color = "hwb(0.25turn, 50%, 20%)"
        hwb = Color(color)
        self.assertEqual("hwb(90 50% 20%)", hwb.to_string())


class TestHWBProperties(util.ColorAsserts, unittest.TestCase):
    """Test HWB."""

    def test_hue(self):
        """Test `hue`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c.hue, 120)
        c.hue = 110
        self.assertEqual(c.hue, 110)

    def test_whiteness(self):
        """Test `whiteness`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c.whiteness, 0.5)
        c.whiteness = 0.6
        self.assertEqual(c.whiteness, 0.6)

    def test_blackness(self):
        """Test `blackness`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c.blackness, 0.2)
        c.blackness = 0.1
        self.assertEqual(c.blackness, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--hwb 120 50% 20% / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)


class TestNull(util.ColorAsserts, unittest.TestCase):
    """Test Null cases."""

    def test_null_input(self):
        """Test null input."""

        c = Color('hwb', [NaN, 0.1, 0.2], 1)
        self.assertTrue(c.is_nan('hue'))

    def test_auto_null(self):
        """Test auto null."""

        c = Color('hwb(120 100% 0% / 1)')
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
