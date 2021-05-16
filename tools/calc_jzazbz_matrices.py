"""Calculate Jzazbz matrices."""
import numpy as np

np.set_printoptions(precision=None, sign='-', floatmode='unique')

m1 = np.asfarray(
    [
        [0.41478972, 0.579999, 0.0146480],
        [-0.2015100, 1.120649, 0.0531008],
        [-0.0166008, 0.264800, 0.6684799]
    ]
)

m2 = np.asfarray(
    [
        [0.5, 0.5, 0],
        [3.524000, -4.066708, 0.542708],
        [0.199076, 1.096799, -1.295875]
    ]
)


if __name__ == "__main__":
    print('===== XYZ to LMS =====')
    print(m1)
    print('===== LMS to XYZ =====')
    print(np.linalg.inv(m1))
    print('===== PQ LMS to Izazbz =====')
    print(m2)
    print('===== Izazbz to PQ LMS =====')
    print(np.linalg.inv(m2))
