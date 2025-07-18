"""
The sYCC color space.

https://www.color.org/sycc.pdf
"""
from __future__ import annotations
from .ycbcr709 import YPbPr, YCbCr, Environment, digital_round
from ..channels import Channel
from ..cat import WHITES

BT601 = (0.2990, 0.1140)


class sYCC(YPbPr):
    """Y'CbCr color class using sRGB and BT.601 transform (8 bit)."""

    BASE = 'srgb'
    NAME = "sycc"
    SERIALIZE = ("--sycc",)
    WHITE = WHITES['2deg']['D65']
    K = BT601
    GAMUT_CHECK = 'srgb'


class sYCC8(YCbCr):
    """YCbCr color class using Rec. 709 (8 bit)."""

    BASE = 'sycc'
    NAME = "sycc-8bit"
    SERIALIZE = ("--sycc-8bit",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(bit_depth=8, standard=False)
    CHANNELS = (
        Channel("y", ENV.y_range[0], ENV.y_range[1], nans=ENV.y_range[0], bound=True, limit=digital_round(ENV)),
        Channel("cb", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=digital_round(ENV)),
        Channel("cr", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=digital_round(ENV))
    )
    GAMUT_CHECK = 'srgb'
