"""Lch D65 class."""
from ..spaces import RE_DEFAULT_MATCH
from . import _cat
from .lab_d65 import LabD65
from .lch import LchBase, lch_to_lab, lab_to_lch
import re


class LchD65(LchBase):
    """Lch D65 class."""

    SPACE = "lch-d65"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = _cat.WHITES["D65"]

    @classmethod
    def _to_lab_d65(cls, lchd65):
        """To Lab."""

        return lch_to_lab(lchd65)

    @classmethod
    def _from_lab_d65(cls, labd65):
        """To Lab."""

        return lab_to_lch(labd65)

    @classmethod
    def _to_xyz(cls, lch):
        """To XYZ."""

        return LabD65._to_xyz(cls._to_lab_d65(lch))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return cls._from_lab_d65(LabD65._from_xyz(xyz))
