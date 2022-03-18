"""Lab D65 class."""
from ..spaces import RE_DEFAULT_MATCH, WHITES
from .lab import Lab
import re


class LabD65(Lab):
    """Lab D65 class."""

    BASE = 'xyz-d65'
    NAME = "lab-d65"
    SERIALIZE = ("--lab-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = WHITES['2deg']['D65']
