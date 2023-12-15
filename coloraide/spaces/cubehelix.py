"""
Cubehelix color space.

Dave Green's Cubehelix colour scheme adapted to a color space.
https://arxiv.org/pdf/1108.5083.pdf

The paper does not describe a color space, but a way to create various
helixes to generate various Cubehelix schemes. Mike Bostock and Jason Davies
adapted this to a color space in D3 Color (https://github.com/d3/d3-color). We
match the algorithm here as implemented in D3.

Copyright 2010-2022 Mike Bostock

Permission to use, copy, modify, and/or distribute this software for any purpose
with or without fee is hereby granted, provided that the above copyright notice
and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.
"""
from __future__ import annotations
from ..spaces import Space, HSLish
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
import math
from .. import util
from ..types import Vector

# Constants
A = -0.14861
B = 1.78277
C = -0.29227
D = -0.90649
E = 1.97294
ED = E * D
EB = E * B
BC_DA = B * C - D * A
MAX_SAT = 4.614386868039719


def srgb_to_cubehelix(coords: Vector) -> Vector:
    """Convert sRGB to Cubehelix."""

    r, g, b = coords
    l = (BC_DA * b + ED * r - EB * g) / (BC_DA + ED - EB)
    bl = b - l
    k = (E * (g - l) - C * bl) / D
    s = math.sqrt(k * k + bl * bl) / (E * l * (1 - l)) if l not in (0.0, 1.0) else 0.0
    h = (math.degrees(math.atan2(k, bl)) - 120) if s else 0.0
    return [util.constrain_hue(h), s, l]


def cubehelix_to_srgb(coords: Vector) -> Vector:
    """Convert Cubehelix to sRGB."""

    h, s, l = coords
    if l in (0.0, 1.0):
        s = 0.0
    h = math.radians(h + 120) if s != 0.0 else 0.0
    a = s * l * (1 - l)
    cosh = math.cos(h)
    sinh = math.sin(h)
    return [
        l + a * (A * cosh + B * sinh),
        l + a * (C * cosh + D * sinh),
        l + a * (E * cosh)
    ]


class Cubehelix(HSLish, Space):
    """Cubehelix class."""

    BASE = 'srgb'
    NAME = "cubehelix"
    SERIALIZE = ("--cubehelix",)
    CHANNELS = (
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE),
        Channel("s", 0.0, MAX_SAT, bound=True),
        Channel("l", 0.0, 1.0, bound=True)
    )
    CHANNEL_ALIASES = {
        "hue": "h",
        "saturation": "s",
        "lightness": "l"
    }
    WHITE = WHITES['2deg']['D65']
    GAMUT_CHECK = 'srgb'

    def normalize(self, coords: Vector) -> Vector:
        """Normalize coordinates."""

        if coords[1] < 0:
            coords[1] *= -1.0
            coords[0] += 180.0
        coords[0] %= 360.0
        return coords

    def is_achromatic(self, coords: Vector) -> bool:
        """Check if color is achromatic."""

        return abs(coords[1]) < 1e-4 or coords[2] > (1 - 1e-7) or coords[2] < 1e-08

    def to_base(self, coords: Vector) -> Vector:
        """To LChuv from HSLuv."""

        return cubehelix_to_srgb(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From LChuv to HSLuv."""

        return srgb_to_cubehelix(coords)
