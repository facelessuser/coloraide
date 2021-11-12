"""LCH class."""
from ..spaces import RE_DEFAULT_MATCH
from .lchuv import Lchuv
from .lchuv import lchuv_to_luv, luv_to_lchuv
import re
from ..util import Vector, MutableVector


class LchuvD65(Lchuv):
    """Lch(uv) class."""

    BASE = "luv-d65"
    SPACE = "lchuv-d65"
    SERIALIZE = ("--lchuv-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def to_base(cls, lchuv: Vector) -> MutableVector:
        """To Luv."""

        return lchuv_to_luv(lchuv)

    @classmethod
    def from_base(cls, luv: Vector) -> MutableVector:
        """To Luv."""

        return luv_to_lchuv(luv)
