"""Calculate HCT J approximation polynomial."""
import sys
import os
import numpy as np

sys.path.insert(0, os.getcwd())

from coloraide.everything import ColorAll as Color
from coloraide.spaces import cam16
from coloraide.spaces import hct

env = hct.HCT.ENV

j = []
t = []

for r in range(200001):
    xyz = Color('srgb', [r / 100000] * 3).convert('xyz-d65')
    j.append(cam16.xyz_to_cam(xyz.coords(), env)[0])
    t.append(hct.y_to_lstar(xyz[1]))

print('==== Positive Lightness ====')
print(np.polyfit(t, j, 2).tolist())

j = []
t = []

for r in range(200001):
    xyz = Color('srgb', [-r / 100000] * 3).convert('xyz-d65')
    j.append(cam16.xyz_to_cam(xyz.coords(), env)[0])
    t.append(hct.y_to_lstar(xyz[1]))

print('==== Negative Lightness ====')
print(np.polyfit(t, j, 2).tolist())
