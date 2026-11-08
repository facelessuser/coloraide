"""Test utilities."""
import unittest
import math
from coloraide import util, NaN


class TestUtil(unittest.TestCase):
    """Test utilities."""

    def test_compare_coords(self):
        """Test coordinate comparison."""

        self.assertTrue(util.cmp_coords([1, 2, 3], [1, 2, 3]))
        self.assertTrue(util.cmp_coords([1, NaN, 3], [1, NaN, 3]))
        self.assertFalse(util.cmp_coords([1, 3, 2], [1, 2, 3]))
        self.assertFalse(util.cmp_coords([1, 2, NaN], [1, NaN, 3]))
        self.assertFalse(util.cmp_coords([1, 2, 3, 4], [1, 2, 3]))


    def test_constrain_hue(self):
        """Test constraining hues to the range [0, 360)."""

        self.assertEqual(util.constrain_hue(0.0), 0.0)
        self.assertEqual(util.constrain_hue(359.5), 359.5)
        self.assertEqual(util.constrain_hue(360.0), 0.0)
        self.assertEqual(util.constrain_hue(725.0), 5.0)
        self.assertEqual(util.constrain_hue(-1.0), 359.0)
        self.assertTrue(math.isnan(util.constrain_hue(NaN)))

    def test_constrain_hue_tiny_negative(self):
        """Test that a very small negative hue is constrained to 0 and not rounded up to 360."""

        # A plain modulo will round `-1e-17` up to exactly `360.0`
        self.assertEqual(-1e-17 % 360, 360.0)
        self.assertEqual(util.constrain_hue(-1e-17), 0.0)
        self.assertEqual(util.constrain_hue(-1e-300), 0.0)
        self.assertEqual(util.constrain_hue(-1e-17 - 360), 0.0)

    def test_constrain_hue_max_hue(self):
        """Test constraining hues with a different full turn, such as radians."""

        self.assertEqual(util.constrain_hue(0.5, 1.0), 0.5)
        self.assertEqual(util.constrain_hue(1.0, 1.0), 0.0)
        self.assertEqual(util.constrain_hue(-0.25, 1.0), 0.75)
        self.assertEqual(util.constrain_hue(math.tau, math.tau), 0.0)
        self.assertEqual(util.constrain_hue(-1e-17, math.tau), 0.0)
        self.assertEqual(util.constrain_hue(-1e-17, 1.0), 0.0)
        self.assertTrue(math.isnan(util.constrain_hue(NaN, math.tau)))

    def test_formatting_string(self):
        """Test string formatting case."""

        self.assertEqual(
            util.fmt_float(9.345678939171937490173947397373e3, 15, 'decimal'),
            '9345.678939171938'
        )
