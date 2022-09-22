"""XYZ class."""
from __future__ import annotations
from ..cat import WHITES
from .xyz_d65 import XYZD65


class XYZD50(XYZD65):
    """XYZ D50 class."""

    BASE = "xyz-d65"
    NAME = "xyz-d50"
    SERIALIZE = ("xyz-d50",)
    WHITE = WHITES['2deg']['D50']
