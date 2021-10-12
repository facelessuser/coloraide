"""Lab D65 class."""
from ..spaces import RE_DEFAULT_MATCH
from .lab.base import Lab
import re


class LabD65(Lab):
    """Lab D65 class."""

    SPACE = "lab-d65"
    SERIALIZE = ("--lab-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"
