"""
Delta E 99o.

https://de.wikipedia.org/wiki/DIN99-Farbraum
"""
from __future__ import annotations
from .delta_e_76 import DE76


class DE99o(DE76):
    """Delta E 99o class."""

    NAME = "99o"
    SPACE = "din99o"
