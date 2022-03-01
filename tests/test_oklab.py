"""Test Oklab library."""
import unittest
from . import util
from coloraide import Color as Color


class TestOklabInputOutput(util.ColorAsserts, unittest.TestCase):
    """Test Oklab."""

    def test_input_raw(self):
        """Test raw input."""

        self.assertColorEqual(Color("oklab", [1, 0.5, 0.5]), Color('oklab(100% 0.5 0.5)'))

    def test_color_class(self):
        """Test raw input."""

        self.assertColorEqual(Color(Color("oklab", [1, 0.5, 0.5])), Color('oklab(100% 0.5 0.5)'))

    def test_color(self):
        """Test color input/output format."""

        args = {"color": True}
        color = "color(--oklab 1 0.2 -0.3)"

        self.assertEqual(Color(color).to_string(**args), 'color(--oklab 1 0.2 -0.3)')

        color = "color(--oklab 1 0.2 -0.3 / 0.5)"
        self.assertEqual(Color(color).to_string(**args), 'color(--oklab 1 0.2 -0.3 / 0.5)')

        color = "color(--oklab 100% 0.2 -0.3 / 50%)"
        self.assertEqual(Color(color).to_string(**args), 'color(--oklab 1 0.2 -0.3 / 0.5)')

    def test_space(self):
        """Test space input and space output format."""

        args = {}

        color = "oklab(20% 0.1 -0.3)"
        lab = Color(color)
        self.assertEqual(color, lab.to_string(**args))

        color = "oklab(20% 0.1 -0.3 / 1)"
        lab = Color(color)
        self.assertEqual("oklab(20% 0.1 -0.3)", lab.to_string(**args))

        color = "oklab(20% 0.1 -0.3 / 0.2)"
        lab = Color(color)
        self.assertEqual(color, lab.to_string(**args))

    def test_percent(self):
        """Test that percents work properly."""

        args = {}

        color = "oklab(20% 0.1 -0.3 / 100%)"
        lab = Color(color)
        self.assertEqual("oklab(20% 0.1 -0.3)", lab.to_string(**args))

        color = "oklab(20% 0.1 -0.3 / 20%)"
        lab = Color(color)
        self.assertEqual("oklab(20% 0.1 -0.3 / 0.2)", lab.to_string(**args))

    def test_no_alpha(self):
        """Test no alpha."""

        args = {"alpha": False}

        color = "oklab(100% 0.2 -0.3 / 0.5)"
        oklab = Color(color)
        self.assertEqual("oklab(100% 0.2 -0.3)", oklab.to_string(**args))

    def test_force_alpha(self):
        """Test force alpha."""

        args = {"alpha": True}

        color = "oklab(100% 0.2 -0.3 / 100%)"
        oklab = Color(color)
        self.assertEqual("oklab(100% 0.2 -0.3 / 1)", oklab.to_string(**args))

    def test_precision(self):
        """Test precision."""

        color = 'color(--oklab 0.123456 0.123456 -0.123456)'
        self.assertEqual(Color(color).to_string(), 'oklab(12.346% 0.12346 -0.12346)')
        self.assertEqual(Color(color).to_string(precision=3), 'oklab(12.3% 0.123 -0.123)')
        self.assertEqual(Color(color).to_string(precision=0), 'oklab(12% 0 0)')
        self.assertEqual(
            Color(color).to_string(precision=-1),
            'oklab(12.3455999999999992411403582082130014896392822265625% 0.12345599999999999629718416827017790637910366058349609 -0.12345599999999999629718416827017790637910366058349609)'  # noqa:  E501
        )

    def test_fit(self):
        """Test fit."""

        self.assertEqual(
            Color('oklab(200% 0.6 -0.6)').to_string(),
            'oklab(200% 0.6 -0.6)'
        )

        self.assertEqual(
            Color('oklab(200% 0.6 -0.6)').to_string(fit="clip"),
            'oklab(200% 0.6 -0.6)'
        )

        self.assertEqual(
            Color('oklab(200% 0.6 -0.6)').to_string(fit=False),
            'oklab(200% 0.6 -0.6)'
        )


class TestOklabProperties(util.ColorAsserts, unittest.TestCase):
    """Test Oklab."""

    def test_lightness(self):
        """Test `lightness`."""

        c = Color('color(--oklab 1 0.2 -0.3 / 1)')
        self.assertEqual(c.lightness, 1)
        c.lightness = 0.2
        self.assertEqual(c.lightness, 0.2)

    def test_a(self):
        """Test `a`."""

        c = Color('color(--oklab 1 0.2 -0.3 / 1)')
        self.assertEqual(c.a, 0.2)
        c.a = 0.1
        self.assertEqual(c.a, 0.1)

    def test_b(self):
        """Test `b`."""

        c = Color('color(--oklab 1 0.2 -0.3 / 1)')
        self.assertEqual(c.b, -0.3)
        c.b = 0.1
        self.assertEqual(c.b, 0.1)

    def test_alpha(self):
        """Test `alpha`."""

        c = Color('color(--oklab 1 0.2 -0.3 / 1)')
        self.assertEqual(c.alpha, 1)
        c.alpha = 0.5
        self.assertEqual(c.alpha, 0.5)
