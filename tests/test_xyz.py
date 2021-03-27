"""Test XYZ library."""
import unittest
from . import util
from coloraide.css import Color


class TestXYZInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test XYZ."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("xyz", [1, 1, 1]), Color('color(xyz 100% 100% 100%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("xyz", [1, 1, 1])), Color('color(xyz 100% 100% 100%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(xyz 0.3 1 0.5)"

        self.assertEqual(Color(color).to_string(**args), 'color(xyz 0.3 1 0.5)')

        color = "color(xyz 0.3 1 0.5 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(xyz 0.3 1 0.5 / 0.5)')

        color = "color(xyz 30% 100% 50% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(xyz 0.3 1 0.5 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(xyz 0.3 1 0.5 / 0.2)"
        xyz = Color(color)
        self.assertEqual("color(xyz 0.3 1 0.5)", xyz.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(xyz 0.3 1 0.5 / 100%)"
        xyz = Color(color)
        self.assertEqual("color(xyz 0.3 1 0.5 / 1)", xyz.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(xyz 0.1234567 0.1234567 0.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(xyz 0.12346 0.12346 0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(xyz 0.123 0.123 0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(xyz 0 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(xyz 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(xyz 2 -1 0)').to_string(),
            'color(xyz 2 -1 0)'
        )

        self.assertEqual(
            Color('color(xyz 2 -1 0)').to_string(fit="clip"),
            'color(xyz 2 -1 0)'
        )

        self.assertEqual(
            Color('color(xyz 2 -1 0)').to_string(fit=False),
            'color(xyz 2 -1 0)'
        )
