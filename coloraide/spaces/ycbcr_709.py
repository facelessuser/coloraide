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
from ..cat import WHITES
from .. import algebra as alg

BT709 = [0.2126, 0.0722]


def digital_round(x: float, env: Environment) -> float:
    """Rounding for digital values."""

    return alg.clamp(alg.round_half_up(x), 0, env.max_integer_size)


class Environment:
    """Environment."""

    def __init__(
        self,
        *,
        kr: float,
        kb: float,
        integer: bool = False,
        standard: bool = False,
        bit_depth: int = 8
    ) -> None:
        """Initialize."""

        self.max_integer_size = (1 << bit_depth) - 1
        self.standard = standard
        self.integer = integer

        # Construct the Y'CbCr matrix
        kg = 1 - kr - kb
        self.rgb_to_ycbcr = [
            [kr, kg, kb],
            [-kr / (2 * (1 - kb)), -kg / (2 * (1 - kb)), 0.5],
            [0.5, -kg / (2 * (1 - kr)), -kb / (2 * (1 - kr))]
        ]
        self.ycbcr_to_rgb = alg.inv(self.rgb_to_ycbcr)

        # Standard form which removes negative values and adds headroom/footroom
        if standard:
            self.y_scale = 219 * (1 << (bit_depth - 8))  # type: float
            self.y_offset = 1 << (bit_depth - 4)  # type: float
            self.c_scale = 224 * (1 << (bit_depth - 8))  # type: float
            self.c_offset = 1 << (bit_depth - 1)  # type: float

        # Removes negative values but extends values to full range without adding headroom/footroom
        # The default form cannot be in unsigned integer form and must be shifted
        else:
            if integer:
                self.y_scale = self.max_integer_size
                self.y_offset = 0
                self.c_scale = self.max_integer_size
                self.c_offset = 1 << (bit_depth - 1)

            # Floating point should revert to normal
            else:
                self.y_scale = self.max_integer_size
                self.y_offset = 0
                self.c_scale = self.max_integer_size
                self.c_offset = 0

        # Scale integer range down to 0 - 1
        if not integer:
            self.y_scale /= self.max_integer_size
            self.y_offset /= self.max_integer_size
            self.c_scale /= self.max_integer_size
            self.c_offset /= self.max_integer_size

        # Calculate minimum and maximum ranges for color channels
        self.y_range = [self.y_offset + 0 * self.y_scale, self.y_offset + 1 * self.y_scale]
        self.c_range = [self.c_offset + -0.5 * self.c_scale, self.c_offset + 0.5 * self.c_scale]


class YCbCr(Luminant, Space):
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
        if env.standard or env.integer:
            o = env.c_offset
            s = env.c_scale
            return alg.rect_to_polar((coords[1] - o) / s, (coords[2] - o) / s)[0] < util.ACHROMATIC_THRESHOLD_SM
        else:
            return alg.rect_to_polar(coords[1], coords[2])[0] < util.ACHROMATIC_THRESHOLD_SM

    def to_base(self, coords: Vector) -> Vector:
        """To base from oRGB."""

        env = self.ENV
        if env.integer:
            coords = [digital_round(c, env) for c in coords]
        co = env.c_offset
        cs = env.c_scale
        coords = [
            (coords[0] - env.y_offset) / env.y_scale,
            (coords[1] - co) / cs,
            (coords[2] - co) / cs,
        ]
        return alg.matmul(env.ycbcr_to_rgb, coords, dims=alg.D2_D1)

    def from_base(self, coords: Vector) -> Vector:
        """From base to oRGB."""

        env = self.ENV
        co = env.c_offset
        cs = env.c_scale
        coords = alg.matmul(env.rgb_to_ycbcr, coords, dims=alg.D2_D1)
        coords = [
            env.y_offset + coords[0] * env.y_scale,
            co + coords[1] * cs,
            co + coords[2] * cs,
        ]
        if env.integer:
            coords = [digital_round(c, env) for c in coords]
        return coords


class YCbCr709(Prism, YCbCr):
    """Y'CbCr color class using Rec. 709 (8 bit)."""

    BASE = 'rec709'
    NAME = "ycbcr-709"
    SERIALIZE = ("--ycbcr-709",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(kr=BT709[0], kb=BT709[1], bit_depth=8, standard=True)
    CHANNELS = (
        Channel("y", ENV.y_range[0], ENV.y_range[1], nans=ENV.y_range[0], bound=True),
        Channel("cb", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True),
        Channel("cr", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True)
    )
    GAMUT_CHECK = 'rec709'
