# -*- coding: utf-8 -*-
"""Calculate the required matrices for simulating color vision deficiency."""
import sys
import os

sys.path.insert(0, os.getcwd())

from coloraide import algebra as alg  # noqa: E402
from coloraide import Color  # noqa: E402

# Smith & Pokorny (1975) 2-deg cone fundamentals
M = [
    [0.15514, 0.54312, -0.03286],
    [-0.15514, 0.45684, 0.03286],
    [0, 0, 0.01608]
]

# Linear sRGB to Judd-Vos corrected XYZ (approximation)
# https://vision.psychol.cam.ac.uk/jdmollon/papers/colourmaps.pdf
RGB_TO_XYZ = [
    [40.9568, 35.5041, 17.9167],
    [21.3389, 70.6743, 7.9868],
    [1.86297, 11.462, 91.2367]
]


def pprint(value):
    """Print the matrix."""

    print('[', end='')
    first = True
    for v in value:
        if first:
            first = False
        else:
            print(',\n ', end='')
        print(v, end='')
    print(']')


####################
# General matrices
####################
T = alg.dot(M, alg.divide(RGB_TO_XYZ, 100))
INV_T = alg.inv(T)

print('===== LRGB to LMS =====')
pprint(T)

print('===== LMS to LRGB =====')
pprint(INV_T)

print('===== XYZ to LMS =====')
pprint(M)

print('===== LMS to XYZ =====')
pprint(alg.inv(M))

####################
# Viénot matrices
# http://vision.psychol.cam.ac.uk/jdmollon/papers/colourmaps.pdf
####################
print('===== VIENOT PROTAN =====')
white = Color('white').convert('srgb-linear')
blue = Color('blue').convert('srgb-linear')
lw, mw, sw = alg.dot(T, white[:-1])
lb, mb, sb = alg.dot(T, blue[:-1])
q1 = (lb * sw - lw * sb) / (mb * sw - mw * sb)
q2 = (lb * mw - lw * mb) / (sb * mw - sw * mb)
sp = [[0.0, q1, q2], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
m = alg.multi_dot([INV_T, sp, T])
pprint(m)

print('===== VIENOT DEUTAN =====')
white = Color('white').convert('srgb-linear')
blue = Color('blue').convert('srgb-linear')
lw, mw, sw = alg.dot(T, white[:-1])
lb, mb, sb = alg.dot(T, blue[:-1])
q1 = (mb * sw - mw * sb) / (lb * sw - lw * sb)
q2 = (mb * lw - mw * lb) / (sb * lw - sw * lb)
sd = [[1.0, 0.0, 0.0], [q1, 0.0, q2], [0.0, 0.0, 1.0]]
m = alg.multi_dot([INV_T, sd, T])
pprint(m)

print('===== VIENOT TRITAN =====')
white = Color('white').convert('srgb-linear')
red = Color('red').convert('srgb-linear')
lw, mw, sw = alg.dot(T, white[:-1])
lb, mb, sb = alg.dot(T, red[:-1])
q1 = (sb * mw - sw * mb) / (lb * mw - lw * mb)
q2 = (sb * lw - sw * lb) / (mb * lw - mw * lb)
st = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [q1, q2, 0.0]]
m = alg.multi_dot([INV_T, st, T])
pprint(m)

####################
# Brettel matrices
# https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.496.7153&rep=rep1&type=pdf
####################
LMS_WHITE = alg.dot(T, [1, 1, 1])

# http://cvrl.ioo.ucl.ac.uk/: CIE 1931 2-deg, XYZ CMFs modified by Judd (1951) and Vos (1978)
LMS_475 = alg.dot(M, [1.3287E-01, 1.1284E-01, 9.422E-01])
LMS_575 = alg.dot(M, [8.4394E-01, 9.1558E-01, 1.9706E-03])
LMS_485 = alg.dot(M, [5.6985E-02, 1.6987E-01, 5.864E-01])
LMS_660 = alg.dot(M, [1.6161E-01, 6.1E-02, 1.1906E-05])

AXIS = alg.identity(3)
NAMES = ['PROTAN', 'DEUTAN', 'TRITAN']
WINGS = [(LMS_475, LMS_575), (LMS_475, LMS_575), (LMS_485, LMS_660)]

for axis, name, wings in zip(AXIS, NAMES, WINGS):
    wing1, wing2 = wings

    v1 = alg.cross(LMS_WHITE, wing1)
    v2 = alg.cross(LMS_WHITE, wing2)
    va = alg.cross(LMS_WHITE, axis)

    # Make sure the wings are on the correct sides
    if alg.dot(va, v1) < 0:
        v1, v2 = v2, v1

    index = axis.index(1.0)
    m1 = alg.identity(3)
    m2 = alg.identity(3)
    if index == 0:
        # Protan
        m1[index] = [0.0, -v1[1] / v1[0], -v1[2] / v1[0]]
        m2[index] = [0.0, -v2[1] / v2[0], -v2[2] / v2[0]]
    elif index == 1:
        # Deutan
        m1[index] = [-v1[0] / v1[1], 0.0, -v1[2] / v1[1]]
        m2[index] = [-v2[0] / v2[1], 0.0, -v2[2] / v2[1]]
    else:
        # Tritan
        m1[index] = [-v1[0] / v1[2], -v1[1] / v1[2], 0.0]
        m2[index] = [-v2[0] / v2[2], -v2[1] / v2[2], 0.0]

    print('===== BRETTEL {} ====='.format(name))
    print('--- Wing 1 (LMS to Linear sRGB included) ---')
    pprint(alg.dot(INV_T, m1))
    print('--- Wing 2 (LMS to Linear sRGB included) ---')
    pprint(alg.dot(INV_T, m2))
    print('--- Separating axis ---')
    print(va)
