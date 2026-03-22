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
from .lab import Lab
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from .. import algebra as alg
from ..types import Vector


M1 = [
    [0.758376129483666, 0.38380162590825073, -0.09608055040602373],
    [0.1267139363153284, 0.8421628149123207, 0.03434823621506485],
    [0.07639223722200054, 0.25894352627545103, 0.6139139663787314]
]

M1_INV = [
    [1.4133073795748359, -0.7245661027731641, 0.2617287231983285],
    [-0.20907372745004316, 1.3153903462455017, -0.10631661879545858],
    [-0.08767910052303855, -0.46465890124976855, 1.641168001772807]
]

M2 = [
    [0.10058070589596234, 1.0155897099394149, -0.1161704158353769],
    [2.361576469961645, -2.4409973750629357, 0.07942090510129071],
    [0.04565327074453785, 0.818754884454245, -0.8644081551987829]
]

M2_INV = [
    [0.9999999999999997, 0.3827736318539182, -0.09922417671418936],
    [0.9999999999999996, -0.039921540824987126, -0.13806096115936264],
    [0.9999999999999997, -0.017597113360184317, -1.292870720601441]
]


def xyz_d65_to_helmgen(xyz: Vector) -> Vector:
    """Convert XYZ to Helmgen."""

    lms = alg.matmul_x3(M1, xyz, dims=alg.D2_D1)
    c = [alg.nth_root(v, 3) for v in lms]
    return alg.matmul_x3(M2, c, dims=alg.D2_D1)


def helmgen_to_xyz(lab: Vector) -> Vector:
    """Convert Helmgen to XYZ."""

    c = alg.matmul_x3(M2_INV, lab, dims=alg.D2_D1)
    lms = [alg.spow(v, 3) for v in c]
    return alg.matmul_x3(M1_INV, lms, dims=alg.D2_D1)


class Helmgen(Lab):
    """Helmgen class."""

    BASE = "xyz-d65"
    NAME = "helmgen"
    SERIALIZE = ("--helmgen",)
    CHANNELS = (
        Channel("l", 0.0, 1.0),
        Channel("a", -0.4, 0.4, flags=FLG_MIRROR_PERCENT),
        Channel("b", -0.4, 0.4, flags=FLG_MIRROR_PERCENT)
    )
    WHITE = WHITES['2deg']['ASTM-E308-D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return helmgen_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_d65_to_helmgen(coords)
