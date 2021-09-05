"""Test ICtCp library."""
import unittest
from . import util
from coloraide import Color


class TestICtCpInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test ICtCp."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("ictcp", [1, 0.5, 0.5]), Color('color(--ictcp 100% 0.5 0.5)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("ictcp", [1, 0.5, 0.5])), Color('color(--ictcp 100% 0.5 0.5)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--ictcp 1 0.2 -0.3)"

        self.assertEqual(Color(color).to_string(**args), 'color(--ictcp 1 0.2 -0.3)')

        color = "color(--ictcp 1 0.2 -0.3 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--ictcp 1 0.2 -0.3 / 0.5)')

        color = "color(--ictcp 100% 0.2 -0.3 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--ictcp 1 0.2 -0.3 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(--ictcp 1 0.2 -0.3 / 0.5)"
        ictcp = Color(color)
        self.assertEqual("color(--ictcp 1 0.2 -0.3)", ictcp.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(--ictcp 1 0.2 -0.3 / 100%)"
        ictcp = Color(color)
        self.assertEqual("color(--ictcp 1 0.2 -0.3 / 1)", ictcp.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--ictcp 0.123456 0.123456 -0.123456)'
        self.assertEqual(Color(color).to_string(), 'color(--ictcp 0.12346 0.12346 -0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(--ictcp 0.123 0.123 -0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(--ictcp 0 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(--ictcp 0.12345599999999999629718416827017790637910366058349609 0.12345599999999999629718416827017790637910366058349609 -0.12345599999999999629718416827017790637910366058349609)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--ictcp 2 0.6 -0.6)').to_string(),
            'color(--ictcp 2 0.6 -0.6)'
        )

        self.assertEqual(
            Color('color(--ictcp 2 0.6 -0.6)').to_string(fit="clip"),
            'color(--ictcp 2 0.6 -0.6)'
        )

        self.assertEqual(
            Color('color(--ictcp 2 0.6 -0.6)').to_string(fit=False),
            'color(--ictcp 2 0.6 -0.6)'
        )


class TestICtCpProperties(util.ColorAsserts, unittest.TestCase):
    """Test ICtCp."""

    def test_i(self):
        """Test `i`."""

        c = Color('color(--ictcp 1 0.2 -0.3 / 1)')
        self.assertEqual(c.i, 1)
        c.i = 0.2
        self.assertEqual(c.i, 0.2)

    def test_ct(self):
        """Test `ct`."""

        c = Color('color(--ictcp 1 0.2 -0.3 / 1)')
        self.assertEqual(c.ct, 0.2)
        c.ct = 0.1
        self.assertEqual(c.ct, 0.1)

    def test_cp(self):
        """Test `cp`."""

        c = Color('color(--ictcp 1 0.2 -0.3 / 1)')
        self.assertEqual(c.cp, -0.3)
        c.cp = 0.1
        self.assertEqual(c.cp, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--ictcp 1 0.2 -0.3 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)
