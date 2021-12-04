"""
Luv class.

https://en.wikipedia.org/wiki/CIELUV
"""
from ..spaces import RE_DEFAULT_MATCH
from .luv import Luv
import re


class LuvD65(Luv):
    """Oklab class."""

    BASE = "xyz-d65"
    NAME = "luv-d65"
    SERIALIZE = ("--luv-d65",)
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))
    WHITE = "D65"
