"""
YCbCr color space.

Rec. 709
- https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.709-6-201506-I!!PDF-E.pdf

Matrix derivation and approach
- https://www.itu.int/rec/T-REC-H.Sup18-201710-I
"""
from __future__ import annotations
import math
from .. import util
from ..channels import Channel
from ..types import Vector
from ..spaces import Luminant, Prism, Labish, Space
from ..cat import WHITES
from .. import algebra as alg

BT709 = (0.2126, 0.0722)


class Environment:
    """Environment."""

    def __init__(
        self,
        *,
        k: tuple[float, float] = BT709,
        standard: bool = False,
        bit_depth: int = 8
    ) -> None:
        """Initialize."""

        # Construct the transformation matrix
        kr, kb = k
        kg = 1 - kr - kb
        self.rgb_to_ycbcr = [
            [kr, kg, kb],
            [-kr / (2 * (1 - kb)), -kg / (2 * (1 - kb)), 0.5],
            [0.5, -kg / (2 * (1 - kr)), -kb / (2 * (1 - kr))]
        ]
        self.ycbcr_to_rgb = alg.inv(self.rgb_to_ycbcr)

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
        self.c_middle = self.digital_round(self.c_range[0] + (self.c_range[1] - self.c_range[0]) / 2)

    def digital_round(self, x: float) -> int:
        """
        Apply digital rounding and clamp to integer range.

        Rounding is applied such that half values are rounding towards positive or negative infinity
        depending on the number's sign. Rounding defined in ITU-R BT.2100.

        - https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2100-3-202502-I!!PDF-E.pdf

        Clamping is then applied to keep the value within the target integer type.
        """

        return alg.clamp(int(alg.sign(x) * math.floor(abs(x) + 0.5)), 0, self.max_integer_size)


class YPbPr(Labish, Space):
    """YPbPr class."""

    ENV: Environment
    CHANNELS = (
        Channel("y", 0.0, 1.0, bound=True),
        Channel("cb", -0.5, 0.5, bound=True),
        Channel("cr", -0.5, 0.5, bound=True)
    )
    CHANNEL_ALIASES = {
        'luma': 'y'
    }

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "y"

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return alg.rect_to_polar(coords[1], coords[2])[0] < util.ACHROMATIC_THRESHOLD_SM

    def to_base(self, coords: Vector) -> Vector:
        """To base from oRGB."""

        return alg.matmul(self.ENV.ycbcr_to_rgb, coords, dims=alg.D2_D1)

    def from_base(self, coords: Vector) -> Vector:
        """From base to oRGB."""

        return alg.matmul(self.ENV.rgb_to_ycbcr, coords, dims=alg.D2_D1)


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

        return coords[1] == coords[2] == self.ENV.c_middle

    def to_base(self, coords: Vector) -> Vector:
        """To base from oRGB."""

        env = self.ENV
        co = env.c_offset
        cs = env.c_scale
        coords = [
            (coords[0] - env.y_offset) / env.y_scale,
            (coords[1] - co) / cs,
            (coords[2] - co) / cs,
        ]
        coords = alg.matmul(env.ycbcr_to_rgb, coords, dims=alg.D2_D1)
        int_size = env.max_integer_size
        coords = [env.digital_round(c * int_size) / int_size for c in coords]
        return coords

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
        return [env.digital_round(c) for c in coords]


class YPbPr709(YPbPr):
    """YPbPr color class using Rec. 709."""

    BASE = 'rec709'
    NAME = "ypbpr709"
    SERIALIZE = ("--ypbpr709",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(k=BT709)
    GAMUT_CHECK = 'rec709'


class YCbCr709Bit8(YCbCr):
    """YCbCr color class using Rec. 709 (8 bit)."""

    BASE = 'rec709'
    NAME = "ycbcr709-8bit"
    SERIALIZE = ("--ycbcr709-8bit",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(bit_depth=8, standard=True)
    K = BT709
    CHANNELS = (
        Channel("y", ENV.y_range[0], ENV.y_range[1], nans=ENV.y_range[0], bound=True, limit=ENV.digital_round),
        Channel("cb", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=ENV.digital_round),
        Channel("cr", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=ENV.digital_round)
    )
    GAMUT_CHECK = 'rec709'


class YCbCr709Bit10(YCbCr):
    """YCbCr color class using Rec. 709 (10 bit)."""

    BASE = 'rec709'
    NAME = "ycbcr709-10bit"
    SERIALIZE = ("--ycbcr709-10bit",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(bit_depth=10, standard=True)
    K = BT709
    CHANNELS = (
        Channel("y", ENV.y_range[0], ENV.y_range[1], nans=ENV.y_range[0], bound=True, limit=ENV.digital_round),
        Channel("cb", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=ENV.digital_round),
        Channel("cr", ENV.c_range[0], ENV.c_range[1], nans=ENV.c_range[0], bound=True, limit=ENV.digital_round)
    )
    GAMUT_CHECK = 'rec709'

