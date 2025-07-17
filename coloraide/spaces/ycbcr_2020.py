"""
Y'CbCr color space.

https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2020-2-201510-I!!PDF-E.pdf
"""
from __future__ import annotations
from .ycbcr_709 import YCbCr, Environment
from ..channels import Channel
from ..spaces import Prism
from ..cat import WHITES

BT2020 = [0.2627, 0.0593]


class YCbCr2020(Prism, YCbCr):
    """Y'CbCr color class using Rec. 2020 (10 bit)."""

    BASE = 'rec2020'
    NAME = "ycbcr-2020"
    SERIALIZE = ("--ycbcr-2020",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(kr=BT2020[0], kb=BT2020[1], bit_depth=10, standard=True)
    CHANNELS = (
        Channel("y", ENV.y_range[0], ENV.y_range[1], nans=ENV.y_range[0], bound=True),
        Channel("cb", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True),
        Channel("cr", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True)
    )
    GAMUT_CHECK = 'rec2020'
