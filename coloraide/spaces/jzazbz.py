"""
Jzazbz class.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
from ..spaces import Space, RE_DEFAULT_MATCH, GamutUnbound
from . import _cat
from .xyz_d65 import XYZ
from .. import util
import re

# Many libraries use 200, but `Colorjs.io` uses 203
# The author explains why 203 was chosen:
#
#   Maximum luminance in PQ is 10,000 cd/m^2
#   Relative XYZ has Y=1 for media white
#   BT.2048 says media white Y=203 at PQ 58
#
# We will currently use 203 for now the difference is minimal.
# If there were a significant difference, and one clearly gave
# better results, that would make the decision easier, but the
# explanation above seems sufficient for now.
YW = 203

B = 1.15
G = 0.66
N = 2610 / (2 ** 14)
NINV = (2 ** 14) / 2610
C1 = 3424 / (2 ** 12)
C2 = 2413 / (2 ** 7)
C3 = 2392 / (2 ** 7)
P = 1.7 * 2523 / (2 ** 5)
PINV = (2 ** 5) / (1.7 * 2523)
D = -0.56
D0 = 1.6295499532821566E-11

# XYZ cone matrices
xyz_to_lms_m = [
    [0.41478972, 0.579999, 0.0146480],
    [-0.2015100, 1.120649, 0.0531008],
    [-0.0166008, 0.264800, 0.6684799]
]

lms_to_xyz_mi = [
    [1.9242264357876069, -1.0047923125953657, 0.037651404030618],
    [0.3503167620949991, 0.7264811939316552, -0.065384422948085],
    [-0.0909828109828475, -0.3127282905230739, 1.5227665613052603]
]

# LMS to Izazbz matrices
lms_p_to_izazbz_m = [
    [0.5, 0.5, 0],
    [3.524000, -4.066708, 0.542708],
    [0.199076, 1.096799, -1.295875]
]

izazbz_to_lms_p_mi = [
    [1.0, 0.1386050432715393, 0.05804731615611882],
    [1.0, -0.13860504327153927, -0.05804731615611891],
    [1.0, -0.09601924202631895, -0.811891896056039]
]


def xyz_d65_to_absxyzd65(xyzd65):
    """XYZ D65 to Absolute XYZ D65."""

    return [max(c * YW, 0) for c in xyzd65]


def absxyzd65_to_xyz_d65(absxyzd65):
    """Absolute XYZ D65 XYZ D65."""

    return [max(c / YW, 0) for c in absxyzd65]


def pq_encode(lms):
    """PQ encoding function to encode high dynamic range luminance."""

    return [
        (
            (
                (C1 + (C2 * ((c / 10000) ** N))) /
                (1 + (C3 * ((c / 10000) ** N)))
            ) ** P
        ).real for c in lms
    ]


def pq_decode(pqlms):
    """Decode PQ LMS."""

    return [
        (
            10000 * (
                (
                    (C1 - (c ** PINV)) /
                    ((C3 * (c ** PINV)) - C2)
                ) ** NINV
            )
        ).real for c in pqlms
    ]


def jzazbz_to_xyz_d65(jzazbz):
    """From Jzazbz to XYZ."""

    jz, az, bz = jzazbz

    # Calculate Iz
    iz = (jz + D0) / (1 + D - D * (jz + D0))

    # Convert to LMS prime
    pqlms = util.dot(izazbz_to_lms_p_mi, [iz, az, bz])

    # Decode PQ LMS to LMS
    lms = pq_decode(pqlms)

    # Convert back to absolute XYZ D65
    xm, ym, za = util.dot(lms_to_xyz_mi, lms)
    xa = (xm + ((B - 1) * za)) / B
    ya = (ym + ((G - 1) * xa)) / G

    # Convert back to normal XYZ D65
    return absxyzd65_to_xyz_d65([xa, ya, za])


def xyz_d65_to_jzazbz(xyzd65):
    """From XYZ to Jzazbz."""

    # Convert from XYZ D65 to an absolute XYZ D5
    xa, ya, za = xyz_d65_to_absxyzd65(xyzd65)
    xm = (B * xa) - ((B - 1) * za)
    ym = (G * ya) - ((G - 1) * xa)

    # Convert to LMS
    lms = util.dot(xyz_to_lms_m, [xm, ym, za])

    # PQ encode the LMS
    pqlms = pq_encode(lms)

    # Calculate Izazbz
    iz, az, bz = util.dot(lms_p_to_izazbz_m, pqlms)

    # Calculate Jz
    jz = ((1 + D) * iz) / (1 + (D * iz)) - D0
    return jz, az, bz


class Jzazbz(Space):
    """Jzazbz class."""

    SPACE = "jzazbz"
    CHANNEL_NAMES = ("jz", "az", "bz", "alpha")
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = _cat.WHITES["D65"]

    _range = (
        GamutUnbound([0, 1]),
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
    def _to_xyz(cls, jzazbz):
        """To XYZ."""

        return _cat.chromatic_adaption(cls.white(), XYZ.white(), jzazbz_to_xyz_d65(jzazbz))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return xyz_d65_to_jzazbz(_cat.chromatic_adaption(XYZ.white(), cls.white(), xyz))
