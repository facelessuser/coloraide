"""Calculate `oklab` matrices."""
import numpy as np

np.set_printoptions(precision=None, sign='-', floatmode='unique')


m1 = np.asfarray(
    [
        [0.4122214708, 0.2119034982, 0.0883024619],
        [0.5363325363, 0.6806995451, 0.2817188376],
        [0.0514459929, 0.1073969566, 0.6299787005]
    ]
)

m2 = np.asfarray(
    [
        [0.2104542553, 1.9779984951, 0.0259040371],
        [0.793617785, -2.428592205, 0.7827717662],
        [-0.0040720468, 0.4505937099, -0.808675766]
    ]
)


if __name__ == "__main__":
    print('===== sRGB Linear => lms =====')
    print(m1)
    print('===== lms -> sRGB Linear =====')
    print(np.linalg.inv(m1))
    print('===== lms ** 1/3 -> Oklab =====')
    print(m2)
    print('===== Oklab -> lms ** 1/3 =====')
    print(np.linalg.inv(m2))
