"""Calculate `oklab` matrices."""
import numpy as np

np.set_printoptions(precision=None, sign='-', floatmode='unique')


m1 = np.asfarray(
    [
        [+0.8189330101, +0.0329845436, +0.0482003018],
        [+0.3618667424, +0.9293118715, +0.2643662691],
        [-0.1288597137, +0.0361456387, +0.6338517070]
    ]
)

m2 = np.asfarray(
    [
        [+0.2104542553, +1.9779984951, +0.0259040371],
        [+0.7936177850, -2.4285922050, +0.7827717662],
        [-0.0040720468, +0.4505937099, -0.8086757660]
    ]
)


if __name__ == "__main__":
    print('===== m1 =====')
    print(m1)
    print('===== m1^-1 =====')
    print(np.linalg.inv(m1))
    print('===== m2 =====')
    print(m2)
    print('===== m2^-1 =====')
    print(np.linalg.inv(m2))
