"""XYZ class."""
from ..spaces import RE_DEFAULT_MATCH, WHITES
from .xyz_d65 import XYZD65
import re


class XYZD50(XYZD65):
    """XYZ D50 class."""

    BASE = "xyz-d65"
    NAME = "xyz-d50"
    SERIALIZE = ("xyz-d50",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = WHITES['2deg']['D50']
