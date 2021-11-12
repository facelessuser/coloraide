"""Lch D65 class."""
from ..spaces import RE_DEFAULT_MATCH
from .lch.base import LchBase, lch_to_lab, lab_to_lch
import re
from ..util import Vector, MutableVector


class LchD65(LchBase):
    """Lch D65 class."""

    BASE = "lab-d65"
    SPACE = "lch-d65"
    SERIALIZE = ("--lch-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def to_base(cls, lchd65: Vector) -> MutableVector:
        """To Lab."""

        return lch_to_lab(lchd65)

    @classmethod
    def from_base(cls, labd65: Vector) -> MutableVector:
        """To Lab."""

        return lab_to_lch(labd65)
