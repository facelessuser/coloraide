"""Test A98 RGB library."""
import unittest
from . import util
from coloraide.css import Color


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
            'color(a98-rgb 0.98872 0.86537 0.85054)'
        )

        self.assertEqual(
            Color('color(a98-rgb 2 -1 0)').to_string(fit="clip"),
            'color(a98-rgb 1 0 0)'
        )

        self.assertEqual(
            Color('color(a98-rgb 2 -1 0)').to_string(fit=False),
            'color(a98-rgb 2 -1 0)'
        )
