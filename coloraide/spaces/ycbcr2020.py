"""
Y'CbCr color space.

https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2020-2-201510-I!!PDF-E.pdf
"""
from __future__ import annotations
from .ycbcr709 import YPbPr, YCbCr, Environment, digital_round
from ..channels import Channel
from ..cat import WHITES

BT2020 = (0.2627, 0.0593)


class YPbPr2020(YPbPr):
    """YPbPr color class using Rec. 709."""

    BASE = 'rec2020'
    NAME = "ypbpr2020"
    SERIALIZE = ("--ypbpr2020",)
    WHITE = WHITES['2deg']['D65']
    K = BT2020
    GAMUT_CHECK = 'rec2020'


class YCbCr2020(YCbCr):
    """Y'CbCr color class using Rec. 2020 (12 bit)."""

    BASE = 'ypbpr2020'
    NAME = "ycbcr2020-10bit"
    SERIALIZE = ("--ycbcr2020-10bit",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(bit_depth=10, standard=True)
    CHANNELS = (
        Channel("y", ENV.y_range[0], ENV.y_range[1], nans=ENV.y_range[0], bound=True, limit=digital_round(ENV)),
        Channel("cb", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=digital_round(ENV)),
        Channel("cr", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=digital_round(ENV))
    )
    GAMUT_CHECK = 'rec2020'
