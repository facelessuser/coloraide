"""Calculate CATs."""
import numpy as np

np.set_printoptions(precision=16, sign='-')

white_d65 = [0.95047, 1.00000, 1.08883]
white_d50 = [0.96422, 1.00000, 0.82521]

wd50 = np.array(white_d50).reshape(3, 1)
wd65 = np.array(white_d65).reshape(3, 1)

bradford_m = np.asarray(
    [
        [0.8951000, 0.2664000, -0.1614000],
        [-0.7502000, 1.7135000, 0.0367000],
        [0.0389000, -0.0685000, 1.0296000]
    ]
)

von_kries_m = np.asarray(
    [
        [0.4002400, 0.7076000, -0.0808100],
        [-0.2263000, 1.1653200, 0.0457000],
        [0.0000000, 0.0000000, 0.9182200]
    ]
)


def pre_calculate_cat(src_white, dest_white, m, mi):
    """Calculate CAT."""

    src = np.dot(m, src_white)
    dest = np.dot(m, dest_white)
    m2 = np.divide(dest, src)

    m3 = [
        [m2[0][0], 0, 0],
        [0, m2[1][0], 0],
        [0, 0, m2[2][0]]
    ]
    to_d50 = np.dot(mi, np.dot(m3, m))
    to_d65 = np.linalg.inv(to_d50)
    return to_d65, to_d50


if __name__ == '__main__':
    # Since we now calculate transform matrices on the fly and then cache them,
    # it isn't strictly necessary for us to pre-calculate D50 and D65 transform
    # matrices anymore. While we take a performance hit on the first calculation,
    # afterwards, we just retrieve the previously calculated matrices from the cache.
    # If we need the pre-calculated matrices in the future, we can just uncomment
    # them below.

    print('===== Bradford M =====')
    print(bradford_m)

    mi = np.linalg.inv(bradford_m)
    print('===== Bradford M^1 =====')
    print(mi)

    # ```
    # to_d65, to_d50 = pre_calculate_cat(wd65, wd50, bradford_m, mi)
    #
    # print('===== Bradford To D65 =====')
    # print(to_d65)
    #
    # print('===== Bradford To D50 =====')
    # print(to_d50)
    # ```

    print('===== von Kries M =====')
    print(von_kries_m)

    mi = np.linalg.inv(von_kries_m)
    print('===== von Kries M^1 =====')
    print(mi)

    # ```
    # to_d65, to_d50 = pre_calculate_cat(wd65, wd50, von_kries_m, mi)
    #
    # print('===== von Kries To D65 =====')
    # print(to_d65)
    #
    # print('===== von Kries To D50 =====')
    # print(to_d50)
    # ```
