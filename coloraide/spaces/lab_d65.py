"""Lab D65 class."""
from ..spaces import RE_DEFAULT_MATCH
from .xyz import XYZ
from .lab.base import LabBase, lab_to_xyz, xyz_to_lab
import re


class LabD65(LabBase):
    """Lab D65 class."""

    SPACE = "lab-d65"
    SERIALIZE = ("--lab-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    @classmethod
    def _to_xyz(cls, parent, lab):
        """To XYZ."""

        return parent.chromatic_adaptation(cls.WHITE, XYZ.WHITE, lab_to_xyz(lab, cls.white()))

    @classmethod
    def _from_xyz(cls, parent, xyz):
        """From XYZ."""

        return xyz_to_lab(parent.chromatic_adaptation(XYZ.WHITE, cls.WHITE, xyz), cls.white())
