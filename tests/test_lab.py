"""Test Lab library."""
import unittest
from . import util
from coloraide.css import Color


class TestLabInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test Lab."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("lab", [20, 10, -30]), Color('lab(20% 10 -30)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("lab", [20, 10, -30])), Color('lab(20% 10 -30)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(lab 20 10 -30)"

        self.assertEqual(Color(color).to_string(**args), 'color(lab 20 10 -30)')

        color = "color(lab 20% 10 -30 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(lab 20 10 -30 / 0.5)')

        color = "color(lab 20% 10 -30 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(lab 20 10 -30 / 0.5)')

    def test_comma(self):
        """Test comma input and comma output format."""

        args = {"comma": True}

        color = "lab(20%, 10, -30)"
        lab = Color(color)
        self.assertEqual(color, lab.to_string(**args))

        color = "lab(20%, 10, -30, 1)"
        lab = Color(color)
        self.assertEqual("lab(20%, 10, -30)", lab.to_string(**args))

        color = "lab(20%, 10, -30, 0.2)"
        lab = Color(color)
        self.assertEqual("lab(20%, 10, -30, 0.2)", lab.to_string(**args))

    def test_space(self):
        """Test space input and space output format."""

        args = {}

        color = "lab(20% 10 -30)"
        lab = Color(color)
        self.assertEqual(color, lab.to_string(**args))

        color = "lab(20% 10 -30 / 1)"
        lab = Color(color)
        self.assertEqual("lab(20% 10 -30)", lab.to_string(**args))

        color = "lab(20% 10 -30 / 0.2)"
        lab = Color(color)
        self.assertEqual(color, lab.to_string(**args))

    def test_percent(self):
        """Test that percents work properly."""

        args = {"comma": True}

        color = "lab(20%, 10, -30, 100%)"
        lab = Color(color)
        self.assertEqual("lab(20%, 10, -30)", lab.to_string(**args))

        color = "lab(20%, 10, -30, 20%)"
        lab = Color(color)
        self.assertEqual("lab(20%, 10, -30, 0.2)", lab.to_string(**args))

        args["comma"] = False

        color = "lab(20% 10 -30 / 100%)"
        lab = Color(color)
        self.assertEqual("lab(20% 10 -30)", lab.to_string(**args))

        color = "lab(20% 10 -30 / 20%)"
        lab = Color(color)
        self.assertEqual("lab(20% 10 -30 / 0.2)", lab.to_string(**args))

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"comma": True, "alpha": False}

        color = "lab(20%, 10, -30, 0.2)"
        lab = Color(color)
        self.assertEqual("lab(20%, 10, -30)", lab.to_string(**args))

        args["comma"] = False

        color = "lab(20% 10 -30 / 0.2)"
        lab = Color(color)
        self.assertEqual("lab(20% 10 -30)", lab.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"comma": True, "alpha": True}

        color = "lab(20%, 10, -30, 1)"
        lab = Color(color)
        self.assertEqual("lab(20%, 10, -30, 1)", lab.to_string(**args))

        args["comma"] = False

        color = "lab(20% 10 -30 / 1)"
        lab = Color(color)
        self.assertEqual("lab(20% 10 -30 / 1)", lab.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(lab 20.1234567% 10.1234567 -30.1234567)'
        self.assertEqual(Color(color).to_string(), 'lab(20.123% 10.123 -30.123)')
        self.assertEqual(Color(color).to_string(precision=3), 'lab(20.1% 10.1 -30.1)')
        self.assertEqual(Color(color).to_string(precision=0), 'lab(20% 10 -30)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'lab(20.12345669999999842048055143095552921295166015625% 10.1234567000000001968373908312059938907623291015625 -30.12345669999999842048055143095552921295166015625)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(lab -20% 180 -180)').to_string(),
            'lab(-20% 180 -180)'
        )

        self.assertEqual(
            Color('color(lab -20% 180 -180)').to_string(fit="clip"),
            'lab(-20% 180 -180)'
        )

        self.assertEqual(
            Color('color(lab -20% 180 -180)').to_string(fit=False),
            'lab(-20% 180 -180)'
        )
