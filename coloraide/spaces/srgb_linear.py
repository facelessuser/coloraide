"""SRGB Linear color class."""
from ..spaces import RE_DEFAULT_MATCH
from .srgb.base import SRGB, lin_srgb_to_xyz, xyz_to_lin_srgb, lin_srgb, gam_srgb
from .xyz import XYZ
import re
from ..util import Vector, MutableVector
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class SRGBLinear(SRGB):
    """SRGB linear."""

    SPACE = "srgb-linear"
    SERIALIZE = ("--srgb-linear",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def _to_srgb(cls, parent: 'Color', rgb: Vector) -> MutableVector:
        """Linear sRGB to sRGB."""

        return gam_srgb(rgb)

    @classmethod
    def _from_srgb(cls, parent: 'Color', rgb: Vector) -> MutableVector:
        """sRGB to linear sRGB."""

        return lin_srgb(rgb)

    @classmethod
    def _to_xyz(cls, parent: 'Color', rgb: Vector) -> MutableVector:
        """SRGB Linear to XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lin_srgb_to_xyz(rgb))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """XYZ to SRGB Linear."""

        return xyz_to_lin_srgb(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz))
