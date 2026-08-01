"""
Calculate values for the Newton approximation of CAM16 J from HCT T (tone) approximation polynomial.

- Calculate a simple polynomial that describes a rough relationship between HCT T and CAM16 J. This
  is used to get an initial guess of CAM16 lightness (J) from HCT tone (T).
- Calculate the constant for the first derivative approximation for Newton's Method. It is too
  difficult to provide an exact first derivative for CAM16 relationship of XYZ's Y and CAM16 J. But
  we can calculate a reasonable approximation of the first derivative (the rate of change) and then
  see that it is somewhat constant in relation to J and Y. There is some deviation, but it is small
  enough that we can calculate a fairly reliable first derivative approximation. To further refine
  it, we can use Ostrowski's Method without having to estimate a second derivative.
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
# When we manually estimate the approximate rate of change we can see
# that it is fairly constant, roughly in the range of 1.8 - 2. If we average
# the rate of change, divide by the ratio of the current Y and J, we get
# an approximate first derivative of `avg(dy/dx) = c * Y / J` where `c` is
# some constant.
#
# Depending on how small `dy` is for our original estimate of the
# results, `c` will be somewhat different for our estimated derivative,
# but the smaller `dy` we use, the more consistent this value is.
# Using a very small `dy` gives us a better rate of change. If using a `dy`
# of about 0.1, we may get an average closer to 2 (what we used before),
# but with a smaller value, we can get a value that approaches ~1.832/1.833
# which gives us a better, faster overall convergence as it is a better
# average overall.
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
