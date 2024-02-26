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
            alg.inv(
                [[[[8, 9], [4, 2]],
                  [[6, 2], [7, 1]]],
                 [[[7, 3], [6, 1]],
                  [[6, 4], [2, 2]]]]
            ),
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
        ),

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

        cbrt = alg.vectorize1(lambda x: alg.nth_root(x, 3))

        self.assertEqual(
            cbrt([8, 27]),
            [2, 3]
        )

        with self.assertRaises(TypeError):
            cbrt([8, 27], 4)

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

    def test_apply_two_inputs(self):
        """Test vectorize2 with two inputs."""

        npow = alg.vectorize2(alg.npow)
        self.assertEqual(
            npow([[1, 2, 3], [4, 5, 6]], 2),
            [[1, 4, 9], [16, 25, 36]]
        )

    def test_apply_one_input(self):
        """Test apply with one input."""

        sqrt = alg.vectorize1(math.sqrt)
        self.assertEqual(
            sqrt([[1, 4, 9], [16, 25, 36]]),
            [[1, 2, 3], [4, 5, 6]]
        )

        isnan = alg.vectorize1(math.isnan)
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

        m = [[0.1, 0.0], [1.0, 0.0], [0.0, .95], [1, 1]]
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

        m = [[0.1, 0.0], [1.0, 0.0], [0.0, .95], [1, 1]]
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
        e = [[0.01916714204221337, 0.1832287507130633, -0.0062749572162008015],
             [0.40726884019241044, 0.04836985569214323, -0.15606627471940138],
             [52.09999999999999, -7.766666666666662, -20.233333333333327],
             [-0.05851413543721229, -0.03550295857988176, 0.3019066403681789]]
        self.assertEqual(alg.solve(m, b), e)

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
        e = [[0.5297833935018049, -0.3561973525872442, -0.2111913357400721],
             [-0.23864959254947615, 0.6006984866123398, -0.2805587892898718],
             [0.20853080568720359, -0.10426540284360161, 0.32227488151658773]]
        self.assertEqual(alg.solve(m, b), e)

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
