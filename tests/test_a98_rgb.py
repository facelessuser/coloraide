"""Test A98 RGB library."""
import unittest
from . import util
from coloraide import Color


class TestA98RGBInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test A98 RGB."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("a98-rgb", [1, 1, 1]), Color('color(a98-rgb 100% 100% 100%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("a98-rgb", [1, 1, 1])), Color('color(a98-rgb 100% 100% 100%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(a98-rgb 0.3 1 0.5)"

        self.assertEqual(Color(color).to_string(**args), 'color(a98-rgb 0.3 1 0.5)')

        color = "color(a98-rgb 0.3 1 0.5 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(a98-rgb 0.3 1 0.5 / 0.5)')

        color = "color(a98-rgb 30% 100% 50% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(a98-rgb 0.3 1 0.5 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(a98-rgb 0.3 1 0.5 / 0.2)"
        a98 = Color(color)
        self.assertEqual("color(a98-rgb 0.3 1 0.5)", a98.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(a98-rgb 0.3 1 0.5 / 100%)"
        a98 = Color(color)
        self.assertEqual("color(a98-rgb 0.3 1 0.5 / 1)", a98.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(a98-rgb 0.1234567 0.1234567 0.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(a98-rgb 0.12346 0.12346 0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(a98-rgb 0.123 0.123 0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(a98-rgb 0 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(a98-rgb 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(a98-rgb 2 -1 0)').to_string(),
            'color(a98-rgb 1 0.84439 0.82433)'
        )

        self.assertEqual(
            Color('color(a98-rgb 2 -1 0)').to_string(fit="clip"),
            'color(a98-rgb 1 0 0)'
        )

        self.assertEqual(
            Color('color(a98-rgb 2 -1 0)').to_string(fit=False),
            'color(a98-rgb 2 -1 0)'
        )


class TestA98RGBProperties(util.ColorAsserts, unittest.TestCase):
    """Test A98 RGB."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(a98-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.red, 0.1)
        c.red = 0.2
        self.assertEqual(c.red, 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(a98-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.green, 0.2)
        c.green = 0.1
        self.assertEqual(c.green, 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(a98-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.blue, 0.3)
        c.blue = 0.1
        self.assertEqual(c.blue, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(a98-rgb 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)
