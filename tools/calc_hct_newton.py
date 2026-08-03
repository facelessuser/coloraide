"""
Calculate values for the Newton approximation of CAM16 J from HCT T (tone) approximation polynomial.

- Calculate a simple polynomial that describes a rough relationship between HCT T and CAM16 J. This
  is used to get an initial guess of CAM16 lightness (J) from HCT tone (T).
- Calculate the constant for the first derivative approximation for Newton's Method. It is too
  difficult to provide an exact first derivative for CAM16 J'. But we can calculate a reasonable
  approximation of the first derivative by dividing the rate of change by (Y / J) and seeing we
  get a fairly constant value. With that knowledge, we are able to derive an approximate formula
  of `J' ~= c * Y / J`. There is some deviation in the constant, but it is small enough that we
  can take the average and get good results. To further refine it, we can use Ostrowski's Method
  without having to estimate a second derivative.
"""
import sys
import os
import numpy as np

sys.path.insert(0, os.getcwd())

from coloraide.everything import ColorAll as Color
from coloraide.spaces import cam16
from coloraide.spaces import hct

env = hct.HCT.ENV

print('==== Positive Lightness ====')
# Calculate polynomial for a reasonable J guess with positive lightness
j = []
t = []
for r in range(200001):
    xyz = Color('srgb', [r / 100000] * 3).convert('xyz-d65')
    j.append(cam16.xyz_to_cam(xyz.coords(), env)[0])
    t.append(hct.y_to_lstar(xyz[1]))
print(np.polyfit(t, j, 2).tolist())

print('==== Negative Lightness ====')
# Calculate polynomial for a reasonable J guess with negative lightness
j = []
t = []
for r in range(200001):
    xyz = Color('srgb', [-r / 100000] * 3).convert('xyz-d65')
    j.append(cam16.xyz_to_cam(xyz.coords(), env)[0])
    t.append(hct.y_to_lstar(xyz[1]))
print(np.polyfit(t, j, 2).tolist())

print("==== Estimate c for Approximate J' Derivative: (c * y) / J ====")
# To obtain the first derivative for `J'`, we manually measure the rate of change
# at various points for `J` in relation to `y` in a CAM16 with the same environment
# that HCT uses. From this, it can be noted that if `dy / dJ` is divided by `y / J`,
# we get a fairly constant value (roughly between 1.8 - 2). From this, we have a
# rough approximation of `J' ~= K * y / J`, where we set `K` to measured average of
# `~1.832`.
#
# It can be noted that we do not just focus on achromatic values, but
# calculate the derivative on random colors in the Rec. 2020 gamut.
total = 0
count = 0
dy = 1e-12
for _ in range(200001):
    c = Color.random('rec2020').convert('xyy')
    y = c['Y']
    j = cam16.xyz_to_cam(c.convert('xyz-d65').coords(), env)[0]

    c['Y'] = y + dy
    j1 = cam16.xyz_to_cam(c.convert('xyz-d65').coords(), env)[0]
    c['Y'] = y - dy
    j2 = cam16.xyz_to_cam(c.convert('xyz-d65').coords(), env)[0]
    # Rate of change: `dy/dj`
    dydj = (2 * dy) / (j1 - j2)
    # If we assume this value is mainly dependent on J and Y,
    # and divide by the ratio of `Y / J`, we end up with a
    # constant `c` for an equation `c * Y / J`
    total += dydj * (j / y)
    count += 1

print(round(total / count, 3))
