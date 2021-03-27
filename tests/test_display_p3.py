"""Test Display P3 library."""
import unittest
from . import util
from coloraide.css import Color


class TestDisplayP3InputOutput(util.ColorAsserts, unittest.TestCase):
    """Test Display P3."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("display-p3", [1, 1, 1]), Color('color(display-p3 100% 100% 100%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("display-p3", [1, 1, 1])), Color('color(display-p3 100% 100% 100%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(display-p3 0.3 1 0.5)"

        self.assertEqual(Color(color).to_string(**args), 'color(display-p3 0.3 1 0.5)')

        color = "color(display-p3 0.3 1 0.5 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(display-p3 0.3 1 0.5 / 0.5)')

        color = "color(display-p3 30% 100% 50% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(display-p3 0.3 1 0.5 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(display-p3 0.3 1 0.5 / 0.2)"
        p3 = Color(color)
        self.assertEqual("color(display-p3 0.3 1 0.5)", p3.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(display-p3 0.3 1 0.5 / 100%)"
        p3 = Color(color)
        self.assertEqual("color(display-p3 0.3 1 0.5 / 1)", p3.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(display-p3 0.1234567 0.1234567 0.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(display-p3 0.12346 0.12346 0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(display-p3 0.123 0.123 0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(display-p3 0 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(display-p3 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(display-p3 2 -1 0)').to_string(),
            'color(display-p3 1 0.60497 0.48289)'
        )

        self.assertEqual(
            Color('color(display-p3 2 -1 0)').to_string(fit="clip"),
            'color(display-p3 1 0 0)'
        )

        self.assertEqual(
            Color('color(display-p3 2 -1 0)').to_string(fit=False),
            'color(display-p3 2 -1 0)'
        )
