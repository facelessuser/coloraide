"""Calculate HCT J approximation polynomial."""
import sys
import os
import numpy as np

sys.path.insert(0, os.getcwd())

from coloraide.everything import ColorAll as Color  # noqa: E402
from coloraide.spaces import cam16_jmh  # noqa: E402
from coloraide.spaces import hct  # noqa: E402

env = hct.HCT.ENV

j = []
t = []

for r in range(200000):
    xyz = Color('srgb', [r / 100000] * 3).convert('xyz-d65')
    j.append(cam16_jmh.xyz_d65_to_cam16(xyz.coords(), env)[0])
    t.append(hct.y_to_lstar(xyz[1]))

print('==== Positive Lightness ====')
print(np.polyfit(t, j, 2).tolist())

j = []
t = []

for r in range(200000):
    xyz = Color('srgb', [-r / 100000] * 3).convert('xyz-d65')
    j.append(cam16_jmh.xyz_d65_to_cam16(xyz.coords(), env)[0])
    t.append(hct.y_to_lstar(xyz[1]))

print('==== Negative Lightness ====')
print(np.polyfit(t, j, 2).tolist())
