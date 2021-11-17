"""Test Luv D65 library."""
import unittest
from . import util
from coloraide import Color


class TestLuvD65InputOutput(util.ColorAsserts, unittest.TestCase):
    """Test Luv."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("luv-d65", [20, 10, -30]), Color('color(--luv-d65 20% 10 -30)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("luv-d65", [20, 10, -30])), Color('color(--luv-d65 20% 10 -30)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--luv-d65 20% 10 -30)"

        self.assertEqual(Color(color).to_string(**args), 'color(--luv-d65 20 10 -30)')

        color = "color(--luv-d65 20% 10 -30 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--luv-d65 20 10 -30 / 0.5)')

        color = "color(--luv-d65 20% 10 -30 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--luv-d65 20 10 -30 / 0.5)')

    def test_percent(self):
        """Test that percents work properly."""

        color = "color(--luv-d65 20% 10 -30 / 100%)"
        luv = Color(color)
        self.assertEqual("color(--luv-d65 20 10 -30)", luv.to_string())

        color = "color(--luv-d65 20% 10 -30 / 20%)"
        luv = Color(color)
        self.assertEqual("color(--luv-d65 20 10 -30 / 0.2)", luv.to_string())

    def test_no_alpha(self):
        """Test no alpha."""

        color = "color(--luv-d65 20% 10 -30 / 0.2)"
        luv = Color(color)
        self.assertEqual("color(--luv-d65 20 10 -30)", luv.to_string(alpha=False))

    def test_force_alpha(self):
        """Test force alpha."""

        color = "color(--luv-d65 20% 10 -30 / 1)"
        luv = Color(color)
        self.assertEqual("color(--luv-d65 20 10 -30 / 1)", luv.to_string(alpha=True))

    def test_precision(self):
        """Test precision."""

        color = 'color(--luv-d65 20.1234567% 10.1234567 -30.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(--luv-d65 20.123 10.123 -30.123)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(--luv-d65 20.1 10.1 -30.1)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(--luv-d65 20 10 -30)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(--luv-d65 20.12345669999999842048055143095552921295166015625 10.1234567000000001968373908312059938907623291015625 -30.12345669999999842048055143095552921295166015625)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--luv-d65 -20% 180 -180)').to_string(),
            'color(--luv-d65 -20 180 -180)'
        )

        self.assertEqual(
            Color('color(--luv-d65 -20% 180 -180)').to_string(fit="clip"),
            'color(--luv-d65 -20 180 -180)'
        )

        self.assertEqual(
            Color('color(--luv-d65 -20% 180 -180)').to_string(fit=False),
            'color(--luv-d65 -20 180 -180)'
        )


class TestLuvD65Properties(util.ColorAsserts, unittest.TestCase):
    """Test Luv D65."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--luv-d65 90% 50 -20 / 1)')
        self.assertEqual(c.lightness, 90)
        c.lightness = 80
        self.assertEqual(c.lightness, 80)

    def test_u(self):
        """Test `u`."""

        c = Color('color(--luv-d65 90% 50 -20 / 1)')
        self.assertEqual(c.u, 50)
        c.u = 40
        self.assertEqual(c.u, 40)

    def test_v(self):
        """Test `v`."""

        c = Color('color(--luv-d65 90% 50 -20 / 1)')
        self.assertEqual(c.v, -20)
        c.v = -10
        self.assertEqual(c.v, -10)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--luv-d65 90% 50 -20 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)
