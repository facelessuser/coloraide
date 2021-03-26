"""Test LCH library."""
import unittest
from . import util
from coloraide.css import Color


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
        color = "color(lch 20 10 130)"

        self.assertEqual(Color(color).to_string(**args), 'color(lch 20 10 130)')

        color = "color(lch 20% 10 130 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(lch 20 10 130 / 0.5)')

        color = "color(lch 20% 10 130 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(lch 20 10 130 / 0.5)')

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

        color = "lch(20%, 10, 130, 0.2)"
        lch = Color(color)
        self.assertEqual("lch(20%, 10, 130, 0.2)", lch.to_string(**args))

        args["comma"] = False

        color = "lch(20% 10 130 / 0.2)"
        lch = Color(color)
        self.assertEqual("lch(20% 10 130 / 0.2)", lch.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(lch 20.1234567% 10.1234567 130.1234567)'
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
            Color('color(lch -20% 20 120)').to_string(),
            'lch(-20% 20 120)'
        )

        self.assertEqual(
            Color('color(lch -20% 20 120)').to_string(fit="clip"),
            'lch(-20% 20 120)'
        )

        self.assertEqual(
            Color('color(lch -20% 20 120)').to_string(fit=False),
            'lch(-20% 20 120)'
        )
