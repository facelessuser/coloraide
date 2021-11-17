"""LCH class."""
from ..spaces import RE_DEFAULT_MATCH
from .lchuv import Lchuv
import re


class LchuvD65(Lchuv):
    """Lch(uv) class."""

    BASE = "luv-d65"
    NAME = "lchuv-d65"
    SERIALIZE = ("--lchuv-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"
