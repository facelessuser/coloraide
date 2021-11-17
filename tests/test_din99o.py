"""Test DIN99o library."""
import unittest
from . import util
from coloraide import Color


class TestDIN99oInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test DIN99o."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("din99o", [20, 10, -30]), Color('color(--din99o 20% 10 -30)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("din99o", [20, 10, -30])), Color('color(--din99o 20% 10 -30)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--din99o 20% 10 -30)"

        self.assertEqual(Color(color).to_string(**args), 'color(--din99o 20 10 -30)')

        color = "color(--din99o 20% 10 -30 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--din99o 20 10 -30 / 0.5)')

        color = "color(--din99o 20% 10 -30 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--din99o 20 10 -30 / 0.5)')

    def test_percent(self):
        """Test that percents work properly."""

        color = "color(--din99o 20% 10 -30 / 100%)"
        din99o = Color(color)
        self.assertEqual("color(--din99o 20 10 -30)", din99o.to_string())

        color = "color(--din99o 20% 10 -30 / 20%)"
        din99o = Color(color)
        self.assertEqual("color(--din99o 20 10 -30 / 0.2)", din99o.to_string())

    def test_no_alpha(self):
        """Test no alpha."""

        color = "color(--din99o 20% 10 -30 / 0.2)"
        din99o = Color(color)
        self.assertEqual("color(--din99o 20 10 -30)", din99o.to_string(alpha=False))

    def test_force_alpha(self):
        """Test force alpha."""

        color = "color(--din99o 20% 10 -30 / 1)"
        din99o = Color(color)
        self.assertEqual("color(--din99o 20 10 -30 / 1)", din99o.to_string(alpha=True))

    def test_precision(self):
        """Test precision."""

        color = 'color(--din99o 20.1234567% 10.1234567 -30.1234567)'
        self.assertEqual(Color(color).to_string(), 'color(--din99o 20.123 10.123 -30.123)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(--din99o 20.1 10.1 -30.1)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(--din99o 20 10 -30)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(--din99o 20.12345669999999842048055143095552921295166015625 10.1234567000000001968373908312059938907623291015625 -30.12345669999999842048055143095552921295166015625)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--din99o -20% 180 -180)').to_string(),
            'color(--din99o -20 180 -180)'
        )

        self.assertEqual(
            Color('color(--din99o -20% 180 -180)').to_string(fit="clip"),
            'color(--din99o -20 180 -180)'
        )

        self.assertEqual(
            Color('color(--din99o -20% 180 -180)').to_string(fit=False),
            'color(--din99o -20 180 -180)'
        )


class TestDIN99oProperties(util.ColorAsserts, unittest.TestCase):
    """Test DIN99o."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--din99o 90% 50 -20 / 1)')
        self.assertEqual(c.lightness, 90)
        c.lightness = 80
        self.assertEqual(c.lightness, 80)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--din99o 90% 50 -20 / 1)')
        self.assertEqual(c.a, 50)
        c.a = 40
        self.assertEqual(c.a, 40)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--din99o 90% 50 -20 / 1)')
        self.assertEqual(c.b, -20)
        c.b = -10
        self.assertEqual(c.b, -10)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--din99o 90% 50 -20 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)
