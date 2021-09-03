"""
ICtCp class.

https://professional.dolby.com/siteassets/pdfs/ictcp_dolbywhitepaper_v071.pdf
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, OptionalPercent
from .xyz import XYZ
from .. import util
import re

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
    [-0.192188, 1.1003800000000001, 0.07554],
    [0.006956000000000001, 0.074916, 0.8433400000000001]
]

lms_to_xyz_mi = [
    [2.0705082034204145, -1.3267039449989098, 0.2066805790352646],
    [0.3650251372337387, 0.6804585253538307, -0.04546355870112315],
    [-0.04950397021841151, -0.0495039702184115, 1.1880952852418762]
]

# LMS to Izazbz matrices
lms_p_to_ictcp_m = [
    [0.5, 0.5, 0.0],
    [1.61376953125, -3.323486328125, 1.709716796875],
    [4.378173828125, -4.24560546875, -0.132568359375]
]

ictcp_to_lms_p_mi = [
    [0.9999999999999998, 0.008609037037932761, 0.11102962500302598],
    [0.9999999999999998, -0.008609037037932752, -0.11102962500302593],
    [0.9999999999999998, 0.5600313357106791, -0.3206271749873188]
]


def ictcp_to_xyz_d65(ictcp):
    """From ICtCp to XYZ."""

    # Convert to LMS prime
    pqlms = util.dot(ictcp_to_lms_p_mi, ictcp)

    # Decode PQ LMS to LMS
    lms = util.pq_st2084_eotf(pqlms)

    # Convert back to absolute XYZ D65
    absxyz = util.dot(lms_to_xyz_mi, lms)

    # Convert back to normal XYZ D65
    return util.absxyzd65_to_xyz_d65(absxyz)


def xyz_d65_to_ictcp(xyzd65):
    """From XYZ to ICtCp."""

    # Convert from XYZ D65 to an absolute XYZ D5
    absxyz = util.xyz_d65_to_absxyzd65(xyzd65)

    # Convert to LMS
    lms = util.dot(xyz_to_lms_m, absxyz)

    # PQ encode the LMS
    pqlms = util.pq_st2084_inverse_eotf(lms)

    # Calculate Izazbz
    return util.dot(lms_p_to_ictcp_m, pqlms)


class ICtCp(Space):
    """ICtCp class."""

    SPACE = "ictcp"
    SERIALIZE = ("--ictcp",)
    CHANNEL_NAMES = ("i", "ct", "cp", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    RANGE = (
        GamutUnbound([OptionalPercent(0), OptionalPercent(1)]),
        GamutUnbound([-0.5, 0.5]),
        GamutUnbound([-0.5, 0.5])
    )

    @property
    def i(self):
        """`I` channel."""

        return self._coords[0]

    @i.setter
    def i(self, value):
        """Set `I` channel."""

        self._coords[0] = self._handle_input(value)

    @property
    def ct(self):
        """`Ct` axis."""

        return self._coords[1]

    @ct.setter
    def ct(self, value):
        """`Ct` axis."""

        self._coords[1] = self._handle_input(value)

    @property
    def cp(self):
        """`Cp` axis."""

        return self._coords[2]

    @cp.setter
    def cp(self, value):
        """Set `Cp` axis."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def _to_xyz(cls, parent, ictcp):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, ictcp_to_xyz_d65(ictcp))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return xyz_d65_to_ictcp(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz))
