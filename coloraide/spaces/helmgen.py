"""
Helmlab GenSpace: generation-optimized color space for interpolation.

A simplified pipeline (`XYZ -> M1 -> cbrt -> M2 -> NC`) optimized for
perceptually uniform gradients, palette generation, and color-mix.
Achieves 6x better hue accuracy than Oklab with 10% better perceptual
distance prediction.

Key differences from Helmlab (MetricSpace):
  - Shared gamma = 1/3 (cube root, guarantees achromatic a=b=0)
  - No enrichment stages (simpler, faster, better for generation)
  - Different M1/M2 matrices (Phase1H-optimized)

- https://arxiv.org/abs/2602.23010
- https://github.com/Grkmyldz148/helmlab
"""
from __future__ import annotations
from functools import lru_cache
from .lab import Lab
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from .. import util
from .. import algebra as alg
from ..types import Vector, Matrix

M1 = [
    [ 0.4407412072890238, 0.40911369156796634, 0.18687249931895067],
    [ 0.12308224353121994, 0.557136239636739, 0.19274910862205916],
    [-0.23021079382916068, 0.9278243045135821, 0.4854100909928004]
]
M1_INV = [
    [2.126067208590642, -0.584957446988563, -0.5862125072812663],
    [-2.416561715802903, 5.96398983868483, -1.4378868725604865],
    [5.627382627163576, -11.677133103760319, 4.530507259029062]
]
M2 = [
    [ 0.2778609560084774, 0.21180362605092856, 0.6372017137356791],
    [ 1.7548720474157444, -0.9793270531556616, -0.7760752041286899],
    [-2.418690735750103, 3.982044105359993, -1.2833774660668076]
]
M2_INV = [
    [0.8649568923272442, 0.5589393137919957, 0.09145639155676465],
    [0.8215892255459026, 0.2356964021282657, 0.2653934155119385],
    [0.9190914921797732, -0.3220781744225231, -0.1280967178320807]
]


def xyz_d65_to_helmlab(xyz: Vector) -> Vector:
    """Convert XYZ to Helmlab."""

    lms = alg.matmul(M1, xyz, dims=alg.D2_D1)
    c = [alg.nth_root(v, 3) for v in lms]
    return alg.matmul(M2, c, dims=alg.D2_D1)


def helmlab_to_xyz(lab: Vector) -> Vector:
    """Convert Helmlab to XYZ."""

    c = alg.matmul(M2_INV, lab, dims=alg.D2_D1)
    lms = [alg.spow(v, 3) for v in c]
    return alg.matmul(M1_INV, lms, dims=alg.D2_D1)


@lru_cache(maxsize=1)
def get_nc_lut() -> Matrix:
    """
    Run pipeline without NC on D65 neutrals to measure achromatic error.

    ```
    nc = [[ncl, nca, ncb], ...]
    ```
    """

    n = 256
    nc = alg.zeros((n, 3))
    x, y, z = util.xy_to_xyz(WHITES['2deg']['ASTM-E308-D65'])
    for i in range(n):
        y = i / (n - 1)
        xyz = [y * x, y, y * z]

        # Pipeline without NC
        nc[i][:] = xyz_d65_to_helmlab(xyz)
    return nc


def neutral_error(l: float, nc: Matrix | None = None) -> Vector:
    """Neutral correction error."""

    if nc is None:
        nc = get_nc_lut()

    n = len(nc)

    if l <= 0:
        return [0.0, 0.0]

    if l < nc[0][0]:
        t = l / nc[0][0]
        return [nc[0][1] * t, nc[0][2] * t]

    if l >= nc[n - 1][0]:
        return nc[n - 1][1:]

    lo, hi = 0, n - 1
    while (hi - lo) > 1:
        mid = (lo + hi) >> 1
        if nc[mid][0] <= l:
            lo = mid
        else:
            hi = mid

    t = (l - nc[lo][0]) / (nc[lo + 1][0] - nc[lo][0])
    return [
        nc[lo][1] + t * (nc[lo + 1][1] - nc[lo][1]),
        nc[lo][2] + t * (nc[lo + 1][2] - nc[lo][2])
    ]


def xyz_d65_to_helmlab_corrected(xyz: Vector) -> Vector:
    """Convert XYZ to Helmlab."""

    lab = xyz_d65_to_helmlab(xyz)

    # Stage 10: Neutral correction (LUT)
    a_err, b_err = neutral_error(lab[0])
    lab[1] -= a_err
    lab[2] -= b_err
    return lab


def helmlab_corrected_to_xyz(lab: Vector) -> Vector:
    """Convert XYZ to Helmlab."""

    # Stage 10: Neutral correction (LUT)
    a_err, b_err = neutral_error(lab[0])
    lab[1] += a_err
    lab[2] += b_err

    return helmlab_to_xyz(lab)


class Helmgen(Lab):
    """Helmgen class."""

    BASE = "xyz-d65"
    NAME = "helmgen"
    SERIALIZE = ("--helmgen",)
    CHANNELS = (
        Channel("l", 0.0, 1.168140042703694),
        Channel("a", -0.4, 0.4, flags=FLG_MIRROR_PERCENT),
        Channel("b", -0.4, 0.4, flags=FLG_MIRROR_PERCENT)
    )
    WHITE = WHITES['2deg']['ASTM-E308-D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return helmlab_corrected_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_d65_to_helmlab_corrected(coords)
