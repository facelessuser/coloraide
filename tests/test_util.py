"""Test utilities."""
import unittest
import decimal
from coloraide import util, NaN


class TestUtil(unittest.TestCase):
    """Test utilities."""

    def test_is_number(self):
        """Test if is a number."""

        self.assertTrue(util.is_number(3))
        self.assertTrue(util.is_number(3.3))
        self.assertTrue(util.is_number(decimal.Decimal('3.3')))
        self.assertFalse(util.is_number('3.3'))

    def test_no_nan(self):
        """Test no `NaN`."""

        self.assertEqual(util.no_nan(NaN), 0)
        self.assertEqual(util.no_nans([0, 1, 2, NaN]), [0, 1, 2, 0])

    def test_compare_coords(self):
        """Test coordinate comparison."""

        self.assertTrue(util.cmp_coords([1, 2, 3], [1, 2, 3]))
        self.assertTrue(util.cmp_coords([1, NaN, 3], [1, NaN, 3]))
        self.assertFalse(util.cmp_coords([1, 3, 2], [1, 2, 3]))
        self.assertFalse(util.cmp_coords([1, 2, NaN], [1, NaN, 3]))
        self.assertFalse(util.cmp_coords([1, 2, 3, 4], [1, 2, 3]))

    def test_is_nan(self):
        """Test if is `NaN`."""

        self.assertTrue(util.is_nan(float('nan')))
        self.assertTrue(NaN)
        self.assertFalse(util.is_nan(3))
        self.assertFalse(util.is_nan(0))

    def test_round(self):
        """Test rounding."""

        self.assertEqual(util.round_half_up(3.3), 3)
        self.assertEqual(util.round_half_up(3.5), 4)
        self.assertEqual(util.round_half_up(3.9), 4)
        self.assertEqual(util.round_half_up(4), 4)

    def test_scale(self):
        """Test rounding."""

        self.assertEqual(util.round_half_up(3.345, 1), 3.3)
        self.assertEqual(util.round_half_up(3.345, 2), 3.35)
        self.assertEqual(util.round_half_up(3.345, 3), 3.345)
        self.assertEqual(util.round_half_up(333, -2), 300)

    def test_cbrt(self):
        """Test cube root."""

        self.assertEqual(util.cbrt(27), 3)
        self.assertEqual(util.cbrt(-27), -3)

    def test_clamp(self):
        """Test clamp."""

        self.assertEqual(util.clamp(3, None, None), 3)
        self.assertEqual(util.clamp(3, 4, None), 4)
        self.assertEqual(util.clamp(4, 4, None), 4)
        self.assertEqual(util.clamp(4, None, 4), 4)
        self.assertEqual(util.clamp(5, None, 4), 4)
        self.assertEqual(util.clamp(3, 4, 6), 4)
        self.assertEqual(util.clamp(7, 4, 6), 6)
        self.assertEqual(util.clamp(4, 4, 6), 4)
        self.assertEqual(util.clamp(6, 4, 6), 6)

    def test_format_float(self):
        """Test formatting of floats."""

        self.assertEqual(util.fmt_float(0.123456, 5), "0.12346")
        self.assertEqual(util.fmt_float(0.123456, 4), "0.1235")
        self.assertEqual(util.fmt_float(2.123456, 0), "2")
        self.assertEqual(util.fmt_float(2.123456, -1), "2.12345600000000001017497197608463466167449951171875")

    def test_dot(self):
        """Test dot."""

        self.assertEqual(util.dot(2, 2), 4)
        self.assertEqual(util.dot([1, 2, 3], 2), [2, 4, 6])
        self.assertEqual(util.dot(2, [1, 2, 3]), [2, 4, 6])
        self.assertEqual(util.dot([1, 2, 3], [4, 5, 6]), 32)
        self.assertEqual(util.dot([4, 5, 6], [1, 2, 3]), 32)
        self.assertEqual(
            util.dot(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [1, 2, 3]
            ),
            [14, 32, 50]
        )
        self.assertEqual(
            util.dot(
                [1, 2, 3],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [30, 36, 42]
        )
        self.assertEqual(
            util.dot(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[48, 60, 72], [8, 10, 12], [42, 51, 60]]
        )

    def test_multiply(self):
        """Test multiply."""

        self.assertEqual(util.multiply(2, 2), 4)
        self.assertEqual(util.multiply([1, 2, 3], 2), [2, 4, 6])
        self.assertEqual(util.multiply(2, [1, 2, 3]), [2, 4, 6])
        self.assertEqual(util.multiply([1, 2, 3], [4, 5, 6]), [4, 10, 18])
        self.assertEqual(util.multiply([4, 5, 6], [1, 2, 3]), [4, 10, 18])
        self.assertEqual(
            util.multiply(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [1, 2, 3]
            ),
            [[1, 4, 9], [4, 10, 18], [7, 16, 27]]
        )
        self.assertEqual(
            util.multiply(
                [1, 2, 3],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[1, 4, 9], [4, 10, 18], [7, 16, 27]]
        )
        self.assertEqual(
            util.multiply(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[4, 8, 12], [4, 0, 6], [14, 24, 36]]
        )

    def test_divide(self):
        """Test divide."""

        self.assertEqual(util.divide(4, 2), 2)
        self.assertEqual(util.divide([2, 4, 6], 2), [1, 2, 3])
        self.assertEqual(util.divide(2, [2, 4, 6]), [1.0, 0.5, 0.3333333333333333])
        self.assertEqual(util.divide([4, 10, 18], [4, 5, 6]), [1, 2, 3])
        self.assertEqual(util.divide([4, 10, 18], [1, 2, 3]), [4, 5, 6])
        self.assertEqual(
            util.divide(
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]],
                [1, 2, 3]
            ),
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        )
        self.assertEqual(
            util.divide(
                [1, 2, 3],
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]]
            ),
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        )
        self.assertEqual(
            util.divide(
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
        )
        self.assertEqual(
            util.divide(
                [[4, 8, 12], [4, 0, 6], [14, 24, 36]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[4, 4, 4], [1, 0, 1], [2, 3, 4]]
        )
