"""
Linear Rec. 2100.

As defined in CSS, this is simply an alias for linear Rec. 2020.
"""
from __future__ import annotations
from ..cat import WHITES
from .rec2020_linear import Rec2020Linear


class Rec2100Linear(Rec2020Linear):
    """Linear Rec. 2100 class."""

    NAME = "rec2100-linear"
    SERIALIZE = ('rec2100-linear',)
    WHITE = WHITES['2deg']['D65']
