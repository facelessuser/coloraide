"""Test Rec.2020 library."""
import unittest
from . import util
from coloraide import Color


class TestRec2020InputOutput(util.ColorAsserts, unittest.TestCase):
    """Test Rec.2020."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("rec2020", [1, 1, 1]), Color('color(rec2020 100% 100% 100%)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("rec2020", [1, 1, 1])), Color('color(rec2020 100% 100% 100%)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(rec2020 0.3 1 0.5)"

        self.assertEqual(Color(color).to_string(**args), 'color(rec2020 0.3 1 0.5)')

        color = "color(rec2020 0.3 1 0.5 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(rec2020 0.3 1 0.5 / 0.5)')

        color = "color(rec2020 30% 100% 50% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(rec2020 0.3 1 0.5 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(rec2020 0.3 1 0.5 / 0.2)"
        rec = Color(color)
        self.assertEqual("color(rec2020 0.3 1 0.5)", rec.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(rec2020 0.3 1 0.5 / 100%)"
        rec = Color(color)
        self.assertEqual("color(rec2020 0.3 1 0.5 / 1)", rec.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(rec2020 0.1234567 0.1234567 0.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(rec2020 0.12346 0.12346 0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(rec2020 0.123 0.123 0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(rec2020 0 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(rec2020 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531 0.12345670000000000254836152180359931662678718566894531)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(rec2020 2 -1 0)').to_string(),
            'color(rec2020 1 0.51431 0.38338)'
        )

        self.assertEqual(
            Color('color(rec2020 2 -1 0)').to_string(fit="clip"),
            'color(rec2020 1 0 0)'
        )

        self.assertEqual(
            Color('color(rec2020 2 -1 0)').to_string(fit=False),
            'color(rec2020 2 -1 0)'
        )


class TestRec2020Properties(util.ColorAsserts, unittest.TestCase):
    """Test Rec2020."""

    def test_red(self):
        """Test `red`."""

        c = Color('color(rec2020 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.red, 0.1)
        c.red = 0.2
        self.assertEqual(c.red, 0.2)

    def test_green(self):
        """Test `green`."""

        c = Color('color(rec2020 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.green, 0.2)
        c.green = 0.1
        self.assertEqual(c.green, 0.1)

    def test_blue(self):
        """Test `blue`."""

        c = Color('color(rec2020 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.blue, 0.3)
        c.blue = 0.1
        self.assertEqual(c.blue, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(rec2020 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)
