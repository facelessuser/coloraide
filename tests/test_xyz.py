"""Test XYZ D65 library."""
import unittest
from . import util
from coloraide import Color


class TestXYZD65InputOutput(util.ColorAsserts, unittest.TestCase):
    """Test XYZ D65."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("xyz", [1, 1, 1]), Color('color(xyz 1 1 1)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("xyz", [1, 1, 1])), Color('color(xyz 1 1 1)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(xyz 0.3 1 0.5)"

        self.assertEqual(Color(color).to_string(**args), 'color(xyz 0.3 1 0.5)')

        color = "color(xyz 0.3 1 0.5 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(xyz 0.3 1 0.5 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(xyz 0.3 1 0.5 / 0.2)"
        xyzd65 = Color(color)
        self.assertEqual("color(xyz 0.3 1 0.5)", xyzd65.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(xyz 0.3 1 0.5 / 100%)"
        xyzd65 = Color(color)
        self.assertEqual("color(xyz 0.3 1 0.5 / 1)", xyzd65.to_string(**args))

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


class TestXYZD65Properties(util.ColorAsserts, unittest.TestCase):
    """Test XYZ D65."""

    def test_x(self):
        """Test `x`."""

        c = Color('color(xyz 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.x, 0.1)
        c.x = 0.2
        self.assertEqual(c.x, 0.2)

    def test_y(self):
        """Test `y`."""

        c = Color('color(xyz 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.y, 0.2)
        c.y = 0.1
        self.assertEqual(c.y, 0.1)

    def test_z(self):
        """Test `z`."""

        c = Color('color(xyz 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.z, 0.3)
        c.z = 0.1
        self.assertEqual(c.z, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(xyz 0.1 0.2 0.3 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)
