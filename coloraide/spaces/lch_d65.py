"""Lch D65 class."""
from ..spaces import RE_DEFAULT_MATCH, GamutUnbound, FLG_ANGLE, FLG_OPT_PERCENT, FLG_PERCENT
from .lch import Lch
import re


class LchD65(Lch):
    """Lch D65 class."""

    BASE = "lab-d65"
    NAME = "lch-d65"
    SERIALIZE = ("--lch-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"

    BOUNDS = (
        # I think chroma, specifically should be clamped.
        # Some libraries don't to prevent rounding issues. We should only get
        # negative chroma via direct user input, but when translating to
        # Lab, this will be corrected.
        GamutUnbound(0.0, 100.0, FLG_PERCENT),
        GamutUnbound(0.0, 160.0, FLG_OPT_PERCENT),
        GamutUnbound(0.0, 360.0, FLG_ANGLE)
    )
