"""Lab D65 class."""
from ..spaces import RE_DEFAULT_MATCH, GamutUnbound
from .lab import Lab
import re


class LabD65(Lab):
    """Lab D65 class."""

    BASE = 'xyz-d65'
    NAME = "lab-d65"
    SERIALIZE = ("--lab-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    BOUNDS = (
        GamutUnbound(0.0, 100.0),  # Technically we could/should clamp the zero side.
        GamutUnbound(-130, 130),
        GamutUnbound(-130, 130)
    )
