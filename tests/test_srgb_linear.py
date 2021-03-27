"""Test SRGB Linear library."""
import unittest
from . import util
from coloraide.css import Color


class TestSRGBLinearInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test SRGB Linear."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("srgb-linear", [1, 1, 1]), Color('color(srgb-linear 100% 100% 100%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("srgb-linear", [1, 1, 1])), Color('color(srgb-linear 100% 100% 100%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(srgb-linear 0.3 1 0.5)"

        self.assertEqual(Color(color).to_string(**args), 'color(srgb-linear 0.3 1 0.5)')

        color = "color(srgb-linear 0.3 1 0.5 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(srgb-linear 0.3 1 0.5 / 0.5)')

        color = "color(srgb-linear 30% 100% 50% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(srgb-linear 0.3 1 0.5 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(srgb-linear 0.3 1 0.5 / 0.2)"
        srgbl = Color(color)
        self.assertEqual("color(srgb-linear 0.3 1 0.5)", srgbl.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(srgb-linear 0.3 1 0.5 / 100%)"
        srgbl = Color(color)
        self.assertEqual("color(srgb-linear 0.3 1 0.5 / 1)", srgbl.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(srgb-linear 0.1234567 0.1234567 0.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(srgb-linear 0.12346 0.12346 0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(srgb-linear 0.123 0.123 0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(srgb-linear 0 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(srgb-linear 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(srgb-linear 2 0 0)').to_string(),
            'color(srgb-linear 0.98363 0.29954 0.18756)'
        )

        self.assertEqual(
            Color('color(srgb-linear 2 0 0)').to_string(fit="clip"),
            'color(srgb-linear 1 0 0)'
        )

        self.assertEqual(
            Color('color(srgb-linear 2 0 0)').to_string(fit=False),
            'color(srgb-linear 2 0 0)'
        )
