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


class Environment:
    """Environment."""

    def __init__(
        self,
        *,
        kr: float,
        kb: float,
        integer: bool = False,
        output: str = 'standard',
        bit_depth: int = 8
    ) -> None:
        """Initialize."""

        if bit_depth not in (8, 10, 12, 14):
            raise ValueError(f"Unsupported bit depth of '{bit_depth}'")

        # Construct the Y'CbCr matrix
        kg = 1 - kr - kb
        self.rgb_to_ycbcr = [
            [kr, kg, kb],
            [-kr / (2 * (1 - kb)), -kg / (2 * (1 - kb)), 0.5],
            [0.5, -kg / (2 * (1 - kr)), -kb / (2 * (1 - kr))]
        ]
        self.ycbcr_to_rgb = alg.inv(self.rgb_to_ycbcr)

        # Standard form which removes negative values and adds headroom/footroom
        if output == 'standard':
            self.y_scale = 219 * (1 << (bit_depth - 8))  # type: float
            self.y_offset = 1 << (bit_depth - 4)  # type: float
            self.c_scale = 224 * (1 << (bit_depth - 8))  # type: float
            self.c_offset = 1 << (bit_depth - 1)  # type: float
        # Removes negative values but extends values to full range without adding headroom/footroom
        elif output == 'full':
            self.y_scale = (1 << bit_depth) - 1
            self.y_offset = 0
            self.c_scale = (1 << bit_depth) - 1
            self.c_offset = 1 << (bit_depth - 1)
        # Negative values remain unchanged
        elif output == 'default':
            self.y_scale = (1 << bit_depth) - 1
            self.y_offset = 0
            self.c_scale = (1 << bit_depth) - 1
            self.c_offset = 0
        else:
            raise ValueError(f"Unrecognized output '{output}'")

        # Scale integer range down to 0 - 1
        if not integer:
            div = (1 << bit_depth) - 1
            self.y_scale /= div
            self.y_offset /= div
            self.c_scale /= div
            self.c_offset /= div

        # Calculate minimum and maximum ranges for color channels
        self.y_range = [self.y_offset + 0 * self.y_scale, self.y_offset + 1 * self.y_scale]
        self.c_range = [self.c_offset + -0.5 * self.c_scale, self.c_offset + 0.5 * self.c_scale]


class YCbCr(Luminant, Space):
    """Y'CbCr color class."""

    ENV: Environment

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "y"

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        o = self.ENV.c_offset
        s = self.ENV.c_scale
        return alg.rect_to_polar((coords[1] - o) / s, (coords[2] - o) / s)[0] < util.ACHROMATIC_THRESHOLD_SM

    def to_base(self, coords: Vector) -> Vector:
        """To base from oRGB."""

        co = self.ENV.c_offset
        cs = self.ENV.c_scale
        coords = [
            (coords[0] - self.ENV.y_offset) / self.ENV.y_scale,
            (coords[1] - co) / cs,
            (coords[2] - co) / cs,
        ]
        return alg.matmul(self.ENV.ycbcr_to_rgb, coords, dims=alg.D2_D1)

    def from_base(self, coords: Vector) -> Vector:
        """From base to oRGB."""

        co = self.ENV.c_offset
        cs = self.ENV.c_scale
        coords = alg.matmul(self.ENV.rgb_to_ycbcr, coords, dims=alg.D2_D1)
        return [
            self.ENV.y_offset + coords[0] * self.ENV.y_scale,
            co + coords[1] * cs,
            co + coords[2] * cs,
        ]


class YCbCr709(Prism, YCbCr):
    """Y'CbCr color class using Rec. 709 (8 bit)."""

    BASE = 'rec709'
    NAME = "ycbcr-709"
    SERIALIZE = ("--ycbcr-709",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(kr=BT709[0], kb=BT709[1], bit_depth=8)
    CHANNELS = (
        Channel("y", ENV.y_range[0], ENV.y_range[1], bound=True),
        Channel("cb", ENV.c_range[0], ENV.c_range[1], bound=True),
        Channel("cr", ENV.c_range[0], ENV.c_range[1], bound=True)
    )
    GAMUT_CHECK = 'rec709'
