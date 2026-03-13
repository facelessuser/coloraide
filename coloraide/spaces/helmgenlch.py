"""
Helmgenlch class.

LCh based on the Helmlab GenSpace: generation-optimized color space for interpolation.

A simplified pipeline (`XYZ -> M1 -> cbrt -> M2 -> NC`) optimized for
perceptually uniform gradients, palette generation, and color-mix.
Achieves 6x better hue accuracy than Oklab with 10% better perceptual
distance prediction.

Key differences from Helmlab (MetricSpace):
  - Shared gamma = 1/3 (cube root, guarantees achromatic a=b=0)
  - No enrichment stages (simpler, faster, better for generation)
  - Different M1/M2 matrices (Phase1H-optimized)

- https://arxiv.org/abs/2602.23010
- https://github.com/Grkmyldz148/helmlab
"""
from __future__ import annotations
from .lch import LCh
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE


class Helmgenlch(LCh):
    """Helmgenlch class."""

    BASE = "helmgen"
    NAME = "helmgenlch"
    SERIALIZE = ("--helmgenlch",)
    CHANNELS = (
        Channel("l", 0.0, 1.168140042703694),
        Channel("c", 0.0, 1.0),
        Channel("h", flags=FLG_ANGLE)
    )
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }
    WHITE = WHITES['2deg']['ASTM-E308-D65']
