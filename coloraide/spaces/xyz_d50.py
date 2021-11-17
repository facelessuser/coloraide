"""XYZ class."""
from ..spaces import RE_DEFAULT_MATCH
from .xyz import XYZ
import re


class XYZD50(XYZ):
    """XYZ D50 class."""

    BASE = "xyz"
    NAME = "xyz-d50"
    SERIALIZE = ("xyz-d50",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D50"
