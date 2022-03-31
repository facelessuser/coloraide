"""Test Algebra."""
import unittest
from coloraide import algebra as alg


class TestAlgebra(unittest.TestCase):
    """Test Algebra."""

    def test_ones(self):
        """Test ones matrix."""

        self.assertEqual(
            alg.ones((3, 2)),
            [[1.0, 1.0],
             [1.0, 1.0],
             [1.0, 1.0]]
        )

    def test_zeros(self):
        """Test zeros matrix."""

        self.assertEqual(
            alg.zeros((2, 3)),
            [[0.0, 0.0, 0.0],
             [0.0, 0.0, 0.0]]
        )

    def test_identity(self):
        """Test identity."""

        self.assertEqual(
            alg.identity(4),
            [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, 1.0]]
        )

    def test_reshape(self):
        """Test `reshape`."""

        self.assertEqual(
            alg.reshape([0, 1, 2, 3, 4, 5], (3, 2)),
            [
                [0, 1],
                [2, 3],
                [4, 5]
            ]
        )

    def test_transpose(self):
        """Test transpose."""

        self.assertEqual(
            alg.transpose([[[5, 6, 7, 8, 9], [1, 2, 3, 4, 5]], [[9, 8, 7, 6, 5], [6, 5, 4, 3, 2]]]),
            [[[5, 9], [1, 6]], [[6, 8], [2, 5]], [[7, 7], [3, 4]], [[8, 6], [4, 3]], [[9, 5], [5, 2]]]
        )

    def test_arange(self):
        """Test `arange`."""

        self.assertEqual(
            alg.reshape(alg.arange(6), (3, 2)),
            [
                [0, 1],
                [2, 3],
                [4, 5]
            ]
        )

        self.assertEqual(
            alg.arange(0.0, 1.0, 0.1),
            [0.0,
             0.1,
             0.2,
             0.30000000000000004,
             0.4,
             0.5,
             0.6,
             0.7,
             0.7999999999999999,
             0.8999999999999999]
        )

        self.assertEqual(
            alg.arange(1.0, 0.0, -0.1),
            [1.0,
             0.9,
             0.8,
             0.7000000000000001,
             0.6000000000000001,
             0.5000000000000001,
             0.40000000000000013,
             0.30000000000000016,
             0.20000000000000015,
             0.10000000000000014]
        )

        self.assertEqual(
            alg.arange(0.2, -2.0, -0.2),
            [0.2,
             0.0,
             -0.2,
             -0.4,
             -0.6000000000000001,
             -0.8,
             -1.0,
             -1.2,
             -1.4,
             -1.5999999999999999,
             -1.7999999999999998]
        )

    def test_flatiter(self):
        """Test `flatiter`."""

        self.assertEqual(
            list(alg.flatiter([[1, 2, 3], [4, 5, 6], [7, 8, 9]])),
            [1, 2, 3, 4, 5, 6, 7, 8, 9]
        )

    def test_full(self):
        """Test full."""

        self.assertEqual(
            alg.full((3, 2, 4), 2),
            [[[2, 2, 2, 2],
              [2, 2, 2, 2]],
             [[2, 2, 2, 2],
              [2, 2, 2, 2]],
             [[2, 2, 2, 2],
              [2, 2, 2, 2]]]
        )

    def test_fill_diagonal(self):
        """Test fiiling  a diagonal."""

        m1 = alg.zeros((3, 3))
        alg.fill_diagonal(m1, 3)
        self.assertEqual(
            m1,
            [[3, 0, 0], [0, 3, 0], [0, 0, 3]]
        )

        seq = [4, 5]
        m1 = alg.zeros((3, 3))
        alg.fill_diagonal(m1, seq)
        self.assertEqual(
            m1,
            [[4, 0, 0], [0, 5, 0], [0, 0, 4]]
        )

        m1 = alg.zeros((6, 3))
        alg.fill_diagonal(m1, 3)
        self.assertEqual(
            m1,
            [[3.0, 0.0, 0.0],
             [0.0, 3.0, 0.0],
             [0.0, 0.0, 3.0],
             [0.0, 0.0, 0.0],
             [0.0, 0.0, 0.0],
             [0.0, 0.0, 0.0]]
        )

        m1 = alg.zeros((6, 3))
        alg.fill_diagonal(m1, 3, wrap=True)
        self.assertEqual(
            m1,
            [[3.0, 0.0, 0.0],
             [0.0, 3.0, 0.0],
             [0.0, 0.0, 3.0],
             [0.0, 0.0, 0.0],
             [3.0, 0.0, 0.0],
             [0.0, 3.0, 0.0]]
        )

    def test_is_nan(self):
        """Test if is `NaN`."""

        self.assertTrue(alg.is_nan(float('nan')))
        self.assertTrue(alg.NaN)
        self.assertFalse(alg.is_nan(3))
        self.assertFalse(alg.is_nan(0))

    def test_round(self):
        """Test rounding."""

        self.assertEqual(alg.round_half_up(3.3), 3)
        self.assertEqual(alg.round_half_up(3.5), 4)
        self.assertEqual(alg.round_half_up(3.9), 4)
        self.assertEqual(alg.round_half_up(4), 4)

    def test_scale(self):
        """Test rounding."""

        self.assertEqual(alg.round_half_up(3.345, 1), 3.3)
        self.assertEqual(alg.round_half_up(3.345, 2), 3.35)
        self.assertEqual(alg.round_half_up(3.345, 3), 3.345)
        self.assertEqual(alg.round_half_up(333, -2), 300)

    def test_cbrt(self):
        """Test cube root."""

        self.assertEqual(alg.cbrt(27), 3)
        self.assertEqual(alg.cbrt(-27), -3)

    def test_clamp(self):
        """Test clamp."""

        self.assertEqual(alg.clamp(3, None, None), 3)
        self.assertEqual(alg.clamp(3, 4, None), 4)
        self.assertEqual(alg.clamp(4, 4, None), 4)
        self.assertEqual(alg.clamp(4, None, 4), 4)
        self.assertEqual(alg.clamp(5, None, 4), 4)
        self.assertEqual(alg.clamp(3, 4, 6), 4)
        self.assertEqual(alg.clamp(7, 4, 6), 6)
        self.assertEqual(alg.clamp(4, 4, 6), 4)
        self.assertEqual(alg.clamp(6, 4, 6), 6)

    def test_dot(self):
        """Test dot."""

        self.assertEqual(alg.dot(2, 2), 4)
        self.assertEqual(alg.dot([1, 2, 3], 2), [2, 4, 6])
        self.assertEqual(alg.dot(2, [1, 2, 3]), [2, 4, 6])
        self.assertEqual(alg.dot([1, 2, 3], [4, 5, 6]), 32)
        self.assertEqual(alg.dot([4, 5, 6], [1, 2, 3]), 32)
        self.assertEqual(
            alg.dot(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [1, 2, 3]
            ),
            [14, 32, 50]
        )
        self.assertEqual(
            alg.dot(
                [1, 2, 3],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [30, 36, 42]
        )
        self.assertEqual(
            alg.dot(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[48, 60, 72], [8, 10, 12], [42, 51, 60]]
        )

    def test_multiply(self):
        """Test multiply."""

        self.assertEqual(alg.multiply(2, 2), 4)
        self.assertEqual(alg.multiply([1, 2, 3], 2), [2, 4, 6])
        self.assertEqual(alg.multiply(2, [1, 2, 3]), [2, 4, 6])
        self.assertEqual(alg.multiply([1, 2, 3], [4, 5, 6]), [4, 10, 18])
        self.assertEqual(alg.multiply([4, 5, 6], [1, 2, 3]), [4, 10, 18])
        self.assertEqual(
            alg.multiply(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [1, 2, 3]
            ),
            [[1, 4, 9], [4, 10, 18], [7, 16, 27]]
        )
        self.assertEqual(
            alg.multiply(
                [1, 2, 3],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[1, 4, 9], [4, 10, 18], [7, 16, 27]]
        )
        self.assertEqual(
            alg.multiply(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[4, 8, 12], [4, 0, 6], [14, 24, 36]]
        )
        self.assertEqual(
            alg.multiply(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]]
            ),
            [[4, 8, 12], [4, 0, 6], [14, 24, 36]]
        )
        self.assertEqual(
            alg.multiply(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                2
            ),
            [[8, 8, 8], [2, 0, 2], [4, 6, 8]]
        )
        self.assertEqual(
            alg.multiply(
                2,
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]]
            ),
            [[8, 8, 8], [2, 0, 2], [4, 6, 8]]
        )

    def test_divide(self):
        """Test divide."""

        self.assertEqual(alg.divide(4, 2), 2)
        self.assertEqual(alg.divide([2, 4, 6], 2), [1, 2, 3])
        self.assertEqual(alg.divide(2, [2, 4, 6]), [1.0, 0.5, 0.3333333333333333])
        self.assertEqual(alg.divide([4, 10, 18], [4, 5, 6]), [1, 2, 3])
        self.assertEqual(alg.divide([4, 10, 18], [1, 2, 3]), [4, 5, 6])
        self.assertEqual(
            alg.divide(
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]],
                [1, 2, 3]
            ),
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        )
        self.assertEqual(
            alg.divide(
                [1, 2, 3],
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]]
            ),
            [
                [1.0, 0.5, 0.3333333333333333],
                [0.25, 0.2, 0.16666666666666666],
                [0.14285714285714285, 0.125, 0.1111111111111111]
            ]
        )
        self.assertEqual(
            alg.divide(
                [[1], [2], [3]],
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]]
            ),
            [
                [1.0, 0.25, 0.1111111111111111],
                [0.5, 0.2, 0.1111111111111111],
                [0.42857142857142855, 0.1875, 0.1111111111111111]
            ]
        )
        self.assertEqual(
            alg.divide(
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]],
                [[1], [2], [3]]
            ),
            [
                [1.0, 4.0, 9.0],
                [2.0, 5.0, 9.0],
                [2.3333333333333335, 5.333333333333333, 9.0]
            ]
        )
        self.assertEqual(
            alg.divide(
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
        )
        self.assertEqual(
            alg.divide(
                [[4, 8, 12], [4, 0, 6], [14, 24, 36]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[4, 4, 4], [1, 0, 1], [2, 3, 4]]
        )
        self.assertEqual(
            alg.divide(
                [[4, 8, 12], [4, 0, 6], [14, 24, 36]],
                2
            ),
            [[2.0, 4.0, 6.0], [2.0, 0.0, 3.0], [7.0, 12.0, 18.0]]
        )
        self.assertEqual(
            alg.divide(
                2,
                [[4, 8, 12], [4, 1, 6], [14, 24, 36]]
            ),
            [
                [0.5, 0.25, 0.16666666666666666],
                [0.5, 2.0, 0.3333333333333333],
                [0.14285714285714285, 0.08333333333333333, 0.05555555555555555]
            ]
        )

    def test_add(self):
        """Test addition."""

        self.assertEqual(
            alg.add(
                alg.reshape(alg.arange(9.0), (3, 3)),
                alg.arange(3.0)
            ),
            [
                [0.0, 2.0, 4.0],
                [3.0, 5.0, 7.0],
                [6.0, 8.0, 10.0]
            ]
        )

    def test_subtraction(self):
        """Test subtraction."""

        self.assertEqual(
            alg.subtract(
                alg.reshape(alg.arange(9.0), (3, 3)),
                alg.arange(3.0)
            ),
            [
                [0.0, 0.0, 0.0],
                [3.0, 3.0, 3.0],
                [6.0, 6.0, 6.0]
            ]
        )