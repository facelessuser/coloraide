"""
ICtCp class.

https://professional.dolby.com/siteassets/pdfs/ictcp_dolbywhitepaper_v071.pdf
"""
from __future__ import annotations
from ..spaces import Space, Labish
from ..cat import WHITES
from ..channels import Channel, FLG_MIRROR_PERCENT
from .. import util
from .. import algebra as alg
from ..types import Vector
from typing import cast

# All PQ Values are equivalent to defaults as stated in link below:
# https://en.wikipedia.org/wiki/High-dynamic-range_video#Perceptual_quantizer
#
# ```
# M1 = 2610 / 16384
# M1INV = 16384 / 2610
# M2 = 2523 / 32
# M2INV = 32 / 2523
# C1 = 3424 / 4096
# C2 = 2413 / 128
# C3 = 2392 / 128
# ```

# XYZ transform matrices
xyz_to_lms_m = [
    [0.359132, 0.697604, -0.03578],
    [-0.19218800000000003, 1.1003800000000001, 0.07554],
    [0.006956, 0.074916, 0.8433400000000001]
]

lms_to_xyz_mi = [
    [2.070508203420414, -1.3267039449989098, 0.20668057903526463],
    [0.36502513723373864, 0.6804585253538307, -0.045463558701123154],
    [-0.04950397021841152, -0.049503970218411505, 1.1880952852418765]
]

# LMS to Izazbz matrices
lms_p_to_ictcp_m = [
    [0.5, 0.5, 0.0],
    [1.61376953125, -3.323486328125, 1.709716796875],
    [4.378173828125, -4.24560546875, -0.132568359375]
]

ictcp_to_lms_p_mi = [
    [1.0, 0.008609037037932726, 0.11102962500302596],
    [1.0, -0.008609037037932726, -0.11102962500302596],
    [1.0000000000000002, 0.5600313357106792, -0.32062717498731885]
]


def ictcp_to_xyz_d65(ictcp: Vector) -> Vector:
    """From ICtCp to XYZ."""

    # Convert to LMS prime
    pqlms = alg.dot(ictcp_to_lms_p_mi, ictcp, dims=alg.D2_D1)

    # Decode PQ LMS to LMS
    lms = util.pq_st2084_eotf(pqlms)

    # Convert back to absolute XYZ D65
    absxyz = alg.dot(lms_to_xyz_mi, lms, dims=alg.D2_D1)

    # Convert back to normal XYZ D65
    return util.absxyzd65_to_xyz_d65(absxyz)


def xyz_d65_to_ictcp(xyzd65: Vector) -> Vector:
    """From XYZ to ICtCp."""

    # Convert from XYZ D65 to an absolute XYZ D5
    absxyz = util.xyz_d65_to_absxyzd65(xyzd65)

    # Convert to LMS
    lms = alg.dot(xyz_to_lms_m, absxyz, dims=alg.D2_D1)

    # PQ encode the LMS
    pqlms = util.pq_st2084_oetf(lms)

    # Calculate Izazbz
    return alg.dot(lms_p_to_ictcp_m, pqlms, dims=alg.D2_D1)


class ICtCp(Labish, Space):
    """ICtCp class."""

    BASE = "xyz-d65"
    NAME = "ictcp"
    SERIALIZE = ("--ictcp",)
    CHANNELS = (
        Channel("i", 0.0, 1.0),
        Channel("ct", -0.5, 0.5, flags=FLG_MIRROR_PERCENT),
        Channel("cp", -0.5, 0.5, flags=FLG_MIRROR_PERCENT)
    )
    CHANNEL_ALIASES = {
        "intensity": "i",
        "protan": "cp",
        "tritan": "ct"
    }
    WHITE = WHITES['2deg']['D65']
    DYNAMIC_RANGE = 'hdr'

    def labish_names(self) -> tuple[str, ...]:
        """
        Return Lab-ish names in the order L a b.

        ICtCp flips protan and tritan (which corresponds to `a` and `b`).
        Interestingly, the polarity of tritan (yellow/blue) is also flipped.
        """

        channels = cast(Space, self).channels
        return channels[0], channels[2], channels[1]

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from ICtCp."""

        return ictcp_to_xyz_d65(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to ICtCp."""

        return xyz_d65_to_ictcp(coords)
