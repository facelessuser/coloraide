"""Test easings."""
import unittest
from coloraide import ease, ease_in, ease_out, ease_in_out, linear, cubic_bezier


class TestCubicBezier(unittest.TestCase):
    """Test Cubic Bezier specific cases."""

    def test_x_range(self):
        """Test that X range is constrained to 0 - 1."""

        with self.assertRaises(ValueError):
            cubic_bezier(1.2, 0, 1, 1)

        with self.assertRaises(ValueError):
            cubic_bezier(-0.2, 0, 1, 1)

        with self.assertRaises(ValueError):
            cubic_bezier(0, 0, 1.2, 1)

        with self.assertRaises(ValueError):
            cubic_bezier(0, 0, -0.2, 1)

    def test_bisect(self):
        """
        Test bisect method.

        Normally, Newton's method finds an answer pretty quick,
        but if we test long enough, we'll find a result that
        doesn't resolve within our limits. When this happens,
        bisect method takes over.
        """

        ease_in_out_expo = cubic_bezier(1.000, 0.000, 0.000, 1.000)
        self.assertEqual(ease_in_out_expo(0.43), 0.14556343840627634)


class TestEasingMethods(unittest.TestCase):
    """Test different easing methods."""

    def ease(self, method, expected):
        """Perform easing test."""

        i = -0.5
        results = []
        while i < 1.6:
            results.append(method(i))
            i += 0.1
        self.assertEqual(results, expected)

    def test_linear(self):
        """Test linear."""

        self.ease(
            linear,
            [
                -0.5,
                -0.4,
                -0.30000000000000004,
                -0.20000000000000004,
                -0.10000000000000003,
                -2.7755575615628914e-17,
                0.09999999999999998,
                0.19999999999999998,
                0.3,
                0.4,
                0.5,
                0.6,
                0.7,
                0.7999999999999999,
                0.8999999999999999,
                0.9999999999999999,
                1.0999999999999999,
                1.2,
                1.3,
                1.4000000000000001,
                1.5000000000000002
            ]
        )

    def test_ease(self):
        """Test ease."""

        self.ease(
            ease,
            [
                -0.2,
                -0.16000000000000003,
                -0.12000000000000002,
                -0.08000000000000002,
                -0.040000000000000015,
                -1.1102230246251566e-17,
                0.09479630571604325,
                0.29524433426782254,
                0.5133151609733584,
                0.6825405059781395,
                0.802403387584857,
                0.8852293098761204,
                0.9407646142976396,
                0.9756253556235668,
                0.9943164774845563,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0
            ]
        )

    def test_ease_in(self):
        """Test ease in."""

        self.ease(
            ease_in,
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.017026609651562934,
                0.06228200013673226,
                0.12957676084535252,
                0.21486093875289342,
                0.3153568125725393,
                0.4291197692963171,
                0.5548140325286628,
                0.6916339333193129,
                0.8394278457624664,
                0.9999999999999998,
                1.172413793103448,
                1.3448275862068964,
                1.5172413793103448,
                1.6896551724137931,
                1.8620689655172415
            ]
        )

    def test_ease_out(self):
        """Test ease out."""

        self.ease(
            ease_out,
            [
                -0.8620689655172414,
                -0.6896551724137931,
                -0.517241379310345,
                -0.34482758620689663,
                -0.17241379310344834,
                -4.785444071660158e-17,
                0.16057215423753346,
                0.3083660666806869,
                0.445185967471337,
                0.5708802307036829,
                0.6846431874274606,
                0.7851390612471066,
                0.8704232391546475,
                0.9377179998632681,
                0.982973390348437,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0
            ]
        )

    def test_ease_in_out(self):
        """Test ease in/out."""

        self.ease(
            ease_in_out,
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.01972245354831119,
                0.08165985626589745,
                0.18739590670531256,
                0.33188387009764614,
                0.5,
                0.668116129902354,
                0.8126040932946875,
                0.9183401437341026,
                0.9802775464516889,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0
            ]
        )
