"""Test utilities."""
import unittest
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


    def test_formatting_string(self):
        """Test string formatting case."""

        self.assertEqual(
            util.fmt_float(9.345678939171937490173947397373e3, 15, 'decimal'),
            '9345.678939171938'
        )
