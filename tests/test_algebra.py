"""Test Algebra."""
import unittest
from coloraide import algebra as alg
import math


class TestAlgebra(unittest.TestCase):
    """Test Algebra."""

    def test_nlog(self):
        """Test `nlog`."""

        self.assertEqual(alg.nlog(-3), -1.0986122886681098)

    def test_cross(self):
        """Test cross product."""

        self.assertEqual(
            alg.cross([1, 2, 3], [4, 5, 6]),
            [-3, 6, -3]
        )

        self.assertEqual(
            alg.cross([1, 2], [4, 5]),
            [-3]
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
            [[6], [3]]
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
              [[-0.12500000000000003, 0.25000000000000006],
               [0.8750000000000001, -0.7500000000000002]]],
             [[[-0.09090909090909094, 0.27272727272727276],
               [0.5454545454545455, -0.6363636363636365]],
              [[0.4999999999999999, -0.9999999999999998],
               [-0.4999999999999999, 1.4999999999999998]]]]
        )

        with self.assertRaises(ValueError):
            alg.inv([[8, 9, 1], [4, 2, 1]])

        with self.assertRaises(ValueError):
            alg.inv([[0, 0], [0, 0]])

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

        self.assertEqual(
            list(alg.broadcast([3], [1, 2, 3])),
            [(3, 1), (3, 2), (3, 3)]
        )

        self.assertEqual(
            list(alg.broadcast(3, [1, 2, 3])),
            [(3, 1), (3, 2), (3, 3)]
        )

        self.assertEqual(
            list(alg.broadcast([1, 2, 3], 3)),
            [(1, 3), (2, 3), (3, 3)]
        )

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
            tuple()
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
            alg.reshape([1], tuple()),
            1
        )

        with self.assertRaises(ValueError):
            alg.reshape([1, 2], tuple())

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

        # Dimensions must be at least 2D
        with self.assertRaises(ValueError):
            alg.fill_diagonal([0, 0, 0], 3)

        # Dimensions over 2D require a equal dimensions
        with self.assertRaises(ValueError):
            alg.fill_diagonal(alg.zeros((3, 2, 4)), 3)

    def test_no_nan(self):
        """Test no `NaN`."""

        self.assertEqual(alg.no_nan(alg.NaN), 0)
        self.assertEqual(alg.no_nans([0, 1, 2, alg.NaN]), [0, 1, 2, 0])

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
            alg.dot([40, 0.3, 12, 9], m2),
            [[[1700.3, 2313.3], [2193.3, 725.6]], [[306.5, 2313.3], [2193.3, 183.9]]]
        )

        self.assertEqual(
            alg.dot(m2, [40, 12]),
            [[[692, 1732, 2772, 3812], [972, 1784, 2196, 3408]], [[452, 692, 932, 1172], [876, 1676, 2076, 3276]]]
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

    def test_apply_two_inputs(self):
        """Test apply with two inputs."""

        self.assertEqual(
            alg.apply(alg.npow, [[1, 2, 3], [4, 5, 6]], 2),
            [[1, 4, 9], [16, 25, 36]]
        )

    def test_apply_one_input(self):
        """Test apply with one input."""

        self.assertEqual(
            alg.apply(math.sqrt, [[1, 4, 9], [16, 25, 36]]),
            [[1, 2, 3], [4, 5, 6]]
        )
