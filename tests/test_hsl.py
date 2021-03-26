"""Test HSL library."""
import unittest
from . import util
from coloraide.css import Color


class TestHSLInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test SRGB."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("hsl", [20, 100, 75]), Color('hsl(20 100% 75%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("hsl", [20, 100, 75])), Color('hsl(20 100% 75%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(hsl 20 100 75)"

        self.assertEqual(Color(color).to_string(**args), 'color(hsl 20 100 75)')

        color = "color(hsl 20 100 75 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(hsl 20 100 75 / 0.5)')

        color = "color(hsl 20 100% 75% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(hsl 20 100 75 / 0.5)')

    def test_comma(self):
        """Test comma input and comma output format."""

        args = {"comma": True}

        color = "hsl(20, 100%, 75%)"
        hsl = Color(color)
        self.assertEqual(color, hsl.to_string(**args))

        color = "hsl(20, 100%, 75%, 1)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        color = "hsl(20, 100%, 75%, 0.2)"
        hsl = Color(color)
        self.assertEqual("hsla(20, 100%, 75%, 0.2)", hsl.to_string(**args))

    def test_space(self):
        """Test space input and space output format."""

        args = {}

        color = "hsl(20 100% 75%)"
        hsl = Color(color)
        self.assertEqual(color, hsl.to_string(**args))

        color = "hsl(20 100% 75% / 1)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

        color = "hsl(20 100% 75% / 0.2)"
        hsl = Color(color)
        self.assertEqual(color, hsl.to_string(**args))

    def test_alias(self):
        """Test that `hsla` is an alias for `hsl`."""

        args = {"comma": True}

        color = "hsla(20, 100%, 75%)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 1)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 0.5)"
        hsl = Color(color)
        self.assertEqual("hsla(20, 100%, 75%, 0.5)", hsl.to_string(**args))

        args["comma"] = False

        color = "hsla(20, 100%, 75%)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 1)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 0.5)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75% / 0.5)", hsl.to_string(**args))

    def test_percent(self):
        """Test that percents work properly."""

        args = {"comma": True}

        color = "hsla(20, 100%, 75%, 100%)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        color = "hsla(20, 100%, 75%, 20%)"
        hsl = Color(color)
        self.assertEqual("hsla(20, 100%, 75%, 0.2)", hsl.to_string(**args))

        args["comma"] = False

        color = "hsl(20 100% 75% / 100%)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

        color = "hsl(20 100% 75% / 20%)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75% / 0.2)", hsl.to_string(**args))

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"comma": True, "alpha": False}

        color = "hsla(20, 100%, 75%, 0.2)"
        hsl = Color(color)
        self.assertEqual("hsl(20, 100%, 75%)", hsl.to_string(**args))

        args["comma"] = False

        color = "hsl(20 100% 75% / 0.2)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75%)", hsl.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"comma": True, "alpha": True}

        color = "hsla(20, 100%, 75%, 0.2)"
        hsl = Color(color)
        self.assertEqual("hsla(20, 100%, 75%, 0.2)", hsl.to_string(**args))

        args["comma"] = False

        color = "hsl(20 100% 75% / 0.2)"
        hsl = Color(color)
        self.assertEqual("hsl(20 100% 75% / 0.2)", hsl.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(hsl 20.1234567 50.1234567% 50.1234567%)'
        self.assertEqual(Color(color).to_string(), 'hsl(20.123 50.123% 50.123%)')
        self.assertEqual(Color(color).to_string(precision=3), 'hsl(20.1 50.1% 50.1%)')
        self.assertEqual(Color(color).to_string(precision=0), 'hsl(20 50% 50%)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'hsl(20.12345669999999842048055143095552921295166015625 50.12345669999999842048055143095552921295166015625% 50.12345669999999842048055143095552921295166015625%)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(hsl 20 150 75)').to_string(),
            'hsl(19.92 100% 76.269%)'
        )

        self.assertEqual(
            Color('color(hsl 20 150 75)').to_string(fit="clip"),
            'hsl(20 100% 75%)'
        )

        self.assertEqual(
            Color('color(hsl 20 150 75)').to_string(fit=False),
            'hsl(20 150% 75%)'
        )
