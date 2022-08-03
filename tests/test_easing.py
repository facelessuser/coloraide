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
                0.09479499730150562,
                0.29524455671683436,
                0.5133153550526887,
                0.682540506014571,
                0.8024033876954126,
                0.8852293098934654,
                0.9407646142979406,
                0.9756253688544969,
                0.994316477509521,
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
                0.017026610765605858,
                0.06228200132556937,
                0.12957675643854266,
                0.2148609387527464,
                0.31535681250589304,
                0.4291197633963204,
                0.5548137855026869,
                0.6916339332833448,
                0.8394277819903986,
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
                0.16057221800960114,
                0.30836606671665506,
                0.44518621449731305,
                0.5708802366036794,
                0.6846431874941069,
                0.7851390612472536,
                0.8704232435614574,
                0.9377179986744306,
                0.9829733892343944,
                0.9999999999999998,
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
                0.019722447263855625,
                0.08165982204916349,
                0.1873958911579092,
                0.33188386972039197,
                0.5,
                0.6681161302796081,
                0.8126041088420908,
                0.9183401779508362,
                0.9802775527361445,
                0.9999999999999998,
                1.0,
                1.0,
                1.0,
                1.0,
                1.0
            ]
        )
