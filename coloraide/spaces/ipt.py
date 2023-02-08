"""
The IPT color space.

https://www.researchgate.net/publication/\
221677980_Development_and_Testing_of_a_Color_Space_IPT_with_Improved_Hue_Uniformity.
"""
from __future__ import annotations
from ..spaces import Space, Labish
from ..channels import Channel, FLG_MIRROR_PERCENT
from ..cat import WHITES
from .. import algebra as alg
from ..types import Vector

# The IPT algorithm requires the use of the Hunt-Pointer-Estevez matrix,
# but it was originally calculated with the assumption of a slightly different
# D65 white point than what we use.
#
# - Theirs: [0.9504, 1.0, 1.0889] -> xy chromaticity points (0.3127035830618893, 0.32902313032606195)
# - Ours: [0.9504559270516716, 1, 1.0890577507598784] -> calculated from xy chromaticity points [0.31270, 0.32900]
#
# For a good conversion, our options were to either set the color space to a slightly different D65 white point,
# or adjust the algorithm such that it accounted for the difference in white point. We chose the latter.
#
# ```
# theirs = alg.diag([0.9504, 1.0, 1.0889])
# ours = alg.diag(white_d65)
# return alg.multi_dot([MHPE, theirs, alg.inv(ours)])
# ```
#
# Below is the Hunter-Pointer-Estevez matrix combined with our white point compensation.
XYZ_TO_LMS = [
    [0.4001764512951712, 0.7075, -0.08068831054981859],
    [-0.2279865839462744, 1.15, 0.061191135138152386],
    [0.0, 0.0, 0.9182669691320122]
]

LMS_TO_XYZ = [
    [1.8503518239760197, -1.1383686221417688, 0.23844898940542367],
    [0.36683077517134854, 0.6438845448402356, -0.01067344358438],
    [0.0, 0.0, 1.089007917757562]
]

LMS_P_TO_IPT = [
    [0.4, 0.4, 0.2],
    [4.455, -4.851, 0.396],
    [0.8056, 0.3572, -1.1628]
]

IPT_TO_LMS_P = [
    [1.0000000000000004, 0.0975689305146139, 0.2052264331645916],
    [0.9999999999999997, -0.1138764854731471, 0.13321715836999803],
    [1.0, 0.0326151099170664, -0.6768871830691793]
]


def xyz_to_ipt(xyz: Vector) -> Vector:
    """XYZ to IPT."""

    lms_p = [alg.npow(c, 0.43) for c in alg.dot(XYZ_TO_LMS, xyz, dims=alg.D2_D1)]
    return alg.dot(LMS_P_TO_IPT, lms_p, dims=alg.D2_D1)


def ipt_to_xyz(ipt: Vector) -> Vector:
    """IPT to XYZ."""

    lms = [alg.nth_root(c, 0.43) for c in alg.dot(IPT_TO_LMS_P, ipt, dims=alg.D2_D1)]
    return alg.dot(LMS_TO_XYZ, lms, dims=alg.D2_D1)


class IPT(Labish, Space):
    """The IPT class."""

    BASE = "xyz-d65"
    NAME = "ipt"
    SERIALIZE = ("--ipt",)  # type: tuple[str, ...]
    CHANNELS = (
        Channel("i", 0.0, 1.0),
        Channel("p", -1.0, 1.0, flags=FLG_MIRROR_PERCENT),
        Channel("t", -1.0, 1.0, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "intensity": "i",
        "protan": "cp",
        "tritan": "ct"
    }
    WHITE = WHITES['2deg']['D65']

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ."""

        return ipt_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ."""

        return xyz_to_ipt(coords)
