"""Test Algebra."""
import unittest
import math
from coloraide import algebra as alg


class TestAlgebra(unittest.TestCase):
    """Test Algebra."""

    def test_cross(self):
        """Test cross product."""

        self.assertEqual(
            alg.cross([1, 2, 3], [4, 5, 6]),
            [-3, 6, -3]
        )

        self.assertEqual(
            alg.cross([1, 2], [4, 5]),
            -3
        )

        self.assertEqual(
            alg.cross([1, 2, 3], [4, 5]),
            [-15, 12, -3]
        )

        self.assertEqual(
            alg.cross([1, 2], [4, 5, 6]),
            [12, -6, -3]
        )

        self.assertEqual(
            alg.cross(
                [[1, 2, 3],
                 [4, 5, 6]],
                [7, 8, 9]
            ),
            [[-6, 12, -6],
             [-3, 6, -3]]
        )

        self.assertEqual(
            alg.cross(
                [7, 8, 9],
                [[1, 2, 3],
                 [4, 5, 6]]
            ),
            [[6, -12, 6],
             [3, -6, 3]]
        )

        self.assertEqual(
            alg.cross(
                [[1, 2],
                 [4, 5]],
                [7, 8, 9]
            ),
            [[18, -9, -6], [45, -36, -3]]
        )

        self.assertEqual(
            alg.cross(
                [7, 8, 9],
                [[1, 2],
                 [4, 5]]
            ),
            [[-18, 9, 6], [-45, 36, 3]]
        )

        self.assertEqual(
            alg.cross(
                [7, 8],
                [[1, 2],
                 [4, 5]]
            ),
            [6, 3]
        )

        self.assertEqual(
            alg.cross(
                [[[1, 2, 3],
                  [4, 5, 6]],
                 [[7, 8, 9],
                  [10, 11, 12]]],
                [1, 2, 3]
            ),
            [[[0, 0, 0],
              [3, -6, 3]],
             [[6, -12, 6],
              [9, -18, 9]]]
        )

        self.assertEqual(
            alg.cross(
                [1, 2, 3],
                [[[1, 2, 3],
                  [4, 5, 6]],
                 [[7, 8, 9],
                  [10, 11, 12]]]
            ),
            [[[0, 0, 0],
              [-3, 6, -3]],
             [[-6, 12, -6],
              [-9, 18, -9]]]
        )

        self.assertEqual(
            alg.cross(
                [1, 2, 3],
                [[[1, 2],
                  [4, 5]],
                 [[7, 8],
                  [10, 11]]]
            ),
            [[[-6, 3, 0],
              [-15, 12, -3]],
             [[-24, 21, -6],
              [-33, 30, -9]]]
        )

        self.assertEqual(
            alg.cross(
                [[[1, 2, 3],
                  [4, 5, 6]],
                 [[7, 8, 9],
                  [10, 11, 12]]],
                [[[4, 8, 9],
                  [2, 7, 6]],
                 [[1, 4, 3],
                  [2, 3, 1]]]
            ),
            [[[-6, 3, 0],
              [-12, -12, 18]],
             [[-12, -12, 20],
              [-25, 14, 8]]]
        )

        # Broadcast
        self.assertEqual(
            alg.cross(
                [[[1, 2, 3],
                  [4, 5, 6]]],
                [[[4, 8, 9],
                  [2, 7, 6]],
                 [[1, 4, 3],
                  [2, 3, 1]]]
            ),
            [[[-6, 3, 0],
              [-12, -12, 18]],
             [[-6, 0, 2],
              [-13, 8, 2]]]
        )

        self.assertEqual(
            alg.cross(
                [[[1, 2, 3],
                  [4, 5, 6]]],
                [[[4, 8, 9],
                  [2, 7, 6]],
                 [[1, 4, 3],
                  [2, 3, 1]]]
            ),
            [[[-6, 3, 0],
              [-12, -12, 18]],
             [[-6, 0, 2],
              [-13, 8, 2]]]
        )

        self.assertEqual(
            alg.cross(
                [[[1, 2],
                  [4, 5]]],
                [[[4, 8],
                  [2, 7]],
                 [[1, 4],
                  [2, 3]]]
            ),
            [[0, 18],
             [2, 2]]
        )

        with self.assertRaises(ValueError):
            alg.cross(
                [[[1], [4]]],
                [[[4, 8, 9],
                  [2, 7, 6]],
                 [[1, 4, 3],
                  [2, 3, 1]]]
            )

        with self.assertRaises(ValueError):
            alg.cross(3, 4)

    def test_outer(self):
        """Test outer."""

        self.assertEqual(
            alg.outer(3, 4),
            [[12]]
        )

        self.assertEqual(
            alg.outer(4, [1, 2, 3]),
            [[4, 8, 12]]
        )

        self.assertEqual(
            alg.outer([1, 2, 3], 4),
            [[4], [8], [12]]
        )

        self.assertEqual(
            alg.outer([1, 2, 3], [4, 5, 6]),
            [[4, 5, 6],
             [8, 10, 12],
             [12, 15, 18]]
        )

        self.assertEqual(
            alg.outer([[1, 2], [4, 5]], [4, 5, 6]),
            [[4, 5, 6],
             [8, 10, 12],
             [16, 20, 24],
             [20, 25, 30]]
        )

        self.assertEqual(
            alg.outer([4, 5, 6], [[1, 2], [4, 5]]),
            [[4, 8, 16, 20],
             [5, 10, 20, 25],
             [6, 12, 24, 30]]
        )

        self.assertEqual(
            alg.outer([[1, 2], [3, 4]], [[5, 6], [7, 8]]),
            [[5, 6, 7, 8],
             [10, 12, 14, 16],
             [15, 18, 21, 24],
             [20, 24, 28, 32]]
        )

    def test_inner(self):
        """Test inner."""

        self.assertEqual(
            alg.inner(3, 4),
            12
        )

        self.assertEqual(
            alg.inner(3, [1, 2, 3]),
            [3, 6, 9]
        )

        self.assertEqual(
            alg.inner(3, [[1, 2], [3, 4]]),
            [[3, 6], [9, 12]]
        )

        self.assertEqual(
            alg.inner(3, [[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]]),
            [[[3, 6], [9, 12], [15, 18]], [[21, 24], [27, 30], [33, 36]]]
        )

        self.assertEqual(
            alg.inner([1, 2, 3], [4, 5, 6]),
            32
        )

        self.assertEqual(
            alg.inner([1, 2], [[1, 2], [3, 4]]),
            [5, 11]
        )

        self.assertEqual(
            alg.inner([[1, 2], [3, 4]], [[5, 6], [7, 8]]),
            [[17, 23], [39, 53]]
        )

        self.assertEqual(
            alg.inner([[1, 2], [3, 4], [3, 4]], [[5, 6], [7, 8]]),
            [[17, 23], [39, 53], [39, 53]]
        )

        self.assertEqual(
            alg.inner(
                [[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]],
                [[[13, 14], [15, 16], [17, 18]], [[19, 20], [21, 22], [23, 24]]]
            ),
            [[[[41, 47, 53], [59, 65, 71]],
              [[95, 109, 123], [137, 151, 165]],
              [[149, 171, 193], [215, 237, 259]]],
             [[[203, 233, 263], [293, 323, 353]],
              [[257, 295, 333], [371, 409, 447]],
              [[311, 357, 403], [449, 495, 541]]]]
        )

        with self.assertRaises(ValueError):
            alg.inner([1, 2, 3], [1, 2])

    def test_inv(self):
        """Test inverse."""

        self.assertEqual(
            alg.inv([[8, 9], [4, 2]]),
            [[-0.1, 0.45], [0.2, -0.4]]
        )

        self.assertEqual(
            alg.inv([[[[8, 9], [4, 2]], [[6, 2], [7, 1]]], [[[7, 3], [6, 1]], [[6, 4], [2, 2]]]]),
            [[[[-0.1, 0.45], [0.2, -0.4]],
              [[-0.125, 0.25], [0.875, -0.75]]],
             [[[-0.09090909090909095, 0.27272727272727276],
               [0.5454545454545455, -0.6363636363636365]],
              [[0.5, -0.9999999999999999],
               [-0.49999999999999994, 1.4999999999999998]]]]
        )

        # Prior to a recent change, this would fail as mathematically, this matrix
        # would have the center row zeroed out when we reduce the rows. Now, if this
        # happens, we will re run the `inv`, but evaluate the matrix in the reverse.
        self.assertEqual(
            alg.inv(
                [[0.22156862745098038, -0.22156862745098038, -0.8892156862745098],
                 [-0.3823529411764706, 0.3823529411764706, -0.45784313725490194],
                 [-0.16666666666666669, -0.8333333333333333, 0.16666666666666666]]
            ),
            [[0.7199437370447144, -1.7622890139176783, -1.0],
             [-0.3172194255256145, 0.2520728457210542, -1.0],
             [-0.8661533905833582, -0.5019247853124075, 0.0]]
        )

        with self.assertRaises(ValueError):
            alg.inv([[8, 9, 1], [4, 2, 1]])

        with self.assertRaises(ValueError):
            alg.inv([[0, 0], [0, 0]])

        with self.assertRaises(ValueError):
            alg.inv([[1, 1], [1, 1]])

    def test_vstack(self):
        """Test `vstack`."""

        self.assertEqual(
            alg.vstack((1, 2, 3, 4)),
            [[1], [2], [3], [4]]
        )

        self.assertEqual(
            alg.vstack(([1, 2], [3, 4])),
            [[1, 2], [3, 4]]
        )

        self.assertEqual(
            alg.vstack([[[1, 2], [2, 3]], [[3, 4], [4, 5]], [[5, 6], [6, 7]]]),
            [[1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7]]
        )

        self.assertEqual(
            alg.vstack([[[], []], [[], []], [[], []]]),
            [[], [], [], [], [], []]
        )

        self.assertEqual(
            alg.vstack(
                (
                    [[[[1, 2], [3, 4], [5, 6], [7, 8]],
                      [[9, 10], [11, 12], [13, 14], [15, 16]]],
                     [[[17, 18], [19, 19], [21, 22], [23, 24]],
                      [[25, 26], [27, 28], [29, 30], [31, 32]]]],
                    [[[[33, 34], [35, 36], [37, 38], [39, 40]],
                      [[41, 42], [43, 44], [45, 46], [47, 48]]],
                     [[[49, 50], [51, 52], [53, 54], [55, 56]],
                      [[57, 58], [59, 60], [61, 62], [63, 64]]]]
                )
            ),
            [[[[1, 2], [3, 4], [5, 6], [7, 8]],
              [[9, 10], [11, 12], [13, 14], [15, 16]]],
             [[[17, 18], [19, 19], [21, 22], [23, 24]],
              [[25, 26], [27, 28], [29, 30], [31, 32]]],
             [[[33, 34], [35, 36], [37, 38], [39, 40]],
              [[41, 42], [43, 44], [45, 46], [47, 48]]],
             [[[49, 50], [51, 52], [53, 54], [55, 56]],
              [[57, 58], [59, 60], [61, 62], [63, 64]]]]
        )

        with self.assertRaises(ValueError):
            alg.vstack(([1, 2, 3], [], [4, 5, 6]))

        with self.assertRaises(ValueError):
            alg.vstack(([1, 2, 3], 1, [4, 5, 6]))

        with self.assertRaises(ValueError):
            alg.vstack([])

    def test_hstack(self):
        """Test `hstack`."""

        self.assertEqual(
            alg.hstack((1, 2, 3, 4)),
            [1, 2, 3, 4]
        )

        self.assertEqual(
            alg.hstack(([1, 2], [3, 4])),
            [1, 2, 3, 4]
        )

        self.assertEqual(
            alg.hstack(([1, 2, 3], [], [4, 5, 6])),
            [1, 2, 3, 4, 5, 6]
        )

        self.assertEqual(
            alg.hstack([[1, 2, 3], 1, [4, 5, 6]]),
            [1, 2, 3, 1, 4, 5, 6]
        )

        self.assertEqual(
            alg.hstack([[[1, 2], [2, 3]], [[3, 4], [4, 5]], [[5, 6], [6, 7]]]),
            [[1, 2, 3, 4, 5, 6], [2, 3, 4, 5, 6, 7]]
        )

        self.assertEqual(
            alg.hstack([[[1, 2], [3, 4]], [[], []], [[4, 5], [6, 7]]]),
            [[1, 2, 4, 5], [3, 4, 6, 7]]
        )

        self.assertEqual(
            alg.hstack([[[], []], [[], []], [[], []]]),
            [[], []]
        )

        self.assertEqual(
            alg.hstack(
                (
                    [[[[1, 2], [3, 4], [5, 6], [7, 8]],
                      [[9, 10], [11, 12], [13, 14], [15, 16]]],
                     [[[17, 18], [19, 19], [21, 22], [23, 24]],
                      [[25, 26], [27, 28], [29, 30], [31, 32]]]],
                    [[[[33, 34], [35, 36], [37, 38], [39, 40]],
                      [[41, 42], [43, 44], [45, 46], [47, 48]],
                      [[41, 42], [43, 44], [45, 46], [47, 48]]],
                     [[[49, 50], [51, 52], [53, 54], [55, 56]],
                      [[57, 58], [59, 60], [61, 62], [63, 64]],
                      [[41, 42], [43, 44], [45, 46], [47, 48]]]]
                )
            ),
            [[[[1, 2], [3, 4], [5, 6], [7, 8]],
              [[9, 10], [11, 12], [13, 14], [15, 16]],
              [[33, 34], [35, 36], [37, 38], [39, 40]],
              [[41, 42], [43, 44], [45, 46], [47, 48]],
              [[41, 42], [43, 44], [45, 46], [47, 48]]],
             [[[17, 18], [19, 19], [21, 22], [23, 24]],
              [[25, 26], [27, 28], [29, 30], [31, 32]],
              [[49, 50], [51, 52], [53, 54], [55, 56]],
              [[57, 58], [59, 60], [61, 62], [63, 64]],
              [[41, 42], [43, 44], [45, 46], [47, 48]]]]
        )

        with self.assertRaises(ValueError):
            alg.hstack([[[1, 2], [3, 4]], 1, [[4, 5], [6, 7]]])

        with self.assertRaises(ValueError):
            alg.hstack([[[1, 2], [3, 4]], [], [[4, 5], [6, 7]]])

        with self.assertRaises(ValueError):
            alg.hstack([])

    def test_diag(self):
        """Test `diag`."""

        self.assertEqual(
            alg.diag([1, 2, 3]),
            [[1, 0, 0],
             [0, 2, 0],
             [0, 0, 3]]
        )

        self.assertEqual(
            alg.diag([1, 2, 3], 1),
            [[0, 1, 0, 0],
             [0, 0, 2, 0],
             [0, 0, 0, 3],
             [0, 0, 0, 0]]
        )

        self.assertEqual(
            alg.diag([1, 2, 3], -1),
            [[0, 0, 0, 0],
             [1, 0, 0, 0],
             [0, 2, 0, 0],
             [0, 0, 3, 0]]
        )

        self.assertEqual(
            alg.diag(alg.reshape(alg.arange(16), (4, 4))),
            [0, 5, 10, 15]
        )

        self.assertEqual(
            alg.diag(alg.reshape(alg.arange(16), (4, 4)), 1),
            [1, 6, 11]
        )

        self.assertEqual(
            alg.diag(alg.reshape(alg.arange(16), (4, 4)), -1),
            [4, 9, 14]
        )

        self.assertEqual(
            alg.diag(alg.reshape(alg.arange(16), (8, 2))),
            [0, 3]
        )

        self.assertEqual(
            alg.diag(alg.reshape(alg.arange(16), (8, 2)), 1),
            [1]
        )

        self.assertEqual(
            alg.diag(alg.reshape(alg.arange(16), (8, 2)), -1),
            [2, 5]
        )

        with self.assertRaises(ValueError):
            alg.diag(alg.reshape(alg.arange(16), (4, 2, 2)))

        with self.assertRaises(ValueError):
            alg.diag(3)

    def test_broadcast_reset(self):
        """Test broadcast reset."""

        x = [[[0, 1]],
             [[2, 3]],
             [[4, 5]]]

        y = [[0],
             [1],
             [-1]]

        b = alg.broadcast(x, y)
        self.assertEqual(next(b), (0, 0))
        self.assertEqual(next(b), (1, 0))
        b.reset()
        self.assertEqual(
            list(b),
            [(0, 0), (1, 0), (0, 1), (1, 1), (0, -1), (1, -1),
             (2, 0), (3, 0), (2, 1), (3, 1), (2, -1), (3, -1),
             (4, 0), (5, 0), (4, 1), (5, 1), (4, -1), (5, -1)]
        )

    def test_broadcast(self):
        """Test broadcast."""

        b = alg.broadcast(5, 8)
        self.assertEqual(
            list(b),
            [(5, 8)]
        )
        self.assertEqual(b.shape, ())

        b = alg.broadcast([3], [1, 2, 3])
        self.assertEqual(
            list(b),
            [(3, 1), (3, 2), (3, 3)]
        )
        self.assertEqual(b.shape, (3,))

        b = alg.broadcast(3, [1, 2, 3])
        self.assertEqual(
            list(b),
            [(3, 1), (3, 2), (3, 3)]
        )
        self.assertEqual(b.shape, (3,))

        b = alg.broadcast([1, 2, 3], 3)
        self.assertEqual(
            list(b),
            [(1, 3), (2, 3), (3, 3)]
        )
        self.assertEqual(b.shape, (3,))


        b = alg.broadcast([[1, 2, 3]], [[4], [5], [6]])
        self.assertEqual(
            list(b),
            [(1, 4), (2, 4), (3, 4), (1, 5), (2, 5), (3, 5), (1, 6), (2, 6), (3, 6)]
        )
        self.assertEqual(b.shape, (3, 3))

        b = alg.broadcast([[4], [5], [6]], [[1, 2, 3]])
        self.assertEqual(
            list(b),
            [(4, 1), (4, 2), (4, 3), (5, 1), (5, 2), (5, 3), (6, 1), (6, 2), (6, 3)]
        )
        self.assertEqual(b.shape, (3, 3))

        b = alg.broadcast([[1], [2], [3]], [[], [], []])
        self.assertEqual(
            list(b),
            []
        )
        self.assertEqual(b.shape, (3, 0))

        b = alg.broadcast([[1], [2], [3]], [[], [], []], [[4], [5], [6]])
        self.assertEqual(
            list(b),
            []
        )
        self.assertEqual(b.shape, (3, 0))

        b = alg.broadcast()
        self.assertEqual(
            list(b),
            []
        )
        self.assertEqual(b.shape, ())

        b = alg.broadcast([[1, 2, 3], [4, 5, 6]], [[7], [8]])
        self.assertEqual(
            list(b),
            [(1, 7), (2, 7), (3, 7), (4, 8), (5, 8), (6, 8)]
        )
        self.assertEqual(b.shape, (2, 3))

        b = alg.broadcast([[1, 2], [3, 4]], 5)
        self.assertEqual(
            list(b),
            [(1, 5), (2, 5), (3, 5), (4, 5)]
        )
        self.assertEqual(b.shape, (2, 2))

        b = alg.broadcast(5, [[1, 2], [3, 4]])
        self.assertEqual(
            list(b),
            [(5, 1), (5, 2), (5, 3), (5, 4)]
        )
        self.assertEqual(b.shape, (2, 2))

        b = alg.broadcast([[1, 2], [3, 4]], [5, 6])
        self.assertEqual(
            list(b),
            [(1, 5), (2, 6), (3, 5), (4, 6)]
        )
        self.assertEqual(b.shape, (2, 2))

        b = alg.broadcast([5, 6], [[1, 2], [3, 4]])
        self.assertEqual(
            list(b),
            [(5, 1), (6, 2), (5, 3), (6, 4)]
        )
        self.assertEqual(b.shape, (2, 2))

        # Can't find common shape between two arrays that have no dimensions that are 1
        with self.assertRaises(ValueError):
            list(alg.broadcast([[3, 3], [3, 3]], [[3, 3, 3], [3, 3, 3]]))

    def test_broacast_to(self):
        """Test broadcasting to."""

        self.assertEqual(
            alg.broadcast_to(3, (3, 2)),
            [[3, 3], [3, 3], [3, 3]]
        )

        self.assertEqual(
            alg.broadcast_to(3, 3),
            [3, 3, 3]
        )

        self.assertEqual(
            alg.broadcast_to(3, ()),
            3
        )

        with self.assertRaises(ValueError):
            alg.broadcast_to([1, 2, 3], ())

        # Can't broadcast to a smaller size
        with self.assertRaises(ValueError):
            alg.broadcast_to([[3, 3, 3], [3, 3, 3]], (3,))

        # Can't broadcast dimensions that are greater than 1 to a larger shape
        with self.assertRaises(ValueError):
            alg.broadcast_to([[3, 3], [3, 3]], (2, 3))

    def test_shape(self):
        """Test shape."""

        self.assertEqual(
            alg.shape(3),
            ()
        )

        self.assertEqual(
            alg.shape([1, 2]),
            (2,)
        )

        self.assertEqual(
            alg.shape([[1, 2], [1, 2], [1, 2]]),
            (3, 2)
        )

        self.assertEqual(
            alg.shape(
                [[[2, 2, 2, 2],
                  [2, 2, 2, 2]],
                 [[2, 2, 2, 2],
                  [2, 2, 2, 2]],
                 [[2, 2, 2, 2],
                  [2, 2, 2, 2]]],
            ),
            (3, 2, 4)
        )

        with self.assertRaises(ValueError):
            alg.shape(
                [[[2, 2, 2, 2],
                  [2, 2, 2, 2]],
                 [[2, 2, 2, 2, 2],
                  [2, 2, 2, 2]],
                 [[2, 2, 2, 2],
                  [2, 2, 2, 2]]],
            )

        with self.assertRaises(ValueError):
            alg.shape([3, [3], 3])

        with self.assertRaises(ValueError):
            alg.shape([[1, 2], [1, 2, 3], [1, 2]])

        with self.assertRaises(ValueError):
            alg.shape([[1, 2], [], [1, 2]])

        self.assertEqual(
            alg.shape([]),
            (0,)
        )

        self.assertEqual(
            alg.shape([[]]),
            (1, 0)
        )

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

    def test_eye(self):
        """Test eye."""

        self.assertEqual(
            alg.eye(2),
            [[1.0, 0.0],
             [0.0, 1.0]]
        )

        self.assertEqual(
            alg.eye(2, k=1),
            [[0.0, 1.0],
             [0.0, 0.0]]
        )

        self.assertEqual(
            alg.eye(2, k=2),
            [[0.0, 0.0],
             [0.0, 0.0]]
        )

        self.assertEqual(
            alg.eye(2, k=-1),
            [[0.0, 0.0],
             [1.0, 0.0]]
        )

        self.assertEqual(
            alg.eye(2, k=-2),
            [[0.0, 0.0],
             [0.0, 0.0]]
        )

        self.assertEqual(
            alg.eye(2, 3),
            [[1.0, 0.0, 0.0],
             [0.0, 1.0, 0.0]]
        )

        self.assertEqual(
            alg.eye(2, 3, k=2),
            [[0.0, 0.0, 1.0],
             [0.0, 0.0, 0.0]]
        )

        self.assertEqual(
            alg.eye(2, 3, k=-1),
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0]]
        )

        self.assertEqual(
            alg.eye(3, 2),
            [[1.0, 0.0],
             [0.0, 1.0],
             [0.0, 0.0]]
        )

        self.assertEqual(
            alg.eye(3, 2, k=1),
            [[0.0, 1.0],
             [0.0, 0.0],
             [0.0, 0.0]]
        )

        self.assertEqual(
            alg.eye(3, 2, k=-1),
            [[0.0, 0.0],
             [1.0, 0.0],
             [0.0, 1.0]]
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

        # Can't adjust shape if the shape doesn't match the data size
        with self.assertRaises(ValueError):
            alg.reshape([0, 1, 2, 3, 4, 5], (4, 2))

        # We are already at (6,), but it won't break anything
        self.assertEqual(
            alg.reshape([0, 1, 2, 3, 4, 5], 6),
            [0, 1, 2, 3, 4, 5]
        )

        self.assertEqual(
            alg.reshape([1], ()),
            1
        )

        self.assertEqual(
            alg.reshape(5, (1,)),
            [5]
        )

        with self.assertRaises(ValueError):
            alg.reshape([1, 2], ())

        # Reshaping empty data sets
        with self.assertRaises(ValueError):
            alg.reshape([], ())
        self.assertEqual(alg.reshape([], (0,)), [])
        self.assertEqual(alg.reshape([], (2, 0)), [[], []])
        self.assertEqual(alg.reshape([], (2, 3, 0)), [[[], [], []], [[], [], []]])

    def test_transpose(self):
        """Test transpose."""

        self.assertEqual(
            alg.transpose([[[5, 6, 7, 8, 9], [1, 2, 3, 4, 5]], [[9, 8, 7, 6, 5], [6, 5, 4, 3, 2]]]),
            [[[5, 9], [1, 6]], [[6, 8], [2, 5]], [[7, 7], [3, 4]], [[8, 6], [4, 3]], [[9, 5], [5, 2]]]
        )

        self.assertEqual(
            alg.transpose([[[], []], [[], []], [[], []]]),
            [[[], [], []], [[], [], []]]
        )

        self.assertEqual(alg.transpose([1, 2, 3, 4]), [1, 2, 3, 4])

        self.assertEqual(alg.transpose(1), 1)

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

        with self.assertRaises(ValueError):
            list(alg.flatiter([[1, 2], []]))

        with self.assertRaises(ValueError):
            list(alg.flatiter([[[1, 2], [1, 2, 3]], [1, 2]]))

    def test_full(self):
        """Test full."""

        self.assertEqual(alg.full((), 3), 3)

        self.assertEqual(alg.full((), [3]), 3)

        self.assertEqual(
            alg.full((3, 2, 4), 2),
            [[[2, 2, 2, 2],
              [2, 2, 2, 2]],
             [[2, 2, 2, 2],
              [2, 2, 2, 2]],
             [[2, 2, 2, 2],
              [2, 2, 2, 2]]]
        )

        self.assertEqual(
            alg.full(
                (3, 2, 4),
                [[[0, 1, 2, 3],
                  [4, 5, 6, 7]],
                 [[0, 1, 2, 3],
                  [4, 5, 6, 7]],
                 [[0, 1, 2, 3],
                  [4, 5, 6, 7]]]
            ),
            [[[0, 1, 2, 3],
              [4, 5, 6, 7]],
             [[0, 1, 2, 3],
              [4, 5, 6, 7]],
             [[0, 1, 2, 3],
              [4, 5, 6, 7]]]
        )

        self.assertEqual(
            alg.full(
                (3, 2, 4),
                [[0, 1, 2, 3],
                 [4, 5, 6, 7]]
            ),
            [[[0, 1, 2, 3],
              [4, 5, 6, 7]],
             [[0, 1, 2, 3],
              [4, 5, 6, 7]],
             [[0, 1, 2, 3],
              [4, 5, 6, 7]]]
        )

    def test_fill_diagonal(self):
        """Test filling  a diagonal."""

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

        m1 = alg.zeros((3, 3, 3))
        alg.fill_diagonal(m1, 1)
        self.assertEqual(
            m1,
            [[[1, 0.0, 0.0],
              [0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0]],

             [[0.0, 0.0, 0.0],
              [0.0, 1, 0.0],
              [0.0, 0.0, 0.0]],

             [[0.0, 0.0, 0.0],
              [0.0, 0.0, 0.0],
              [0.0, 0.0, 1]]]
        )

        # Dimensions must be at least 2D
        with self.assertRaises(ValueError):
            alg.fill_diagonal([0, 0, 0], 3)

        # Dimensions over 2D require a equal dimensions
        with self.assertRaises(ValueError):
            alg.fill_diagonal(alg.zeros((3, 2, 4)), 3)

    def test_round_to_inf(self):
        """Test rounding of infinity."""

        self.assertEqual(alg.round_to(math.inf, 2), math.inf)

    def test_round_to_full(self):
        """Test rounding of full precision."""

        self.assertEqual(alg.round_to(1 / 3, -1), 0.3333333333333333)

    def test_round_to_zero(self):
        """Test rounding of zero decimal."""

        self.assertEqual(alg.round_to(4.567, 0), 5)

    def test_round_to_num(self):
        """Test rounding of decimal number."""

        self.assertEqual(alg.round_to(4.567, 2), 4.6)

    def test_round_sig_figs(self):
        """Test rounding of significant figures."""

        self.assertEqual(alg.round_to(0.00003456, 2, 'sigfig'), 0.000035)
        self.assertEqual(alg.round_to(1.00003456, 2, 'sigfig'), 1.0)
        self.assertEqual(alg.round_to(1.00003456, -1, 'sigfig'), 1.00003456)
        self.assertEqual(alg.round_to(1.00003456, 0, 'sigfig'), 1.0)

    def test_rounding_to_decimal_place(self):
        """Test round to specific decimal places."""

        self.assertEqual(alg.round_to(4.567, 2, 'decimal'), 4.57)
        self.assertEqual(alg.round_to(4.567, 1, 'decimal'), 4.6)
        self.assertEqual(alg.round_to(14.567, -1, 'decimal'), 10.0)

    def test_bad_rounding(self):
        """Test bad rounding."""

        with self.assertRaises(ValueError):
            alg.round_to(3.245, 3, 'bad')

    def test_round(self):
        """Test rounding."""

        self.assertEqual(alg.round_half_up(3.3), 3)
        self.assertEqual(alg.round_half_up(3.5), 4)
        self.assertEqual(alg.round_half_up(3.9), 4)
        self.assertEqual(alg.round_half_up(4), 4)
        with self.assertRaises(ValueError):
            alg.round_half_up(3.56, 3.4)

    def test_rounding_scale(self):
        """Test rounding scale."""

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

    def test_matmul(self):
        """
        Test matrix multiplication.

        Results should generally match 'dot' except scalars are not allowed and
        logic for dimensions greater than 2 will be different. All other code
        is shared.
        """

        self.assertEqual(alg.matmul([1, 2, 3], [4, 5, 6]), 32)
        self.assertEqual(alg.matmul([4, 5, 6], [1, 2, 3]), 32)
        self.assertEqual(
            alg.matmul(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [1, 2, 3]
            ),
            [14, 32, 50]
        )
        self.assertEqual(
            alg.matmul(
                [1, 2, 3],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [30, 36, 42]
        )
        self.assertEqual(
            alg.matmul(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[48, 60, 72], [8, 10, 12], [42, 51, 60]]
        )

        m1 = [[[[1, 2, 3, 4],
                [5, 6, 7, 8]],
               [[10, 20, 30, 40],
                [50, 60, 70, 80]],
               [[15, 25, 35, 45],
                [55, 65, 75, 85]]]]

        m2 = [[[[11, 21],
                [31, 41],
                [51, 61],
                [71, 81]],
               [[21, 11],
                [41, 12],
                [51, 13],
                [81, 14]],
               [[2, 17],
                [2, 2],
                [9, 8],
                [3, 4]]],
              [[[5, 1],
                [5, 41],
                [5, 61],
                [5, 81]],
               [[21, 3],
                [41, 3],
                [51, 3],
                [81, 3]],
               [[4, 9],
                [6, 7],
                [1, 2],
                [1, 5]]]]

        e = [[[[510.0, 610.0],
               [1166.0, 1426.0]],

              [[5800.0, 1300.0],
               [13560.0, 3300.0]],

              [[530.0, 765.0],
               [1170.0, 2005.0]]],


             [[[50.0, 590.0],
               [130.0, 1326.0]],

              [[5800.0, 300.0],
               [13560.0, 780.0]],

              [[290.0, 605.0],
               [770.0, 1525.0]]]]

        self.assertEqual(alg.matmul(m1, m2), e)

        self.assertEqual(
            alg.matmul(m2, m1),
            [[[[116.0, 148.0, 180.0, 212.0],
               [236.0, 308.0, 380.0, 452.0],
               [356.0, 468.0, 580.0, 692.0],
               [476.0, 628.0, 780.0, 932.0]],

              [[760.0, 1080.0, 1400.0, 1720.0],
               [1010.0, 1540.0, 2070.0, 2600.0],
               [1160.0, 1800.0, 2440.0, 3080.0],
               [1510.0, 2460.0, 3410.0, 4360.0]],

              [[965.0, 1155.0, 1345.0, 1535.0],
               [140.0, 180.0, 220.0, 260.0],
               [575.0, 745.0, 915.0, 1085.0],
               [265.0, 335.0, 405.0, 475.0]]],


             [[[10.0, 16.0, 22.0, 28.0],
               [210.0, 256.0, 302.0, 348.0],
               [310.0, 376.0, 442.0, 508.0],
               [410.0, 496.0, 582.0, 668.0]],

              [[360.0, 600.0, 840.0, 1080.0],
               [560.0, 1000.0, 1440.0, 1880.0],
               [660.0, 1200.0, 1740.0, 2280.0],
               [960.0, 1800.0, 2640.0, 3480.0]],

              [[555.0, 685.0, 815.0, 945.0],
               [475.0, 605.0, 735.0, 865.0],
               [125.0, 155.0, 185.0, 215.0],
               [290.0, 350.0, 410.0, 470.0]]]]
        )

        m1 = [[[[11, 21],
                [31, 41],
                [51, 61],
                [71, 81]],
               [[21, 11],
                [41, 12],
                [51, 13],
                [81, 14]]],
              [[[5, 21],
                [5, 41],
                [5, 61],
                [5, 81]],
               [[21, 3],
                [41, 3],
                [51, 3],
                [81, 3]]]]

        self.assertEqual(
            alg.matmul([40, 0.3, 12, 9], m1),
            [[[1700.3, 2313.3], [2193.3, 725.6]], [[306.5, 2313.3], [2193.3, 183.9]]]
        )

        self.assertEqual(
            alg.matmul(m1, [40, 12]),
            [[[692, 1732, 2772, 3812], [972, 1784, 2196, 3408]], [[452, 692, 932, 1172], [876, 1676, 2076, 3276]]]
        )

        # Mismatched dimensions
        with self.assertRaises(ValueError):
            alg.matmul([1, 2, 3], [4, 5, 6, 7], dims=alg.D1)

        m1 = [[[[1, 2, 3, 4],
                [5, 6, 7, 8]],
               [[10, 20, 30, 40],
                [50, 60, 70, 80]],
               [[15, 25, 35, 45],
                [55, 65, 75, 85]]]]

        # Scalars are not allowed
        with self.assertRaises(ValueError):
            alg.matmul(m1, 3)

        with self.assertRaises(ValueError):
            alg.matmul(3, m1)

        m1 = [[[[1, 2, 3, 4, 2],
                [5, 6, 7, 8, 4]],
               [[10, 20, 30, 40, 12],
                [50, 60, 70, 80, 1]],
               [[15, 25, 35, 45, 5],
                [55, 65, 75, 85, 7]]]]

        m2 = [[[[11, 21],
                [31, 41],
                [51, 61],
                [71, 81]],
               [[21, 11],
                [41, 12],
                [51, 13],
                [81, 14]]],
              [[[5, 21],
                [5, 41],
                [5, 61],
                [5, 81]],
               [[21, 3],
                [41, 3],
                [51, 3],
                [81, 3]]]]

        # Must have signature `(n,k),(k,m)->(n,m)` for dimensions greater than 2.
        with self.assertRaises(ValueError):
            alg.matmul(m1, m2)

    def test_matmul_x3(self):
        """
        Test matrix multiplication.

        Results should generally match 'dot' except scalars are not allowed and
        logic for dimensions greater than 2 will be different. All other code
        is shared.
        """

        self.assertEqual(alg.matmul_x3([1, 2, 3], [4, 5, 6]), 32)
        self.assertEqual(alg.matmul_x3([4, 5, 6], [1, 2, 3]), 32)
        self.assertEqual(
            alg.matmul_x3(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [1, 2, 3]
            ),
            [14, 32, 50]
        )
        self.assertEqual(
            alg.matmul_x3(
                [1, 2, 3],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [30, 36, 42]
        )
        self.assertEqual(
            alg.matmul_x3(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[48, 60, 72], [8, 10, 12], [42, 51, 60]]
        )

        self.assertEqual(
            alg.matmul_x3(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1], [4], [7]]
            ),
            alg.matmul(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1], [4], [7]]
            )
        )

        # Scalars are not allowed
        with self.assertRaises(ValueError):
            alg.matmul_x3([1, 2, 3], 3)

        with self.assertRaises(ValueError):
            alg.matmul_x3(3, [1, 2, 3])

        m1 = [[[[1, 2, 3, 4],
                [5, 6, 7, 8]],
               [[10, 20, 30, 40],
                [50, 60, 70, 80]],
               [[15, 25, 35, 45],
                [55, 65, 75, 85]]]]

        m2 = [[[[11, 21],
                [31, 41],
                [51, 61],
                [71, 81]],
               [[21, 11],
                [41, 12],
                [51, 13],
                [81, 14]],
               [[2, 17],
                [2, 2],
                [9, 8],
                [3, 4]]],
              [[[5, 1],
                [5, 41],
                [5, 61],
                [5, 81]],
               [[21, 3],
                [41, 3],
                [51, 3],
                [81, 3]],
               [[4, 9],
                [6, 7],
                [1, 2],
                [1, 5]]]]

        with self.assertRaises(ValueError):
            alg.matmul_x3(m1, m2)

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

        m1 = [[[[1, 2, 3, 4],
                [5, 6, 7, 8]],
               [[10, 20, 30, 40],
                [50, 60, 70, 80]],
               [[15, 25, 35, 45],
                [55, 65, 75, 85]]]]

        m2 = [[[[11, 21],
                [31, 41],
                [51, 61],
                [71, 81]],
               [[21, 11],
                [41, 12],
                [51, 13],
                [81, 14]]],
              [[[5, 21],
                [5, 41],
                [5, 61],
                [5, 81]],
               [[21, 3],
                [41, 3],
                [51, 3],
                [81, 3]]]]

        self.assertEqual(
            alg.dot(m1, m2),
            [[[[[[510, 610], [580, 130]], [[50, 610], [580, 30]]],
               [[[1166, 1426], [1356, 330]], [[130, 1426], [1356, 78]]]],
              [[[[5100, 6100], [5800, 1300]], [[500, 6100], [5800, 300]]],
               [[[11660, 14260], [13560, 3300]], [[1300, 14260], [13560, 780]]]],
              [[[[5920, 7120], [6770, 1550]], [[600, 7120], [6770, 360]]],
               [[[12480, 15280], [14530, 3550]], [[1400, 15280], [14530, 840]]]]]]
        )

        self.assertEqual(
            alg.dot(m2, m1),
            [[[[[[  116,   148,   180,   212],
                 [ 1160,  1480,  1800,  2120],
                 [ 1320,  1640,  1960,  2280]]],

               [[[  236,   308,   380,   452],
                 [ 2360,  3080,  3800,  4520],
                 [ 2720,  3440,  4160,  4880]]],

               [[[  356,   468,   580,   692],
                 [ 3560,  4680,  5800,  6920],
                 [ 4120,  5240,  6360,  7480]]],

                [[[  476,   628,   780,   932],
                  [ 4760,  6280,  7800,  9320],
                  [ 5520,  7040,  8560, 10080]]]],

               [[[[   76,   108,   140,   172],
                  [  760,  1080,  1400,  1720],
                  [  920,  1240,  1560,  1880]]],

                [[[  101,   154,   207,   260],
                  [ 1010,  1540,  2070,  2600],
                  [ 1275,  1805,  2335,  2865]]],

                [[[  116,   180,   244,   308],
                  [ 1160,  1800,  2440,  3080],
                  [ 1480,  2120,  2760,  3400]]],

                [[[  151,   246,   341,   436],
                  [ 1510,  2460,  3410,  4360],
                  [ 1985,  2935,  3885,  4835]]]]],

              [[[[[  110,   136,   162,   188],
                  [ 1100,  1360,  1620,  1880],
                  [ 1230,  1490,  1750,  2010]]],

                [[[  210,   256,   302,   348],
                  [ 2100,  2560,  3020,  3480],
                  [ 2330,  2790,  3250,  3710]]],

                [[[  310,   376,   442,   508],
                  [ 3100,  3760,  4420,  5080],
                  [ 3430,  4090,  4750,  5410]]],

                [[[  410,   496,   582,   668],
                  [ 4100,  4960,  5820,  6680],
                  [ 4530,  5390,  6250,  7110]]]],

               [[[[   36,    60,    84,   108],
                  [  360,   600,   840,  1080],
                  [  480,   720,   960,  1200]]],

                [[[   56,   100,   144,   188],
                  [  560,  1000,  1440,  1880],
                  [  780,  1220,  1660,  2100]]],

                [[[   66,   120,   174,   228],
                  [  660,  1200,  1740,  2280],
                  [  930,  1470,  2010,  2550]]],

                [[[   96,   180,   264,   348],
                  [  960,  1800,  2640,  3480],
                  [ 1380,  2220,  3060,  3900]]]]]]
        )

        self.assertEqual(
            alg.dot(2, m1),
            [[[[2, 4, 6, 8],
               [10, 12, 14, 16]],

              [[20, 40, 60, 80],
               [100, 120, 140, 160]],

              [[30, 50, 70, 90],
               [110, 130, 150, 170]]]]
        )

        self.assertEqual(
            alg.dot(m1, 2),
            [[[[2, 4, 6, 8],
               [10, 12, 14, 16]],

              [[20, 40, 60, 80],
               [100, 120, 140, 160]],

              [[30, 50, 70, 90],
               [110, 130, 150, 170]]]]
        )

        self.assertEqual(
            alg.dot([40, 0.3, 12, 9], m2),
            [[[1700.3, 2313.3], [2193.3, 725.6]], [[306.5, 2313.3], [2193.3, 183.9]]]
        )

        self.assertEqual(
            alg.dot(m2, [40, 12]),
            [[[692, 1732, 2772, 3812], [972, 1784, 2196, 3408]], [[452, 692, 932, 1172], [876, 1676, 2076, 3276]]]
        )

        with self.assertRaises(ValueError):
            alg.dot([1, 2, 3], [4, 5, 6, 7], dims=alg.D1)

    def test_dot_x3(self):
        """Test dot."""

        self.assertEqual(alg.dot_x3(2, 2), 4)
        self.assertEqual(alg.dot_x3([1, 2, 3], 2), [2, 4, 6])
        self.assertEqual(alg.dot_x3(2, [1, 2, 3]), [2, 4, 6])
        self.assertEqual(alg.dot_x3([1, 2, 3], [4, 5, 6]), 32)
        self.assertEqual(alg.dot_x3([4, 5, 6], [1, 2, 3]), 32)
        self.assertEqual(
            alg.dot_x3(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [1, 2, 3]
            ),
            [14, 32, 50]
        )
        self.assertEqual(
            alg.dot_x3(
                [1, 2, 3],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [30, 36, 42]
        )
        self.assertEqual(
            alg.dot_x3(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[48, 60, 72], [8, 10, 12], [42, 51, 60]]
        )

        self.assertEqual(
            alg.dot_x3(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                dims=alg.D2
            ),
            [[48, 60, 72], [8, 10, 12], [42, 51, 60]]
        )

    def test_multi_dot(self):
        """Test multi-dot."""

        a = alg.reshape(alg.arange(10 * 30), (10, 30))
        b = alg.reshape(alg.arange(30 * 5), (30, 5))
        c = alg.reshape(alg.arange(5 * 60), (5, 60))
        d = alg.reshape(alg.arange(60 * 5), (60, 5))

        # We need at least two arrays
        with self.assertRaises(ValueError):
            alg.multi_dot([[1, 2, 3]])

        # Test path of 2 matrices which will just be redirected to normal dot.
        self.assertEqual(
            alg.multi_dot(
                (
                    [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
                )
            ),
            [[48, 60, 72], [8, 10, 12], [42, 51, 60]]
        )

        # Test 3 way case which is a little less computationally intense.
        self.assertEqual(
            alg.multi_dot((a, b, c)),
            alg.dot(a, alg.dot(b, c))
        )

        # Test >3
        self.assertEqual(
            alg.multi_dot((a, b, c, d)),
            alg.dot(a, alg.dot(b, alg.dot(c, d)))
        )

        # Test that we assert if matrices are not of shape 2-D
        with self.assertRaises(ValueError):
            alg.multi_dot((a, alg.zeros((2,)), c))

        # Test that a vector in position 1 or -1 will be treated
        # as row vector or column vector respectively.
        self.assertEqual(
            alg.multi_dot(([1, 2, 3], alg.full((3, 3), 1), alg.full((3, 3), 2))),
            [36, 36, 36]
        )
        self.assertEqual(
            alg.multi_dot((alg.full((3, 3), 2), alg.full((3, 3), 1), [1, 2, 3])),
            [36, 36, 36]
        )
        self.assertEqual(
            alg.multi_dot(([1, 2, 3], alg.full((3, 3), 1), [1, 2, 3])),
            36
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

        self.assertEqual(
            alg.multiply(
                [[1, 2, 3]],
                [[4], [5], [6]]
            ),
            [[4, 8, 12], [5, 10, 15], [6, 12, 18]]
        )

        self.assertEqual(
            alg.multiply(
                [[4], [5], [6]],
                [[1, 2, 3]]
            ),
            [[4, 8, 12], [5, 10, 15], [6, 12, 18]]
        )

        m1 = [[[[1, 2, 3, 4],
                [5, 6, 7, 8]],
               [[10, 20, 30, 40],
                [50, 60, 70, 80]],
               [[15, 25, 35, 45],
                [55, 65, 75, 85]]]]

        m2 = [[[[50, 60, 70, 80],
                [15, 25, 35, 45]],
               [[10, 20, 30, 40],
                [5, 6, 7, 8]],
               [[1, 2, 3, 4],
                [55, 65, 75, 85]]]]

        self.assertEqual(
            alg.multiply(m1, [1, 2, 3, 4]),
            [[[[1, 4, 9, 16],
               [5, 12, 21, 32]],
              [[10, 40, 90, 160],
               [50, 120, 210, 320]],
              [[15, 50, 105, 180],
               [55, 130, 225, 340]]]]
        )

        self.assertEqual(
            alg.multiply([1, 2, 3, 4], m1),
            [[[[1, 4, 9, 16],
               [5, 12, 21, 32]],
              [[10, 40, 90, 160],
               [50, 120, 210, 320]],
              [[15, 50, 105, 180],
               [55, 130, 225, 340]]]]
        )

        self.assertEqual(
            alg.multiply(m1, m2),
            [[[[50, 120, 210, 320], [75, 150, 245, 360]],
              [[100, 400, 900, 1600], [250, 360, 490, 640]],
              [[15, 50, 105, 180], [3025, 4225, 5625, 7225]]]]
        )

        self.assertEqual(
            alg.multiply(m2, m1),
            [[[[50, 120, 210, 320], [75, 150, 245, 360]],
              [[100, 400, 900, 1600], [250, 360, 490, 640]],
              [[15, 50, 105, 180], [3025, 4225, 5625, 7225]]]]
        )

        self.assertEqual(
            alg.multiply(m1, 3),
            [[[[3, 6, 9, 12], [15, 18, 21, 24]],
              [[30, 60, 90, 120], [150, 180, 210, 240]],
              [[45, 75, 105, 135], [165, 195, 225, 255]]]]
        )

        self.assertEqual(
            alg.multiply(3, m1),
            [[[[3, 6, 9, 12], [15, 18, 21, 24]],
              [[30, 60, 90, 120], [150, 180, 210, 240]],
              [[45, 75, 105, 135], [165, 195, 225, 255]]]]
        )

    def test_multiply_x3(self):
        """Test multiply."""

        self.assertEqual(alg.multiply_x3(2, 2), 4)
        self.assertEqual(alg.multiply_x3([1, 2, 3], 2), [2, 4, 6])
        self.assertEqual(alg.multiply_x3(2, [1, 2, 3]), [2, 4, 6])
        self.assertEqual(alg.multiply_x3([1, 2, 3], [4, 5, 6]), [4, 10, 18])
        self.assertEqual(alg.multiply_x3([4, 5, 6], [1, 2, 3]), [4, 10, 18])
        self.assertEqual(
            alg.multiply_x3(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [1, 2, 3]
            ),
            [[1, 4, 9], [4, 10, 18], [7, 16, 27]]
        )
        self.assertEqual(
            alg.multiply_x3(
                [1, 2, 3],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[1, 4, 9], [4, 10, 18], [7, 16, 27]]
        )
        self.assertEqual(
            alg.multiply_x3(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[4, 8, 12], [4, 0, 6], [14, 24, 36]]
        )
        self.assertEqual(
            alg.multiply_x3(
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]]
            ),
            [[4, 8, 12], [4, 0, 6], [14, 24, 36]]
        )
        self.assertEqual(
            alg.multiply_x3(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                2
            ),
            [[8, 8, 8], [2, 0, 2], [4, 6, 8]]
        )
        self.assertEqual(
            alg.multiply_x3(
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
        self.assertEqual(alg.divide(8, 4), 2)

    def test_divide_x3(self):
        """Test divide."""

        self.assertEqual(alg.divide_x3(4, 2), 2)
        self.assertEqual(alg.divide_x3([2, 4, 6], 2), [1, 2, 3])
        self.assertEqual(alg.divide_x3(2, [2, 4, 6]), [1.0, 0.5, 0.3333333333333333])
        self.assertEqual(alg.divide_x3([4, 10, 18], [4, 5, 6]), [1, 2, 3])
        self.assertEqual(alg.divide_x3([4, 10, 18], [1, 2, 3]), [4, 5, 6])
        self.assertEqual(
            alg.divide_x3(
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]],
                [1, 2, 3]
            ),
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        )
        self.assertEqual(
            alg.divide_x3(
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
            alg.divide_x3(
                [[1, 4, 9], [4, 10, 18], [7, 16, 27]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
        )
        self.assertEqual(
            alg.divide_x3(
                [[4, 8, 12], [4, 0, 6], [14, 24, 36]],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            ),
            [[4, 4, 4], [1, 0, 1], [2, 3, 4]]
        )
        self.assertEqual(
            alg.divide_x3(
                [[4, 8, 12], [4, 0, 6], [14, 24, 36]],
                2
            ),
            [[2.0, 4.0, 6.0], [2.0, 0.0, 3.0], [7.0, 12.0, 18.0]]
        )
        self.assertEqual(
            alg.divide_x3(
                2,
                [[4, 8, 12], [4, 1, 6], [14, 24, 36]]
            ),
            [
                [0.5, 0.25, 0.16666666666666666],
                [0.5, 2.0, 0.3333333333333333],
                [0.14285714285714285, 0.08333333333333333, 0.05555555555555555]
            ]
        )
        self.assertEqual(alg.divide_x3(8, 4), 2)

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

    def test_add_x3(self):
        """Test addition."""

        self.assertEqual(
            alg.add_x3(
                alg.reshape(alg.arange(9.0), (3, 3)),
                alg.arange(3.0)
            ),
            [
                [0.0, 2.0, 4.0],
                [3.0, 5.0, 7.0],
                [6.0, 8.0, 10.0]
            ]
        )

    def test_subtraction3(self):
        """Test subtraction."""

        self.assertEqual(
            alg.subtract_x3(
                alg.reshape(alg.arange(9.0), (3, 3)),
                alg.arange(3.0)
            ),
            [
                [0.0, 0.0, 0.0],
                [3.0, 3.0, 3.0],
                [6.0, 6.0, 6.0]
            ]
        )

        self.assertEqual(
            alg.subtract_x3(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1], [4], [7]]
            ),
            alg.subtract(
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]],
                [[1], [4], [7]]
            )
        )

        self.assertEqual(
            alg.subtract_x3(
                [[1], [4], [7]],
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]]
            ),
            alg.subtract(
                [[1], [4], [7]],
                [[4, 4, 4], [1, 0, 1], [2, 3, 4]]
            )
        )

        self.assertEqual(
            alg.subtract_x3(
                [[1], [4], [7]],
                [[4], [1], [2]]
            ),
            alg.subtract(
                [[1], [4], [7]],
                [[4], [1], [2]]
            )
        )

        with self.assertRaises(ValueError):
            alg.subtract_x3([[1, 1, 1], [2, 2, 2], [3, 3, 3]], [[1, 1], [2, 2], [3, 3]])

    def test_interpolate(self):
        """Test interpolation."""

        self.assertEqual(
            alg.interpolate([[3, 4], [6, 8], [9, 2]]).steps(5),
            [[3.0, 4.0], [4.5, 6.0], [6.0, 8.0], [7.5, 5.0], [9.0, 2.0]]
        )

    def test_interpolate_natural(self):
        """Test interpolation with a natural spline."""

        self.assertEqual(
            alg.interpolate([[3, 4], [6, 8], [9, 2]], method='natural').steps(5),
            [[3.0, 4.0], [4.5, 6.9375], [6.0, 8.0], [7.5, 5.9375], [9.0, 2.0]]
        )

    def test_interpolate_extrapolate(self):
        """Test extrapolation with splines when interpolating."""

        i = alg.interpolate([[3, 4], [6, 8], [9, 2]], method='natural')
        self.assertEqual(
            i(1.2),
            [9.6, 0.3000000000000007]
        )
        self.assertEqual(
            i(-0.2),
            [2.4, 2.7]
        )

    def test_vectorize(self):
        """Test `vectorize`."""

        cbrt = alg.vectorize(lambda x: alg.nth_root(x, 3))

        self.assertEqual(
            cbrt([8, 27]),
            [2, 3]
        )

        log = alg.vectorize(math.log)
        self.assertEqual(
            log([10, 100]),
            [2.302585092994046, 4.605170185988092]
        )

        self.assertEqual(
            log([10, 100], 10),
            [1.0, 2.0]
        )

        # No arguments sanity check (don't do this in the real world :))
        pi = alg.vectorize(lambda: math.pi)
        self.assertEqual(pi(), math.pi)

        # Exercise logic when no vectorization is allowed while also testing "excluded"
        cbrt2 = alg.vectorize(lambda x: alg.nth_root(x, 3), excluded=[0])
        self.assertEqual(cbrt2(27), 3)

        # Test excluded keywords
        log = alg.vectorize(lambda x, *, base=math.e: math.log(x, base), excluded=['base'])

        self.assertEqual(
            log([10, 100], base=10),
            [1.0, 2.0]
        )

        with self.assertRaises(TypeError):
            log([10, 100], base=[10, math.e])

    def test_vectorize1(self):
        """Test `vectorize1`."""

        cbrt = alg.vectorize2(lambda x: alg.nth_root(x, 3), params=1)

        self.assertEqual(
            cbrt([8, 27]),
            [2, 3]
        )

        with self.assertRaises(TypeError):
            cbrt([8, 27], 4)

        cbrt_x3 = alg.vectorize2(lambda x: alg.nth_root(x, 3), params=1, only_x3=True)

        self.assertEqual(
            cbrt_x3([8, 27, 27]),
            [2, 3, 3]
        )

        self.assertEqual(
            cbrt_x3([8, 27, 27], dims=alg.D1),
            [2, 3, 3]
        )

        self.assertEqual(
            cbrt_x3(27),
            3
        )

        self.assertEqual(
            cbrt_x3(
                [[8, 27, 27], [8, 27, 27], [8, 27, 27]]
            ),
            [[2, 3, 3], [2, 3, 3], [2, 3, 3]]
        )

        self.assertEqual(
            cbrt_x3(
                [[8], [27], [8]]
            ),
            [[2], [3], [2]]
        )

        with self.assertRaises(ValueError):
            cbrt_x3(
                [
                    [[8, 27, 27], [8, 27, 27], [8, 27, 27]],
                    [[8, 27, 27], [8, 27, 27], [8, 27, 27]],
                    [[8, 27, 27], [8, 27, 27], [8, 27, 27]]
                ]
            )

    def test_vectorize2(self):
        """Test `vectorize2`."""

        log = alg.vectorize2(math.log)

        self.assertEqual(
            log([10, 100], 10),
            [1.0, 2.0]
        )

        self.assertEqual(
            log([10, 100], [10, math.e]),
            [1.0, 4.605170185988092]
        )

        with self.assertRaises(TypeError):
            log([10, 100])

        with self.assertRaises(ValueError):
            alg.vectorize2(math.log, params=3)

        root = alg.vectorize2(alg.nth_root, only_x3=True)
        with self.assertRaises(ValueError):
            root(
                [
                    [[1, 2, 3], [1, 2, 3], [1, 2, 3]],
                    [[1, 2, 3], [1, 2, 3], [1, 2, 3]],
                    [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
                ],
                3
            )

    def test_apply_two_inputs(self):
        """Test vectorize2 with two inputs."""

        spow = alg.vectorize2(alg.spow)
        self.assertEqual(
            spow([[1, 2, 3], [4, 5, 6]], 2),
            [[1, 4, 9], [16, 25, 36]]
        )

    def test_apply_one_input(self):
        """Test apply with one input."""

        sqrt = alg.vectorize2(math.sqrt, params=1)
        self.assertEqual(
            sqrt([[1, 4, 9], [16, 25, 36]]),
            [[1, 2, 3], [4, 5, 6]]
        )

        isnan = alg.vectorize2(math.isnan, params=1)
        self.assertTrue(isnan(math.nan))
        self.assertEqual(isnan([2, math.nan, 1]), [False, True, False])
        self.assertEqual(isnan([[2, math.nan], [math.nan, 1]]), [[False, True], [True, False]])
        self.assertTrue(isnan(math.nan, dims=alg.SC))
        self.assertEqual(isnan([2, math.nan, 1], dims=alg.D1), [False, True, False])
        self.assertEqual(isnan([[2, math.nan], [math.nan, 1]], dims=alg.D2), [[False, True], [True, False]])
        self.assertEqual(isnan(
            [[[2, math.nan], [math.nan, 1]], [[2, math.nan], [math.nan, 1]]]),
            [[[False, True], [True, False]], [[False, True], [True, False]]]
        )

    def test_linspace(self):
        """Test `linspace`."""

        self.assertEqual(
            alg.linspace(0, 10, 11),
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        )

        self.assertEqual(
            alg.linspace(0, 10, 11, endpoint=False),
            [0.0,
             0.9090909090909092,
             1.8181818181818183,
             2.727272727272727,
             3.6363636363636367,
             4.545454545454545,
             5.454545454545454,
             6.363636363636363,
             7.272727272727273,
             8.181818181818182,
             9.09090909090909]
        )

        self.assertEqual(
            alg.linspace(0, [5, 10], 3),
            [[0.0, 0.0], [2.5, 5.0], [5.0, 10.0]]
        )

        self.assertEqual(
            alg.linspace([0], [5, 10], 3),
            [[0.0, 0.0], [2.5, 5.0], [5.0, 10.0]]
        )

        self.assertEqual(
            alg.linspace([0, 0], 10, 3),
            [[0.0, 0.0], [5.0, 5.0], [10.0, 10.0]]
        )

        self.assertEqual(
            alg.linspace([0, 0], [10], 3),
            [[0.0, 0.0], [5.0, 5.0], [10.0, 10.0]]
        )

        self.assertEqual(
            alg.linspace([0, 1], [1, 2], 3),
            [[0.0, 1.0], [0.5, 1.5], [1.0, 2.0]]
        )

        self.assertEqual(
            alg.linspace([[0, 1], [2, 3]], [[4, 5], [6, 7]], 3),
            [[[0.0, 1.0], [2.0, 3.0]], [[2.0, 3.0], [4.0, 5.0]], [[4.0, 5.0], [6.0, 7.0]]]
        )

        self.assertEqual(
            alg.linspace(0, 1, 0),
            []
        )

        self.assertEqual(
            alg.linspace([0, 1], [1, 2], 0),
            [[], []]
        )

        with self.assertRaises(ValueError):
            alg.linspace(0, 1, -1)

        with self.assertRaises(ValueError):
            alg.linspace([0, 0], [1, 1, 1], 3)

    def test_ilerp(self):
        """Test inverse interpolation."""

        t = 0.5
        v = alg.lerp(0.2, 1.8, t)
        self.assertEqual(round(alg.ilerp(0.2, 1.8, v), 5), t)

    def test_lerp2d(self):
        """Test 2D interpolation."""

        m = [[0.1, 0.0], [1.0, 0.0], [0.0, .95], [1.0, 1.0]]
        v = alg.lerp2d(alg.transpose(m), [0.5, 0.5])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [0.525, 0.4875])]
        v = alg.lerp2d(alg.transpose(m), [0.0, 0.0])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [0.1, 0.0])]
        v = alg.lerp2d(alg.transpose(m), [1.0, 0.0])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [1.0, 0.0])]
        v = alg.lerp2d(alg.transpose(m), [0.0, 1.0])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [0.0, .95])]
        v = alg.lerp2d(alg.transpose(m), [1.0, 1.0])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [1, 1])]

    def test_ilerp2d(self):
        """Test inverse 2D interpolation."""

        m = [[0.1, 0.0], [1.0, 0.0], [0.0, .95], [1.0, 1.0]]
        v = alg.ilerp2d(alg.transpose(m), [0.525, 0.4875])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [0.5, 0.5])]
        v = alg.ilerp2d(alg.transpose(m), [0.1, 0.0])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [0.0, 0.0])]
        v = alg.ilerp2d(alg.transpose(m), [1.0, 0.0])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [1.0, 0.0])]
        v = alg.ilerp2d(alg.transpose(m), [0.0, .95])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [0.0, 1.0])]
        v = alg.ilerp2d(alg.transpose(m), [1, 1])
        [self.assertAlmostEqual(a, b) for a, b in zip(v, [1.0, 1.0])]

    def test_solve(self):
        """Test solving of linear equations."""

        m = [[1, 3, 4, 7],
             [-8, 27, -36, 0],
             [28, -5, 0, 2],
             [4, 2, 8, -1]]

        s = [-12, 2, 5, -2]

        self.assertEqual(
            alg.solve(m, s),
            [0.19923880867516464, -0.4159366882136168, -0.41178336253247144, -1.329185041986347]
        )

        sm = [[-12, 2, 5, -2],
              [2, 5, -2, 3],
              [20, -19, 1, 5],
              [0, 0, 3, 0]]

        self.assertEqual(
            alg.solve(m, sm),
            [[0.7559958919833264, -0.6273787228901105, 0.07044040355222618, 0.1955536760708029],
             [-0.3308161662538513, 0.3251978493324473, 0.3477919410378783, -0.0010270041684286482],
             [-0.47166676735334984, 0.24442699208602667, 0.3007460883223585, -0.12755995891983324],
             [-1.4109829034011963, 0.09629674379266602, 0.3833142028635293, -0.24031897541231195]]
        )

        m = [[0, 4, 8],
             [7, 2, 6],
             [1, 5, 3]]
        b = [0, 2, 1]
        e = [0.3137254901960785, 0.19607843137254902, -0.09803921568627451]
        self.assertEqual(alg.solve(m, b), e)

        m = [[7, 5, 8],
             [1, 2, 0],
             [6, 3, 4]]
        b = [[8, 6, 2],
             [4, 7, 0],
             [1, 5, 3]]
        e = [[-1.7777777777777781, 0.11111111111111148, 0.8888888888888891],
             [2.888888888888889, 3.444444444444444, -0.4444444444444445],
             [0.7500000000000002, -1.5000000000000002, -0.2500000000000001]]
        self.assertEqual(alg.solve(m, b), e)

        m = [[1, 3, 4],
             [8, 5, 6],
             [7, 2, 0]]
        b = [[9, 20, 18, 12, 4, 13, 21, 11],
             [3, 10, 22, 0, 15, 23, 5, 1],
             [16, 8, 17, 7, 6, 19, 2, 14]]
        e = [[-3.05263157894737, -4.631578947368421, -1.9473684210526319, -4.157894736842106,
              1.5789473684210527, -0.2631578947368416, -5.684210526315789, -4.0],
             [18.68421052631579, 20.210526315789473, 15.31578947368421, 18.05263157894737,
              -2.526315789473684, 10.421052631578947, 20.894736842105264, 21.0],
             [-11.0, -9.0, -6.5, -9.5, 2.5, -4.5, -9.0, -12.0]]
        self.assertEqual(alg.solve(m, b), e)

        m = [[8, 0, 2],
             [5, 1, 6],
             [3, 4, 7]]
        b = [[[15, 4, 23],
              [33, 7, 34],
              [1, 11, 0]],

             [[17, 35, 6],
              [14, 9, 8],
              [5, 32, 26]],

             [[16, 19, 20],
              [2, 3, 13],
              [29, 10, 25]],

             [[22, 12, 24],
              [18, 31, 28],
              [21, 30, 27]]]
        e = [[[-0.06862745098039214, 0.33333333333333337, 1.1666666666666667],
              [-13.303921568627452, 1.3333333333333335, -12.833333333333332],
              [7.7745098039215685, 0.6666666666666666, 6.833333333333333]],

             [[1.8333333333333333, 5.754901960784314, 0.8823529411764706],
              [-2.166666666666667, 13.343137254901961, 6.764705882352941],
              [1.1666666666666667, -5.519607843137255, -0.5294117647058824]],

             [[3.0784313725490193, 3.127450980392157, 2.803921568627451],
              [12.490196078431373, 5.421568627450981, 6.2745098039215685],
              [-4.313725490196078, -3.0098039215686274, -1.2156862745098038]],

             [[2.6666666666666665, 0.15686274509803932, 2.3333333333333335],
              [2.666666666666667, -2.019607843137255, 0.3333333333333339],
              [0.3333333333333333, 5.372549019607843, 2.6666666666666665]]]
        self.assertEqual(alg.solve(m, b), e)

        m = [[5, 1, 3],
             [4, 7, 6],
             [8, 0, 2]]
        b = [[[18, 13],
              [2, 11],
              [19, 5]],

             [[3, 17],
              [7, 6],
              [12, 1]],

             [[4, 0],
              [8, 15],
              [14, 10]],

             [[20, 22],
              [16, 23],
              [21, 9]]]
        e = [[[0.6379310344827589, -1.4655172413793105],
              [-6.0344827586206895, -4.758620689655173],
              [6.948275862068964, 8.362068965517242]],

             [[2.6206896551724137, -3.637931034482758],
              [3.3448275862068964, -9.965517241379308],
              [-4.482758620689655, 15.051724137931032]],

             [[2.931034482758621, 3.103448275862069],
              [3.517241379310345, 6.724137931034483],
              [-4.724137931034483, -7.413793103448276]],

             [[1.1551724137931036, -2.1896551724137927],
              [-3.4137931034482754, -6.827586206896551],
              [5.879310344827585, 13.25862068965517]]]
        self.assertEqual(alg.solve(m, b), e)

        m = [[[3, 6, 25],
              [18, 31, 4],
              [1, 22, 8]],

             [[13, 30, 24],
              [33, 16, 27],
              [19, 28, 7]],

             [[15, 17, 32],
              [9, 23, 14],
              [2, 12, 0]],

             [[34, 29, 10],
              [11, 26, 35],
              [5, 21, 20]]]
        b = [[1, 6, 4],
             [3, 10, 8],
             [2, 7, 11],
             [0, 9, 5]]

        with self.assertRaises(ValueError):
            alg.solve(m, b)

        m = [[[14, 9, 1],
              [18, 21, 5],
              [24, 3, 22]],

             [[26, 15, 10],
              [23, 16, 4],
              [0, 20, 25]],

             [[6, 7, 17],
              [13, 8, 19],
              [12, 11, 2]]]
        b = [[4, 1, 7],
             [0, 3, 5],
             [6, 8, 2]]
        e = [[[0.5812274368231046, 0.016245487364620947, 0.6624548736462091],
              [-0.4259927797833935, 0.04813477737665463, -0.1853188929001202],
              [-0.30324909747292417, 0.33935018050541516, -0.6064981949458482]],
             [[0.1583236321303841, -0.2339930151338766, 0.27124563445867284],
              [-0.3594877764842838, 0.5548311990686845, -0.12176949941792765],
              [0.527590221187427, -0.12386495925494755, 0.17741559953434213]],
             [[-0.7488151658767774, 0.2862559241706164, -0.46635071090047414],
              [1.3744075829383888, 0.45687203791469166, 0.6331753554502372],
              [-0.06635071090047394, -0.23033175355450242, 0.3156398104265403]]]
        self.assertEqual(alg.solve(m, b), e)

        self.assertEqual(
            alg.solve([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], [1, 2]),
            [[0.0, 0.5], [2.000000000000001, -1.5000000000000009]]
        )

        with self.assertRaises(ValueError):
            alg.solve([[2, 4, 5, 6], [0, 0, 0, 0], [1, -4, 0, 3], [2, 9, 9, 2]], [3, 5, 6, 1])

        with self.assertRaises(ValueError):
            alg.solve([[1, 2, 3], [4, 5, 6]], [0, 1])

        with self.assertRaises(ValueError):
            m = [[5, 1, 3],
                 [4, 7, 6],
                 [8, 0, 2]]
            b = [1, 2, 3, 4]
            alg.solve(m, b)

        with self.assertRaises(ValueError):
            m = [[7, 5, 8],
                 [1, 2, 0],
                 [6, 3, 4]]
            b = [[8, 6, 2],
                 [4, 7, 0],
                 [1, 5, 3],
                 [4, 5, 6]]
            alg.solve(m, b)

        with self.assertRaises(ValueError):
            m = [[7, 5, 8],
                 [1, 2, 0],
                 [6, 3, 4]]
            b = [[8, 6, 2],
                 [4, 7, 0, 3],
                 [1, 5, 3]]
            alg.solve(m, b)

        with self.assertRaises(ValueError):
            m = alg.reshape([1] * 9, (3, 3))
            b = alg.reshape([1] * 36, (4, 3, 3))
            alg.solve(m, b)

        with self.assertRaises(ValueError):
            m = alg.reshape([1] * 27, (3, 3, 3))
            b = alg.reshape([1] * 9, (3, 3))
            alg.solve(m, b)

        with self.assertRaises(ValueError):
            m = alg.reshape([1] * 27, (3, 3, 3))
            b = alg.reshape([1] * 24, (3, 4, 2))
            alg.solve(m, b)

    def test_lu(self):
        """Test `LU` decomposition."""

        m = [[1, 0, 1], [4, 0, 3], [1, 2, -1]]
        p, l, u = alg.lu(m)
        self.assertEqual(alg.dot(p, m), alg.dot(l, u))

        m = [[1, 0, 0], [3, 2, 0], [1, 0, 1]]
        p, l, u = alg.lu(m)
        self.assertEqual(alg.dot(p, m), alg.dot(l, u))

        m =  [[2, 4, 5, 6], [0, 0, 0, 0], [1, -4, 0, 3], [2, 9, 9, 2]]
        p, l, u = alg.lu(m)
        self.assertEqual(alg.dot(p, m), alg.dot(l, u))

        # tall
        m = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15]]
        p, l, u = alg.lu(m)
        self.assertEqual(alg.dot(p, m), alg.dot(l, u))

        # wide
        m = [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10], [11, 12, 13, 14, 15]]
        p, l, u = alg.lu(m)
        self.assertEqual(alg.dot(p, m), alg.dot(l, u))

        m =  [[2, 4, 5, 6], [0, 0, 0, 0], [1, -4, 0, 3], [2, 9, 9, 2]]
        p, l, u = alg.lu(m, p_indices=True)
        self.assertEqual([m[idx] for idx in p], alg.dot(l, u))

        m =  [[2, 4, 5, 6], [0, 0, 0, 0], [1, -4, 0, 3], [2, 9, 9, 2]]
        l, u = alg.lu(m, permute_l=True)
        self.assertEqual(m, alg.dot(l, u))

        self.assertEqual(alg.lu([[], []]), ([], [[], []], []))

        m = [[[18, 13],
              [2, 11],
              [19, 5]],

             [[3, 17],
              [7, 6],
              [12, 1]],

             [[4, 0],
              [8, 15],
              [14, 10]],

             [[20, 22],
              [16, 23],
              [21, 9]]]
        p, l, u = alg.lu(m)
        sm = alg.shape(m)
        sp, sl, su = alg.shape(p), alg.shape(l), alg.shape(u)
        rm = list(alg._extract_rows(m, sm))
        rp, rl, ru = list(alg._extract_rows(p, sp)),  list(alg._extract_rows(l, sl)),  list(alg._extract_rows(u, su))
        mm = [rm[r:r + sm[-2]] for r in range(0, len(rm), sm[-2])]
        mp = [rp[r:r + sp[-2]] for r in range(0, len(rp), sp[-2])]
        ml = [rl[r:r + sl[-2]] for r in range(0, len(rl), sl[-2])]
        mu = [ru[r:r + su[-2]] for r in range(0, len(ru), su[-2])]
        for _m, _p, _l, _u in zip(mm, mp, ml, mu):
            self.assertTrue(alg.allclose(alg.dot(_p, _m), alg.dot(_l, _u), rel_tol=1e-12, abs_tol=1e-12))

        l, u = alg.lu(m, permute_l=True)
        self.assertEqual(
            l,
            [[[0.9473684210526315, 0.7889447236180905],
              [0.10526315789473684, 1.0],
              [1.0, 0.0]],

             [[0.25, 1.0],
              [0.5833333333333334, 0.32338308457711445],
              [1.0, 0.0]],

             [[0.2857142857142857, -0.3076923076923076],
              [0.5714285714285714, 1.0],
              [1.0, 0.0]],

             [[0.9523809523809523, 0.8318584070796461],
              [0.7619047619047619, 1.0],
              [1.0, 0.0]]]
        )

        self.assertEqual(
            u,
            [[[19, 5],
              [0.0, 10.473684210526315]],

             [[12, 1],
              [0.0, 16.75]],

             [[14, 10],
              [0.0, 9.285714285714286]],

             [[21, 9],
              [0.0, 16.142857142857142]]]
        )

        with self.assertRaises(ValueError):
            alg.lu([1, 2, 3])

    def test_det(self):
        """Test determinant."""

        self.assertEqual(alg.det([[1, 0, 1], [4, 0, 3], [1, 2, -1]]), 2.0)

        m = [[[[8, 9], [4, 2]],
              [[6, 2], [7, 1]]],
             [[[7, 3], [6, 1]],
              [[6, 4], [2, 2]]]]

        self.assertEqual(alg.det(m), [-20.0, -8.0, -10.999999999999998, 4.0])

        with self.assertRaises(ValueError):
            alg.det([[1, 2, 3], [4, 5, 6]])

    def test_any(self):
        """Test any."""

        self.assertTrue(alg.any([False, True, False]))
        self.assertFalse(alg.any([False, False, False]))

    def test_all(self):
        """Test all."""

        self.assertTrue(alg.all([True, True, True]))
        self.assertFalse(alg.all([False, True, False]))

    def test_extract_columns(self):
        """
        Test extraction of columns for coverage.

        This currently is exercised naturally, so explicitly test even though it is not public.
        """

        # If a vector is passed in, just return the vector back.
        v = [1, 2, 3]
        self.assertEqual(list(alg._extract_cols(v, alg.shape(v))), [[1, 2, 3]])

    def test_zdiv(self):
        """Test zero dividing."""

        self.assertEqual(alg.zdiv(4, 0), 0)

    def test_order(self):
        """Test order."""

        self.assertEqual(alg.order(0), 0)
        self.assertEqual(alg.order(20), 1)
        self.assertEqual(alg.order(2), 0)
        self.assertEqual(alg.order(0.002), -3)

    def test_min_max(self):
        """Test getting the minimum and maximum value."""

        self.assertEqual(alg.minmax([-4, 2, 8, 1]), (-4, 8))

        with self.assertRaises(ValueError):
            alg.minmax([])

    def test_sign(self):
        """Test sign."""

        self.assertEqual(alg.sign(-3), -1)
        self.assertEqual(alg.sign(3), 1)
        self.assertEqual(alg.sign(-0.0), -0.0)
        self.assertEqual(math.copysign(1, alg.sign(-0.0)), -1.0)
        self.assertEqual(alg.sign(0.0), 0.0)
        self.assertEqual(math.copysign(1, alg.sign(0.0)), 1.0)
        self.assertTrue(math.isnan(alg.sign(math.nan)))
        self.assertEqual(math.copysign(1, alg.sign(-math.nan)), -1)
        self.assertTrue(math.isnan(alg.sign(-math.nan)))
        self.assertEqual(math.copysign(1, alg.sign(math.nan)), 1)

    def test_solve_newton_and_halley(self):
        """Test solving with Newton."""

        def f0(x):
            return 2 * x ** 3 - 3 * x ** 2 - 3 * x + 2


        def dx(x):
            return 6 * x ** 2 - 6 * x - 3


        def dx2(x):
            return 12 * x - 6

        # Newton
        self.assertEqual(alg.solve_newton(1, f0, dx), (0.5, True))
        # Halley
        self.assertEqual(alg.solve_newton(1, f0, dx, dx2), (0.5, True))
        # Ostrowski
        self.assertEqual(alg.solve_newton(1, f0, dx, ostrowski=True), (0.5, True))

    def test_pinv(self):
        """Test Moore-Penrose pseudo inverse."""

        m = [
            [0.4123907992659593, 0.3575843393838777, 0.1804807884018343],
            [0.21263900587151033, 0.7151686787677553, 0.07219231536073373],
            [0.019330818715591832, 0.11919477979462595, 0.9505321522496605]
        ]

        v = [0.047770200571454854, 0.02780940276126581, 0.22476064520055364]

        # Negative results can be returned
        result = alg.dot(alg.pinv(m), v)
        self.assertEqual(result, [6.938893903907228e-17, 0.015208514422912755, 0.23455058216100522])

        wide = alg.pinv([[4, 5], [3, 3], [9, 7]])
        self.assertEqual(alg.dot(wide, [3, 5, 6]), [0.296407185628742, 0.5389221556886239])

        tall = alg.pinv([[4, 5, 3], [9, 7, 3]])
        self.assertEqual(alg.dot(tall, [3, 5]), [0.28727272727272735, 0.2818181818181817, 0.1472727272727271])

        p = alg.pinv([[0.0, 0.0], [0.0, 0.0]])
        self.assertEqual(p, [[0.0, 0.0], [0.0, 0.0]])

        p = alg.pinv([[-896, -896], [-19, -19]])
        self.assertEqual(
            p,
            [[-0.0005577848967288655, -1.1828027944027278e-05], [-0.0005577848967288655, -1.1828027944027278e-05]]
        )

        self.assertEqual(
            alg.pinv(
                [[[[8, 9], [4, 2]],
                  [[6, 2], [7, 1]]],
                 [[[7, 3], [6, 1]],
                  [[6, 4], [2, 2]]]]
            ),
            [[[[-0.1, 0.45], [0.20000000000000007, -0.40000000000000024]],
              [[-0.12500000000000006, 0.25], [0.8750000000000002, -0.7500000000000001]]],
             [[[-0.0909090909090909, 0.27272727272727276],
               [0.5454545454545454, -0.6363636363636364]],
              [[0.5000000000000001, -1.0000000000000002],
               [-0.49999999999999994, 1.5000000000000002]]]]
        )

        with self.assertRaises(ValueError):
            alg.pinv([1, 2, 3])

    def test_svd(self):
        """Test singular value decomposition."""

        r = alg.svd([[4, 5], [3, 3], [9, 7]])
        self.assertEqual(
            r,
            (
                [
                    [-0.4610004479435516, -0.8244356590165908, -0.3283053930987498],
                    [-0.3094744298689924, -0.19737303812683718, 0.9301986137797907],
                    [-0.8316875400371866, 0.5304241019811053, -0.16415269654937478]
                ],
                [13.682688482364616, 1.335678065465881],
                [
                    [-0.7496781758158658, 0.66180256323574],
                    [-0.66180256323574, -0.7496781758158658]
                ]
            )
        )

        r = alg.svd([[4, 5], [3, 3], [9, 7]], compute_uv=False)
        self.assertEqual(r, [13.682688482364616, 1.335678065465881])

        r = alg.svd([[4, 5, 3], [9, 7, 3]])
        self.assertEqual(
            r,
            (
                [[-0.8620053963543735, 0.5068990990877176],
                 [0.5068990990877176, 0.8620053963543735]],
                [1.7193878535843496, 13.639783920903831],
                [[0.6479458977504693, 0.7174340165714145, 0.25584085962673253],
                 [-0.44302586328610233, 0.6282015404061778, -0.6396021490668312],
                 [-0.6195919609290794, 0.3010834709802459, 0.7248824356090755]]
            )
        )

        r = alg.svd([[4, 5, 3], [9, 7, 3]], compute_uv=False)
        self.assertEqual(r, [1.7193878535843496, 13.639783920903831])

        self.assertEqual(
            alg.svd(
                [[[[8, 9], [4, 2]],
                  [[6, 2], [7, 1]]],
                 [[[7, 3], [6, 1]],
                  [[6, 4], [2, 2]]]],
                compute_uv=False
            ),
            [[[1.5687405878887022, 12.74908047538765],
              [9.448977704014812, 0.8466524369721866]],

             [[9.680328785854748, 1.1363250405372183],
              [7.72865690108165, 0.5175543501536712]]]
        )

        self.assertEqual(
            alg.svd(
                [[[[8, 9], [4, 2]],
                  [[6, 2], [7, 1]]],
                 [[[7, 3], [6, 1]],
                  [[6, 4], [2, 2]]]]
            ),
            (
                [[[[0.3310069414355005, 0.9436283191604176],
                   [-0.9436283191604177, 0.3310069414355005]],

                  [[-0.6659918587924756, 0.7459590096125545],
                   [-0.7459590096125545, -0.6659918587924756]]],


                 [[[-0.7833356929204806, 0.6215988997712197],
                   [-0.6215988997712197, -0.7833356929204804]],

                  [[-0.9327218431547384, 0.36059667677618457],
                   [-0.3605966767761846, -0.9327218431547382]]]],

                [[[1.5687405878887022, 12.74908047538765],
                  [9.448977704014812, 0.8466524369721866]],

                 [[9.680328785854748, 1.1363250405372183],
                  [7.72865690108165, 0.5175543501536712]]],

                [[[[-0.7180650222569405, 0.6959760224398106],
                   [0.6959760224398106, 0.7180650222569405]],

                  [[-0.9755197343863141, -0.21991190923380002],
                   [-0.21991190923380002, 0.9755197343863141]]],

                 [[[-0.9517180100879393, -0.3069736621833424],
                   [-0.3069736621833424, 0.9517180100879393]],

                  [[-0.8174155604703632, 0.5760484367663209],
                   [-0.5760484367663209, -0.8174155604703632]]]]
            )
        )

        self.assertEqual(
            alg.svd(
                [[[[8, 9], [4, 2], [8, 1]],
                  [[6, 2], [7, 1], [-5, 4]]],
                 [[[7, 3], [6, 1], [0, 3]],
                  [[6, 4], [2, 2], [3, 2]]]]
            ),
            (
                [[[[-0.8158630640566145, 0.5507567320964237, 0.17616606585441114],
                   [-0.3062515053282655, -0.15313848240894962, -0.9395523512235255],
                   [-0.49048697861648083, -0.8204971829664938, 0.2936101097573517]],

                  [[-0.569870147396332, -0.4512374914166255, 0.6867552267340334],
                   [-0.6662765703357557, -0.2354270586537413, -0.7075659911805193],
                   [0.4809610659170925, -0.8607896528151803, -0.16648611557188678]]],

                 [[[-0.7813492793972736, 0.1542880941638442, -0.6047218266150564],
                   [-0.6154226698548603, -0.3514431302100395, 0.7055087977175657],
                   [-0.10367372383625983, 0.9234083117600025, 0.36955222737586757]],

                  [[-0.8453992358072313, 0.29206186347510277, -0.447213595499958],
                   [-0.3265350901827962, -0.9451850796956719, -2.498001805406602e-16],
                   [-0.4226996179036156, 0.14603093173755108, 0.894427190999916]]]],

                [[[14.410248959653265, 4.72702072354374],
                  [10.488624053559748, 4.581349742498148]],

                 [[9.728206988477151, 3.0597367189587263],
                  [8.527894896946133, 0.5244126491991672]]],

                [[[[-0.8102432092178624, -0.5860937995887171],
                   [-0.5860937995887171, 0.8102432092178624]],

                  [[-0.9999368985633744, -0.011233827996719958],
                   [0.011233827996719957, -0.9999368985633742]]],

                 [[[-0.9417954393612556, -0.3361864815817844],
                   [-0.3361864815817844, 0.9417954393612556]],

                  [[-0.8200809852176114, 0.572247479404245],
                   [-0.572247479404245, -0.8200809852176114]]]]
            )
        )

        self.assertEqual(
            alg.svd(
                [[[[8, 9], [4, 2], [8, 1]],
                  [[6, 2], [7, 1], [-5, 4]]],
                 [[[7, 3], [6, 1], [0, 3]],
                  [[6, 4], [2, 2], [3, 2]]]],
                full_matrices=False
            ),
            (
                [[[[-0.8158630640566145, 0.5507567320964237],
                   [-0.3062515053282655, -0.15313848240894962],
                   [-0.49048697861648083, -0.8204971829664938]],

                  [[-0.569870147396332, -0.4512374914166255],
                   [-0.6662765703357557, -0.2354270586537413],
                   [0.4809610659170925, -0.8607896528151803]]],

                 [[[-0.7813492793972736, 0.1542880941638442],
                   [-0.6154226698548603, -0.3514431302100395],
                   [-0.10367372383625983, 0.9234083117600025]],

                  [[-0.8453992358072313, 0.29206186347510277],
                   [-0.3265350901827962, -0.9451850796956719],
                   [-0.4226996179036156, 0.14603093173755108]]]],

                [[[14.410248959653265, 4.72702072354374],
                  [10.488624053559748, 4.581349742498148]],

                 [[9.728206988477151, 3.0597367189587263],
                  [8.527894896946133, 0.5244126491991672]]],

                [[[[-0.8102432092178624, -0.5860937995887171],
                   [-0.5860937995887171, 0.8102432092178624]],

                  [[-0.9999368985633744, -0.011233827996719958],
                   [0.011233827996719957, -0.9999368985633742]]],

                 [[[-0.9417954393612556, -0.3361864815817844],
                   [-0.3361864815817844, 0.9417954393612556]],

                  [[-0.8200809852176114, 0.572247479404245],
                   [-0.572247479404245, -0.8200809852176114]]]]
            )
        )

        self.assertEqual(
            alg.svd(
                [[[[8, 9, 4], [2, 8, 1]],
                  [[6, 2, 7], [1, -5, 4]]],
                 [[[7, 3, 6], [1, 0, 3]],
                  [[6, 4, 2], [2, 3, 2]]]]
            ),
            (
                [[[[-0.8506508083520399, 0.5257311121191337],
                   [-0.5257311121191337, -0.8506508083520399]],

                  [[-0.921852697725676, -0.3875404542701232],
                   [-0.38754045427012307, 0.9218526977256758]]],

                 [[[-0.9641817474962142, -0.2652424509673116],
                   [-0.2652424509673116, 0.9641817474962142]],

                  [[-0.8864236441339941, 0.4628748460655541],
                   [-0.4628748460655541, -0.8864236441339941]]]],

                 [[[14.760051726365678, 3.484375558835424],
                   [9.954367526977135, 5.648943895797081]],

                  [[10.043774073494474, 1.767088668007424],
                   [8.403636584041795, 1.5423657683423768]]],

                [[[[-0.532292761347193, 0.7187937229952555, -0.44721359549995787],
                   [-0.8036358132087726, -0.5951213991516976, -2.7755575615628914e-17],
                   [-0.2661463806735964, 0.3593968614976277, 0.8944271909999159]],

                  [[-0.5945788745075109, -0.24843405312260414, -0.764693718581797],
                   [0.009442777318048962, -0.9531594748488608, 0.3023207724625709],
                   [-0.8039818380696813, 0.172532712129958, 0.569074395223663]]],

                 [[[-0.6983943119501383, -0.5050767544570185, -0.50709255283711],
                   [-0.28799385781905146, -0.4503041456313564, 0.8451542547285165],
                   [-0.6552136467551577, 0.7362904647857248, 0.1690308509457035]],

                  [[-0.7430463579056664, 0.651208558139096, 0.1543033499620918],
                   [-0.5871647429522041, -0.5237224299965502, -0.6172133998483675],
                   [-0.3211225227806299, -0.5492196556250589, 0.7715167498104597]]]]
            )
        )

        self.assertEqual(
            alg.svd(
                [[[[8, 9, 4], [2, 8, 1]],
                  [[6, 2, 7], [1, -5, 4]]],
                 [[[7, 3, 6], [1, 0, 3]],
                  [[6, 4, 2], [2, 3, 2]]]],
                full_matrices=False
            ),
            (
                [[[[-0.8506508083520399, 0.5257311121191337],
                   [-0.5257311121191337, -0.8506508083520399]],

                  [[-0.921852697725676, -0.3875404542701232],
                   [-0.38754045427012307, 0.9218526977256758]]],

                 [[[-0.9641817474962142, -0.2652424509673116],
                   [-0.2652424509673116, 0.9641817474962142]],

                  [[-0.8864236441339941, 0.4628748460655541],
                   [-0.4628748460655541, -0.8864236441339941]]]],

                [[[14.760051726365678, 3.484375558835424],
                  [9.954367526977135, 5.648943895797081]],

                 [[10.043774073494474, 1.767088668007424],
                  [8.403636584041795, 1.5423657683423768]]],

                [[[[-0.532292761347193, 0.7187937229952555],
                   [-0.8036358132087726, -0.5951213991516976],
                   [-0.2661463806735964, 0.3593968614976277]],

                  [[-0.5945788745075109, -0.24843405312260414],
                   [0.009442777318048962, -0.9531594748488608],
                   [-0.8039818380696813, 0.172532712129958]]],


                 [[[-0.6983943119501383, -0.5050767544570185],
                   [-0.28799385781905146, -0.4503041456313564],
                   [-0.6552136467551577, 0.7362904647857248]],

                  [[-0.7430463579056664, 0.651208558139096],
                   [-0.5871647429522041, -0.5237224299965502],
                   [-0.3211225227806299, -0.5492196556250589]]]]
            )
        )

        self.assertEqual(alg.svd([[], []]), ([[1.0, 0.0], [0.0, 1.0]], [], []))

        with self.assertRaises(ValueError):
            alg.svd([1, 2, 3])

    def test_qr(self):
        """Test QR decomposition."""

        r = alg.qr([[4, 5], [3, 3], [9, 7]])
        self.assertEqual(
            r,
            ([[-0.3885143449429056, -0.860971644501641],
              [-0.2913857587071792, -0.22321487079672198],
              [-0.8741572761215376, 0.45705902115519237]],
             [[-10.295630140986997, -8.93582993368683], [0.0, -1.7750896868120227]])
        )

        r = alg.qr([[4, 5], [3, 3], [9, 7]], mode='r')
        self.assertEqual(r, [[-10.295630140986997, -8.93582993368683], [0.0, -1.7750896868120227]])

        r = alg.qr([[4, 5], [3, 3], [9, 7]], mode='complete')
        self.assertEqual(
            r,
            ([[-0.3885143449429056, -0.860971644501641, -0.32830539309874984],
              [-0.2913857587071792, -0.22321487079672198, 0.9301986137797906],
              [-0.8741572761215376, 0.45705902115519237, -0.1641526965493747]],
             [[-10.295630140986997, -8.93582993368683],
              [0.0, -1.7750896868120227],
              [0.0, 0.0]])
        )

        r = alg.qr([[4, 5], [3, 3], [9, 7]], mode='raw')
        self.assertEqual(
            r,
            ([[-10.295630140986997, -8.93582993368683],
              [0.2098543380329, -1.7750896868120227]],
             [1.3885143449429056, 1.0425362362747328])
        )

        r = alg.qr([[4, 5, 3], [9, 7, 3]])
        self.assertEqual(
            r,
            ([[-0.4061384660534477, -0.9138115486202573],
              [-0.9138115486202573, 0.4061384660534475]],
             [[-9.848857801796106, -8.42737317060904, -3.959850044021115],
              [0.0, -1.726088480727153, -1.5230192477004296]])
        )

        r = alg.qr([[4, 5, 3], [9, 7, 3]], mode='r')
        self.assertEqual(
            r,
            [[-9.848857801796106, -8.42737317060904, -3.959850044021115],
             [0.0, -1.726088480727153, -1.5230192477004296]]
        )

        r = alg.qr([[4, 5, 3], [9, 7, 3]], mode='complete')
        self.assertEqual(
            r,
            ([[-0.4061384660534477, -0.9138115486202573],
              [-0.9138115486202573, 0.4061384660534475]],
             [[-9.848857801796106, -8.42737317060904, -3.959850044021115],
              [0.0, -1.726088480727153, -1.5230192477004296]])

        )

        r = alg.qr([[4, 5, 3], [9, 7, 3]], mode='raw')
        self.assertEqual(
            r,
            ([[-9.848857801796106, -8.42737317060904, -3.959850044021115],
              [0.6498730890884561, -1.726088480727153, -1.5230192477004296]],
             [1.4061384660534477, 0.0])
        )

        m = [[1, 3, 6], [1, 2, 2], [1, 3, 8]]
        r = alg.qr(m)
        self.assertEqual(
            r,
            ([[-0.5773502691896257, 0.4082482904638629, -0.7071067811865476],
              [-0.5773502691896257, -0.816496580927726, 2.7755575615628914e-16],
              [-0.5773502691896257, 0.40824829046386324, 0.7071067811865474]],
             [[-1.7320508075688772, -4.618802153517006, -9.237604307034012],
              [0.0, 0.8164965809277258, 4.08248290463863],
              [0.0, 0.0, 1.4142135623730943]])
        )

        r = alg.qr(m, mode='r')
        self.assertEqual(
            r,
            [[-1.7320508075688772, -4.618802153517006, -9.237604307034012],
             [0.0, 0.8164965809277258, 4.08248290463863],
             [0.0, 0.0, 1.4142135623730943]]
        )

        r = alg.qr(m, mode='complete')
        self.assertEqual(
            r,
            ([[-0.5773502691896257, 0.4082482904638629, -0.7071067811865476],
              [-0.5773502691896257, -0.816496580927726, 2.7755575615628914e-16],
              [-0.5773502691896257, 0.40824829046386324, 0.7071067811865474]],
             [[-1.7320508075688772, -4.618802153517006, -9.237604307034012],
              [0.0, 0.8164965809277258, 4.08248290463863],
              [0.0, 0.0, 1.4142135623730943]])
        )

        r = alg.qr(m, mode='raw')
        self.assertEqual(
            r,
            ([[-1.7320508075688772, -4.618802153517006, -9.237604307034012],
              [0.36602540378443865, 0.8164965809277258, 4.08248290463863],
              [0.36602540378443865, -0.13165249758739603, 1.4142135623730943]],
             [1.5773502691896257, 1.9659258262890682, 0.0])
        )

        r = alg.qr([[-896, -896], [-19, -19]])
        self.assertEqual(
            r,
            ([[-0.9997752422110318, -0.02120059107367143],
              [-0.02120059107367143, 0.9997752422110316]],
             [[896.2014282514842, 896.2014282514842], [0.0, 3.552713678800501e-15]])
        )

        self.assertEqual(
            alg.qr(
                [[[[8, 9], [4, 2]],
                  [[6, 2], [7, 1]]],
                 [[[7, 3], [6, 1]],
                  [[6, 4], [2, 2]]]]
            ),
            ([[[[-0.8944271909999157, -0.4472135954999579],
                [-0.4472135954999579, 0.8944271909999159]],
               [[-0.6507913734559685, -0.7592566023652966],
                [-0.7592566023652966, 0.6507913734559685]]],
              [[[-0.7592566023652967, -0.6507913734559686],
                [-0.6507913734559686, 0.7592566023652966]],
               [[-0.948683298050514, -0.31622776601683794],
                [-0.31622776601683794, 0.9486832980505138]]]],
             [[[[-8.94427190999916, -8.94427190999916],
                [0.0, -2.23606797749979]], [[-9.219544457292887, -2.0608393492772334],
                [0.0, -0.8677218312746247]]],
              [[[-9.21954445729289, -2.928561180551858],
                [0.0, -1.1931175180026092]],
               [[-6.32455532033676, -4.427188724235732],
                [0.0, 0.6324555320336758]]]])
        )

        self.assertEqual(
            alg.qr(
                [[[[8, 9], [4, 2]],
                  [[6, 2], [7, 1]]],
                 [[[7, 3], [6, 1]],
                  [[6, 4], [2, 2]]]],
                mode='r'
            ),
            [[[[-8.94427190999916, -8.94427190999916],
               [0.0, -2.23606797749979]],

              [[-9.219544457292887, -2.0608393492772334],
               [0.0, -0.8677218312746247]]],


             [[[-9.21954445729289, -2.928561180551858],
               [0.0, -1.1931175180026092]],

              [[-6.32455532033676, -4.427188724235732],
               [0.0, 0.6324555320336758]]]]
        )

        self.assertEqual(alg.qr([[], []]), ([[1.0, 0.0], [0.0, 1.0]], [[], []]))
        self.assertEqual(alg.qr([[], []], mode='raw'), ([[], []], []))

        m = [[1, 3, 6], [1, 2, 2], [1, 3, 8]]
        with self.assertRaises(ValueError):
            r = alg.qr(m, mode='bad')

        with self.assertRaises(ValueError):
            alg.qr([1, 2, 3])

    def test_svdvals(self):
        """Get just the SVD values."""

        svd = alg.svdvals([[8, 9], [4, 2]])
        self.assertTrue(svd, [1.5687405878887022, 12.74908047538765])

        svd = alg.svdvals([[4, 5], [3, 3], [9, 7]])
        self.assertTrue(svd, [13.682688482364616, 1.335678065465881])

        svd = alg.svdvals([[4, 5, 3], [9, 7, 3]])
        self.assertTrue(svd, [1.7193878535843492, 13.639783920903826])

        svd = alg.svdvals([[1, 2], [1, 2]])
        self.assertTrue(svd, [2.220446049250313e-16, 3.162277660168379])

    def test_matrix_rank(self):
        """Test matrix ranks."""

        self.assertEqual(alg.matrix_rank([[4, 5, 3], [9, 7, 3]]), 2)
        self.assertEqual(alg.matrix_rank([[4, 5], [3, 9], [7, 3]]), 2)
        self.assertEqual(alg.matrix_rank([[0.0, 0.0], [0.0, 0.0]]), 0)
        self.assertEqual(alg.matrix_rank([[-896, -896], [-19, -19]]), 1)
        self.assertEqual(
            alg.matrix_rank(
                [[[[8, 9], [4, 2]],
                  [[6, 2], [7, 1]]],
                 [[[7, 3], [6, 1]],
                  [[6, 4], [2, 2]]]]
            ),
            [[2, 2], [2, 2]]
        )

        with self.assertRaises(ValueError):
            alg.matrix_rank([1, 2, 3])

    def test_fnnls(self):
        """Test fast non-negative least squares method."""

        m = [
            [0.4123907992659593, 0.3575843393838777, 0.1804807884018343],
            [0.21263900587151033, 0.7151686787677553, 0.07219231536073373],
            [0.019330818715591832, 0.11919477979462595, 0.9505321522496605]
        ]

        v = [0.047770200571454854, 0.02780940276126581, 0.22476064520055364]

        res = alg.fnnls(m, v)
        b = alg.dot(alg.pinv(m), v)

        # We should have no negative values, but we should be close to the `pinv` approach.
        self.assertTrue(all(_a >= 0 for _a in res[0]))
        self.assertTrue(res[1] < 1e-10)
        self.assertTrue(all(math.isclose(_a, _b, rel_tol=1e-10, abs_tol=1e-11) for _a, _b in zip(res[0], b)))

        with self.assertRaises(ValueError):
            alg.fnnls(m, v + [1.0])

        with self.assertRaises(ValueError):
            alg.fnnls([], v + [1.0])

        # This is purposely beyond the range of a reasonable solution
        # There will be residual
        v = [0.6369580483012911, 0.262700212011267, 4.994106574466074e-17]
        res = alg.fnnls(m, v)

        # We should have no negative values, but we will have residual
        self.assertFalse(res[1] < 1e-10)
        self.assertTrue(all(_a >= 0 for _a in res[0]))
        self.assertEqual(res[0], [1.477061311287275, 0.0, 0.0])

    def test_bisect(self):
        """Test bisect."""

        from coloraide.easing import _bezier

        a, b, c = .5, -3, 2
        t = 0.9
        b = _bezier(a, b, c)(t)
        f0 = _bezier(a, b, c, y=t)
        r, converged = alg.solve_bisect(0.0, 1.0, f0, start=0.5)
        self.assertTrue(converged)
        self.assertEqual(r, 0.4539687953174507)

    def test_solve_poly(self):
        """Test cubic solving."""

        # Cubic
        self.assertEqual(alg.solve_poly([0.5, -3, 2, 0]), [5.23606797749979, 0.7639320225002102, 0.0])
        self.assertEqual(alg.solve_poly([0.5, -3, 2, -0.9]), [5.310615451738684])
        self.assertEqual(alg.solve_poly([1, -3, 2, 9]), [-1.240040987469445])

        # Quadratic
        self.assertEqual(alg.solve_poly([1, 8, 16]), [-4])
        self.assertEqual(alg.solve_poly([0, 1, 8, 16]), [-4])
        self.assertEqual(alg.solve_poly([3, -9, -81]), [6.908326913195984, -3.9083269131959844])
        self.assertEqual(alg.solve_poly([1, 4, 16]), [])

        # Linear
        self.assertEqual(alg.solve_poly([3, -9]), [3])
        self.assertEqual(alg.solve_poly([0, 0, 3, -9]), [3])

        # 0 degree
        self.assertEqual(alg.solve_poly([3]), [])
        self.assertEqual(alg.solve_poly([0, 0, 0, 3]), [])

        # 4th+ degree
        with self.assertRaises(ValueError):
            alg.solve_poly([1, 2, 3, 4, 5])

    def test_flip(self):
        """Test flip."""

        self.assertEqual(alg.flip(3), 3)

        self.assertEqual(alg.flip([1, 2, 3, 4]), [4, 3, 2, 1])

        m = alg.reshape(alg.arange(8), (2,2,2))

        self.assertEqual(
            alg.flip(m),
            [[[7, 6],
              [5, 4]],
             [[3, 2],
              [1, 0]]]
        )

        self.assertEqual(
            alg.flip(m, 0),
            [[[4, 5],
              [6, 7]],
             [[0, 1],
              [2, 3]]]
        )

        self.assertEqual(
            alg.flip(m, 1),
            [[[2, 3],
              [0, 1]],
             [[6, 7],
              [4, 5]]]
        )

        self.assertEqual(
            alg.flip(m, (2, 0)),
            [[[5, 4],
              [7, 6]],
             [[1, 0],
              [3, 2]]]
        )

        with self.assertRaises(ValueError):
            alg.flip(m, (2, 2))

        with self.assertRaises(ValueError):
            alg.flip(m, 3)

    def test_flipud(self):
        """Test flip on axis 0."""

        m = alg.reshape(alg.arange(8), (2,2,2))

        self.assertEqual(
            alg.flip(m, 0),
            alg.flipud(m)
        )

    def test_fliplr(self):
        """Test flip on axis 1."""

        m = alg.reshape(alg.arange(8), (2,2,2))

        self.assertEqual(
            alg.flip(m, 1),
            alg.fliplr(m)
        )

    def test_roll(self):
        """Test roll."""

        self.assertEqual(alg.roll(3, 1), 3)

        x = alg.arange(10)
        self.assertEqual(alg.roll(x, 2), [8, 9, 0, 1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(alg.roll(x, -2), [2, 3, 4, 5, 6, 7, 8, 9, 0, 1])

        x2 = alg.reshape(x, (2, 5))

        self.assertEqual(
            alg.roll(x2, (2, 1)),
            [[7, 8, 9, 0, 1],
             [2, 3, 4, 5, 6]]
        )

        self.assertEqual(
            alg.roll(x2, 1),
            [[9, 0, 1, 2, 3],
             [4, 5, 6, 7, 8]]
        )

        self.assertEqual(
            alg.roll(x2, -1),
            [[1, 2, 3, 4, 5],
             [6, 7, 8, 9, 0]]
        )

        self.assertEqual(
            alg.roll(x2, 1, axis=0),
            [[5, 6, 7, 8, 9],
             [0, 1, 2, 3, 4]]
        )

        self.assertEqual(
            alg.roll(x2, -1, axis=0),
            [[5, 6, 7, 8, 9],
             [0, 1, 2, 3, 4]]
        )

        self.assertEqual(
            alg.roll(x2, 1, axis=1),
            [[4, 0, 1, 2, 3],
             [9, 5, 6, 7, 8]]
        )

        self.assertEqual(
            alg.roll(x2, -1, axis=1),
            [[1, 2, 3, 4, 0],
             [6, 7, 8, 9, 5]]
        )

        self.assertEqual(
            alg.roll(x2, (1, 1), axis=(1, 0)),
            [[9, 5, 6, 7, 8],
             [4, 0, 1, 2, 3]]
        )

        self.assertEqual(
            alg.roll(x2, (2, 1), axis=(1, 0)),
            [[8, 9, 5, 6, 7],
             [3, 4, 0, 1, 2]]
        )

        self.assertEqual(
            alg.roll(x2, (2, 1), axis=(-1, 0)),
            [[8, 9, 5, 6, 7],
             [3, 4, 0, 1, 2]]
        )

    def test_unique(self):
        """Test unique."""

        self.assertEqual(alg.unique([1, 1, 2, 2, 3, 3]), [1, 2, 3])
        self.assertEqual(alg.unique([[1, 1], [2, 3]]), [1, 2, 3])
        self.assertEqual(
            alg.unique([[1, 0, 0], [1, 0, 0], [2, 3, 4]], axis=0),
            [[1, 0, 0], [2, 3, 4]]
        )

        m = [1, 2, 6, 4, 2, 3, 2]
        self.assertEqual(
            alg.unique(m, return_index=True),
            ([1, 2, 3, 4, 6], [0, 1, 5, 3, 2])
        )
        self.assertEqual(
            alg.unique(m, return_inverse=True),
            ([1, 2, 3, 4, 6], [0, 1, 4, 3, 1, 2, 1])
        )
        self.assertEqual(
            alg.unique(m, return_counts=True),
            ([1, 2, 3, 4, 6], [1, 3, 1, 1, 1])
        )

        with self.assertRaises(ValueError):
            alg.unique([[1, 0, 0], [1, 0, 0], [2, 3, 4]], axis=2)

    def test_ndenumerate(self):
        """Test N-D array enumeration."""

        self.assertEqual(
            list(alg.ndenumerate([[1, 0, 0], [1, 0, 0], [2, 3, 4]])),
            [
                ((0, 0), 1), ((0, 1), 0), ((0, 2), 0),
                ((1, 0), 1),((1, 1), 0), ((1, 2), 0),
                ((2, 0), 2), ((2, 1), 3), ((2, 2), 4)
            ]
        )


def test_pprint(capsys):
    """Test matrix print."""

    m = [[[[41, 47, 53], [59, 65, 71]],
          [[95, 109, 123], [137, 151, 165]],
          [[149, 171, 193], [215, 237, 259]]],
         [[[203, 233, 263], [293, 323, 353]],
          [[257, 295, 333], [371, 409, 447]],
          [[311, 357, 403], [449, 495, 541]]]]

    alg.pprint(m)
    assert (
        capsys.readouterr().out == """[[[[41, 47, 53],
   [59, 65, 71]],

  [[95, 109, 123],
   [137, 151, 165]],

  [[149, 171, 193],
   [215, 237, 259]]],


 [[[203, 233, 263],
   [293, 323, 353]],

  [[257, 295, 333],
   [371, 409, 447]],

  [[311, 357, 403],
   [449, 495, 541]]]]
"""
    )

    alg.pprint(3)
    assert capsys.readouterr().out == '3\n'
