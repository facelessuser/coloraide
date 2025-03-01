"""Test easings."""
import math
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

    def test_difficult_case(self):
        """
        Previously, difficult case.

        When we used Newton's method, this required a fallback to bisect.
        We no longer use Newton's method with a fallback to bisection, so
        this case is no more difficult than any other case as we now
        use Cardano's method.
        """

        ease_in_out_expo = cubic_bezier(1.000, 0.000, 0.000, 1.000)
        self.assertEqual(ease_in_out_expo(0.43), 0.14556294236116715)

    def test_fail(self):
        """Force a failure to calculate a Bezier."""

        ease_in_out_expo = cubic_bezier(1.000, 0.000, 0.000, 1.000)
        with self.assertRaises(ValueError):
            ease_in_out_expo(math.nan)


class TestEasingMethods(unittest.TestCase):
    """Test different easing methods."""

    def ease(self, method, expected):
        """Perform easing test."""

        i = -0.5
        results = []
        while i < 1.6:
            results.append(method(i))
            i += 0.1
        self.assertTrue(all(math.isclose(a, b, rel_tol=1e-14, abs_tol=1e-15) for a, b in zip(results, expected)))

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
                0.2952443342678225,
                0.5133151609733584,
                0.6825405059781395,
                0.802403387584857,
                0.8852293098761204,
                0.94076461429764,
                0.9756253556235666,
                0.9943164774845565,
                1.0000000000000002,
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
                0.017026609651562864,
                0.06228200013673216,
                0.12957676084535247,
                0.2148609387528933,
                0.3153568125725391,
                0.4291197692963168,
                0.5548140325286626,
                0.6916339333193126,
                0.8394278457624664,
                0.9999999999999996,
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
                0.16057215423753335,
                0.3083660666806867,
                0.445185967471337,
                0.5708802307036829,
                0.6846431874274607,
                0.7851390612471065,
                0.8704232391546475,
                0.9377179998632676,
                0.9829733903484368,
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
                0.019722453548311168,
                0.08165985626589742,
                0.1873959067053125,
                0.33188387009764614,
                0.5,
                0.668116129902354,
                0.8126040932946875,
                0.9183401437341026,
                0.9802775464516886,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0
            ]
        )
