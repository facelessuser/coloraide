"""Lch D65 class."""
from ..spaces import RE_DEFAULT_MATCH
from .lch import Lch
import re


class LchD65(Lch):
    """Lch D65 class."""

    BASE = "lab-d65"
    NAME = "lch-d65"
    SERIALIZE = ("--lch-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"
