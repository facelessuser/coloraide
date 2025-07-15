"""
The sYCC color space.

https://www.color.org/sycc.pdf
"""
from __future__ import annotations
from .ycbcr_709 import YCbCr, Environment
from ..channels import Channel
from ..spaces import Prism
from ..cat import WHITES

BT601 = [0.2990, 0.1140]


class sYCC(Prism, YCbCr):
    """Y'CbCr color class using sRGB and BT.601 transform (8 bit)."""

    BASE = 'srgb'
    NAME = "sycc"
    SERIALIZE = ("--sycc",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(kr=BT601[0], kb=BT601[1], output='full', bit_depth=8)
    CHANNELS = (
        Channel("y", ENV.y_range[0], ENV.y_range[1], bound=True),
        Channel("cb", ENV.c_range[0], ENV.c_range[1], bound=True),
        Channel("cr", ENV.c_range[0], ENV.c_range[1], bound=True)
    )
    GAMUT_CHECK = 'srgb'
