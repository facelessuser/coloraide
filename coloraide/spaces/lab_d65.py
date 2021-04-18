"""Lab D65 class."""
from ..spaces import RE_DEFAULT_MATCH
from . import _cat
from .xyz import XYZ
from .lab import LabBase, lab_to_xyz, xyz_to_lab
import re


class LabD65(LabBase):
    """Lab D65 class."""

    SPACE = "lab-d65"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = _cat.WHITES["D65"]

    @classmethod
    def _to_xyz(cls, lab):
        """To XYZ."""

        return _cat.chromatic_adaption(cls.white(), XYZ.white(), lab_to_xyz(lab))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return xyz_to_lab(_cat.chromatic_adaption(XYZ.white(), cls.white(), xyz))
