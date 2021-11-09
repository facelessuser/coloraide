"""LCH class."""
from ..spaces import RE_DEFAULT_MATCH
from .lchuv import Lchuv
from .luv_d65 import LuvD65
from .lchuv import lchuv_to_luv, luv_to_lchuv
import re
from ..util import Vector, MutableVector
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


class LchuvD65(Lchuv):
    """Lch(uv) class."""

    SPACE = "lchuv-d65"
    SERIALIZE = ("--lchuv-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def _to_luv_d65(cls, parent: 'Color', lchuv: Vector) -> MutableVector:
        """To Luv."""

        return lchuv_to_luv(lchuv)

    @classmethod
    def _from_luv_d65(cls, parent: 'Color', luv: Vector) -> MutableVector:
        """To Luv."""

        return luv_to_lchuv(luv)

    @classmethod
    def _to_xyz(cls, parent: 'Color', lchuv: Vector) -> MutableVector:
        """To XYZ."""

        return LuvD65._to_xyz(parent, cls._to_luv_d65(parent, lchuv))

    @classmethod
    def _from_xyz(cls, parent: 'Color', xyz: Vector) -> MutableVector:
        """From XYZ."""

        return cls._from_luv_d65(parent, LuvD65._from_xyz(parent, xyz))
