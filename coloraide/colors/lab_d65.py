"""Lab D65 class."""
from ._space import RE_DEFAULT_MATCH
from .xyz import XYZ
from .lab import LabBase, lab_to_xyz, xyz_to_lab
from . import _convert as convert
import re


class LabD65(LabBase):
    """Lab D65 class."""

    SPACE = "lab-d65"
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space=SPACE))
    WHITE = convert.WHITES["D65"]

    @classmethod
    def _to_xyz(cls, lab):
        """To XYZ."""

        return cls._chromatic_adaption(cls.white(), XYZ.white(), lab_to_xyz(lab))

    @classmethod
    def _from_xyz(cls, xyz):
        """From XYZ."""

        return xyz_to_lab(cls._chromatic_adaption(XYZ.white(), cls.white(), xyz))
