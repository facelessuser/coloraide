"""
Jzazbz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound, OptionalPercent
from .xyz import XYZ
from .. import util
import re

B = 1.15
G = 0.66
D = -0.56
D0 = 1.6295499532821566E-11

# All PQ Values are equivalent to defaults as stated in link below except `M2` (and `IM2`):
# https://en.wikipedia.org/wiki/High-dynamic-range_video#Perceptual_quantizer
#
# ```
# M1 = 2610 / (2 ** 14)
# IM1 = (2 ** 14) / 2610
# C1 = 3424 / (2 ** 12)
# C2 = 2413 / (2 ** 7)
# C3 = 2392 / (2 ** 7)
# M2 = 1.7 * 2523 / (2 ** 5)
# IM2 = (2 ** 5) / (1.7 * 2523)
# ```
M2 = 1.7 * 2523 / (2 ** 5)


# XYZ transform matrices
xyz_to_lms_m = [
    [0.41478972, 0.579999, 0.014648],
    [-0.20151, 1.120649, 0.0531008],
    [-0.0166008, 0.2648, 0.6684799]
]

lms_to_xyz_mi = [
    [1.9242264357876069, -1.0047923125953657, 0.037651404030617994],
    [0.35031676209499907, 0.7264811939316552, -0.06538442294808501],
    [-0.09098281098284754, -0.3127282905230739, 1.5227665613052603]
]

# LMS to Izazbz matrices
lms_p_to_izazbz_m = [
    [0.5, 0.5, 0],
    [3.524, -4.066708, 0.542708],
    [0.199076, 1.096799, -1.295875]
]

izazbz_to_lms_p_mi = [
    [1.0, 0.1386050432715393, 0.05804731615611882],
    [1.0, -0.13860504327153927, -0.05804731615611891],
    [1.0, -0.09601924202631895, -0.811891896056039]
]


def jzazbz_to_xyz_d65(jzazbz):
    """From Jzazbz to XYZ."""

    jz, az, bz = jzazbz

    # Calculate Iz
    iz = (jz + D0) / (1 + D - D * (jz + D0))

    # Convert to LMS prime
    pqlms = util.dot(izazbz_to_lms_p_mi, [iz, az, bz])

    # Decode PQ LMS to LMS
    lms = util.pq_st2084_eotf(pqlms, m2=M2)

    # Convert back to absolute XYZ D65
    xm, ym, za = util.dot(lms_to_xyz_mi, lms)
    xa = (xm + ((B - 1) * za)) / B
    ya = (ym + ((G - 1) * xa)) / G

    # Convert back to normal XYZ D65
    return util.absxyzd65_to_xyz_d65([xa, ya, za])


def xyz_d65_to_jzazbz(xyzd65):
    """From XYZ to Jzazbz."""

    # Convert from XYZ D65 to an absolute XYZ D5
    xa, ya, za = util.xyz_d65_to_absxyzd65(xyzd65)
    xm = (B * xa) - ((B - 1) * za)
    ym = (G * ya) - ((G - 1) * xa)

    # Convert to LMS
    lms = util.dot(xyz_to_lms_m, [xm, ym, za])

    # PQ encode the LMS
    pqlms = util.pq_st2084_inverse_eotf(lms, m2=M2)

    # Calculate Izazbz
    iz, az, bz = util.dot(lms_p_to_izazbz_m, pqlms)

    # Calculate Jz
    jz = ((1 + D) * iz) / (1 + (D * iz)) - D0
    return jz, az, bz


class Jzazbz(Space):
    """Jzazbz class."""

    SPACE = "jzazbz"
    SERIALIZE = ("--jzazbz",)
    CHANNEL_NAMES = ("jz", "az", "bz", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    RANGE = (
        GamutUnbound([OptionalPercent(0), OptionalPercent(1)]),
        GamutUnbound([-0.5, 0.5]),
        GamutUnbound([-0.5, 0.5])
    )

    @property
    def jz(self):
        """Jz channel."""

        return self._coords[0]

    @jz.setter
    def jz(self, value):
        """Set jz channel."""

        self._coords[0] = self._handle_input(value)

    @property
    def az(self):
        """Az axis."""

        return self._coords[1]

    @az.setter
    def az(self, value):
        """Az axis."""

        self._coords[1] = self._handle_input(value)

    @property
    def bz(self):
        """Bz axis."""

        return self._coords[2]

    @bz.setter
    def bz(self, value):
        """Set bz axis."""

        self._coords[2] = self._handle_input(value)

    @classmethod
    def _to_xyz(cls, parent, jzazbz):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, jzazbz_to_xyz_d65(jzazbz))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return xyz_d65_to_jzazbz(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz))
