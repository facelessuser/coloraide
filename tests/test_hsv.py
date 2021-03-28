"""Test HSV library."""
import unittest
from . import util
from coloraide.css import Color


class TestHSVInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test HSV."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("hsv", [20, 100, 75]), Color('color(hsv 20 100 75)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("hsv", [20, 100, 75])), Color('color(hsv 20 100 75)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(hsv 20 100 75)"

        self.assertEqual(Color(color).to_string(**args), 'color(hsv 20 100 75)')

        color = "color(hsv 20 100 75 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(hsv 20 100 75 / 0.5)')

        color = "color(hsv 20 100% 75% / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(hsv 20 100 75 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(hsv 20 100 75 0.2)"
        hsv = Color(color)
        self.assertEqual("color(hsv 20 100 75)", hsv.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(hsv 20 100 75 / 1)"
        hsv = Color(color)
        self.assertEqual("color(hsv 20 100 75 / 1)", hsv.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(hsv 20.1234567 50.1234567 50.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(hsv 20.123 50.123 50.123)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(hsv 20.1 50.1 50.1)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(hsv 20 50 50)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(hsv 20.12345669999999842048055143095552921295166015625 50.12345669999999842048055143095552921295166015625 50.12345669999999842048055143095552921295166015625)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(hsv 20 150 75)').to_string(),
            'color(hsv 40.491 100 50.527)'
        )

        self.assertEqual(
            Color('color(hsv 20 150 75)').to_string(fit="clip"),
            'color(hsv 20 100 75)'
        )

        self.assertEqual(
            Color('color(hsv 20 150 75)').to_string(fit=False),
            'color(hsv 20 150 75)'
        )
