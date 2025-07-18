"""
Y'CbCr color space.

Rec. 601
- https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.601-7-201103-I!!PDF-E.pdf

Rec. 709
- https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.709-6-201506-I!!PDF-E.pdf

Rec. 2020
- https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2020-2-201510-I!!PDF-E.pdf

Matrix derivation and approach
- https://www.itu.int/rec/T-REC-H.Sup18-201710-I
"""
from __future__ import annotations
from .. import util
from ..channels import Channel
from ..types import Vector
from ..spaces import Luminant, Prism, Space
from .lab import Lab
from ..cat import WHITES
from .. import algebra as alg
from typing import Any, Callable

BT709 = (0.2126, 0.0722)


def _digital_round(x: float, env: Environment) -> int:
    """Rounding for digital values."""

    return alg.clamp(int(alg.round_half_up(x)), 0, env.max_integer_size)


def digital_round(env: Environment) -> Callable[[float], int]:
    """Round to integer."""

    return lambda x, e=env: _digital_round(x, e)  # type: ignore[misc]


class Environment:
    """Environment."""

    def __init__(
        self,
        *,
        standard: bool = False,
        bit_depth: int = 8
    ) -> None:
        """Initialize."""

        self.max_integer_size = (1 << bit_depth) - 1
        self.standard = standard

        # Standard form which removes negative values and adds headroom/footroom
        if standard:
            self.y_scale = 219 * (1 << (bit_depth - 8))  # type: float
            self.y_offset = 1 << (bit_depth - 4)  # type: float
            self.c_scale = 224 * (1 << (bit_depth - 8))  # type: float
            self.c_offset = 1 << (bit_depth - 1)  # type: float

        # Removes negative values but extends values to full range without adding headroom/footroom
        # The default form cannot be in unsigned integer form and must be shifted
        else:
            self.y_scale = self.max_integer_size
            self.y_offset = 0
            self.c_scale = self.max_integer_size
            self.c_offset = 1 << (bit_depth - 1)

        # Calculate minimum and maximum ranges for color channels
        self.y_range = [self.y_offset + 0 * self.y_scale, self.y_offset + 1 * self.y_scale]
        self.c_range = [self.c_offset + -0.5 * self.c_scale, self.c_offset + 0.5 * self.c_scale]


class YPbPr(Lab):

    ENV: Environment
    CHANNELS = (
        Channel("y", 0.0, 1.0, bound=True),
        Channel("cb", -0.5, 0.5, bound=True),
        Channel("cr", -0.5, 0.5, bound=True)
    )
    CHANNEL_ALIASES = {
        'lightness': 'y'
    }
    K = (0.0, 0.0)

    def __init__(self, **kwargs: Any) -> None:
        """Initialize."""

        super().__init__(**kwargs)

        # Construct the transformation matrix
        kr, kb = self.K
        kg = 1 - kr - kb
        self.rgb_to_ycbcr = [
            [kr, kg, kb],
            [-kr / (2 * (1 - kb)), -kg / (2 * (1 - kb)), 0.5],
            [0.5, -kg / (2 * (1 - kr)), -kb / (2 * (1 - kr))]
        ]
        self.ycbcr_to_rgb = alg.inv(self.rgb_to_ycbcr)

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "y"

    def to_base(self, coords: Vector) -> Vector:
        """To base from oRGB."""

        return alg.matmul(self.ycbcr_to_rgb, coords, dims=alg.D2_D1)

    def from_base(self, coords: Vector) -> Vector:
        """From base to oRGB."""

        return alg.matmul(self.rgb_to_ycbcr, coords, dims=alg.D2_D1)


class YCbCr(Luminant, Prism, Space):
    """Y'CbCr color class."""

    ENV: Environment

    CHANNEL_ALIASES = {
        'lightness': 'y'
    }

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "y"

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        env = self.ENV
        o = env.c_offset
        s = env.c_scale
        return alg.rect_to_polar((coords[1] - o) / s, (coords[2] - o) / s)[0] < util.ACHROMATIC_THRESHOLD_SM

    def to_base(self, coords: Vector) -> Vector:
        """To base from oRGB."""

        env = self.ENV
        coords = [_digital_round(c, env) for c in coords]
        co = env.c_offset
        cs = env.c_scale
        return [
            (coords[0] - env.y_offset) / env.y_scale,
            (coords[1] - co) / cs,
            (coords[2] - co) / cs,
        ]

    def from_base(self, coords: Vector) -> Vector:
        """From base to oRGB."""

        env = self.ENV
        co = env.c_offset
        cs = env.c_scale
        coords = [
            env.y_offset + coords[0] * env.y_scale,
            co + coords[1] * cs,
            co + coords[2] * cs,
        ]
        return [_digital_round(c, env) for c in coords]


class YPbPr709(YPbPr):
    """YPbPr color class using Rec. 709."""

    BASE = 'rec709'
    NAME = "ypbpr709"
    SERIALIZE = ("--ypbpr709",)
    WHITE = WHITES['2deg']['D65']
    K = BT709
    GAMUT_CHECK = 'rec709'


class YCbCr709(YCbCr):
    """YCbCr color class using Rec. 709 (8 bit)."""

    BASE = 'ypbpr709'
    NAME = "ycbcr709-8bit"
    SERIALIZE = ("--ycbcr709-8bit",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(bit_depth=8, standard=True)
    CHANNELS = (
        Channel("y", ENV.y_range[0], ENV.y_range[1], nans=ENV.y_range[0], bound=True, limit=digital_round(ENV)),
        Channel("cb", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=digital_round(ENV)),
        Channel("cr", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=digital_round(ENV))
    )
    GAMUT_CHECK = 'rec709'
