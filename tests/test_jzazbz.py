"""Test Jzazbz library."""
import unittest
from . import util
from coloraide import Color


class TestJzazbzInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test Jzazbz."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("jzazbz", [1, 0.5, 0.5]), Color('color(--jzazbz 100% 0.5 0.5)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("jzazbz", [1, 0.5, 0.5])), Color('color(--jzazbz 100% 0.5 0.5)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--jzazbz 1 0.2 -0.3)"

        self.assertEqual(Color(color).to_string(**args), 'color(--jzazbz 1 0.2 -0.3)')

        color = "color(--jzazbz 1 0.2 -0.3 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--jzazbz 1 0.2 -0.3 / 0.5)')

        color = "color(--jzazbz 100% 0.2 -0.3 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--jzazbz 1 0.2 -0.3 / 0.5)')

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "color(--jzazbz 1 0.2 -0.3 / 0.5)"
        jzazbz = Color(color)
        self.assertEqual("color(--jzazbz 1 0.2 -0.3)", jzazbz.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "color(--jzazbz 1 0.2 -0.3 / 100%)"
        jzazbz = Color(color)
        self.assertEqual("color(--jzazbz 1 0.2 -0.3 / 1)", jzazbz.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--jzazbz 0.123456 0.123456 -0.123456)'
        self.assertEqual(Color(color).to_string(), 'color(--jzazbz 0.12346 0.12346 -0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'color(--jzazbz 0.123 0.123 -0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'color(--jzazbz 0 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'color(--jzazbz 0.12345599999999999629718416827017790637910366058349609 0.12345599999999999629718416827017790637910366058349609 -0.12345599999999999629718416827017790637910366058349609)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('color(--jzazbz 2 0.6 -0.6)').to_string(),
            'color(--jzazbz 2 0.6 -0.6)'
        )

        self.assertEqual(
            Color('color(--jzazbz 2 0.6 -0.6)').to_string(fit="clip"),
            'color(--jzazbz 2 0.6 -0.6)'
        )

        self.assertEqual(
            Color('color(--jzazbz 2 0.6 -0.6)').to_string(fit=False),
            'color(--jzazbz 2 0.6 -0.6)'
        )


class TestJzazbzProperties(util.ColorAsserts, unittest.TestCase):
    """Test Jzazbz."""

    def test_jz(self):
        """Test `lightness`."""

        c = Color('color(--jzazbz 1 0.2 -0.3 / 1)')
        self.assertEqual(c.jz, 1)
        c.jz = 0.2
        self.assertEqual(c.jz, 0.2)

    def test_az(self):
        """Test `az`."""

        c = Color('color(--jzazbz 1 0.2 -0.3 / 1)')
        self.assertEqual(c.az, 0.2)
        c.az = 0.1
        self.assertEqual(c.az, 0.1)

    def test_bz(self):
        """Test `bz`."""

        c = Color('color(--jzazbz 1 0.2 -0.3 / 1)')
        self.assertEqual(c.bz, -0.3)
        c.bz = 0.1
        self.assertEqual(c.bz, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--jzazbz 1 0.2 -0.3 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)
