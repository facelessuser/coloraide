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
