"""LCH class."""
from ..spaces import RE_DEFAULT_MATCH
from .lchuv import Lchuv
from .luv_d65 import LuvD65
from .lchuv import lchuv_to_luv, luv_to_lchuv
import re


class LchuvD65(Lchuv):
    """Lch(uv) class."""

    SPACE = "lchuv-d65"
    SERIALIZE = ("--lchuv-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def _to_luv_d65(cls, parent, lchuv):
        """To Luv."""

        return lchuv_to_luv(lchuv)

    @classmethod
    def _from_luv_d65(cls, parent, luv):
        """To Luv."""

        return luv_to_lchuv(luv)

    @classmethod
    def _to_xyz(cls, parent, lchuv):
        """To XYZ."""

        return LuvD65._to_xyz(parent, cls._to_luv_d65(parent, lchuv))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return cls._from_luv_d65(parent, LuvD65._from_xyz(parent, xyz))
