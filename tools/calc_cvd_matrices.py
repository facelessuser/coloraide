# -*- coding: utf-8 -*-
"""Calculate the required matrices for simulating color vision deficiency."""
import sys
import os

sys.path.insert(0, os.getcwd())

import tools.calc_xyz_transform as xyzt  # noqa: E402
from coloraide import algebra as alg  # noqa: E402
from coloraide import Color  # noqa: E402

# Calculated using our own `calc_xyz_transform.py`
RGB_TO_XYZ, XYZ_TO_RGB = xyzt.get_matrix(xyzt.white_d65, 'srgb')

M = [
    [0.15514, 0.54312, -0.03286],
    [-0.15514, 0.45684, 0.03286],
    [0, 0, 0.01608]
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
T = alg.dot(M, RGB_TO_XYZ)
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

print('===== ACHROMATOPSIA =====')
pprint([RGB_TO_XYZ[1]] * 3)

####################
# Brettel matrices
####################
LMS_WHITE = alg.dot(T, [1, 1, 1])

# http://cvrl.ioo.ucl.ac.uk/cie.htm: CIE 1931 CMFs
LMS_475 = alg.dot(M, [0.1421, 0.1126, 1.0419])
LMS_575 = alg.dot(M, [0.8425, 0.9154, 0.0018])
LMS_485 = alg.dot(M, [0.05795, 0.1693, 0.6162])
LMS_660 = alg.dot(M, [0.1649, 0.0610, 0.0000])

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
