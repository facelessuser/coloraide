"""
Helmlch class.

LCh based on the Helmlab MetricSpace - 13-stage perceptual color space.

A data-driven analytical color space trained on 64,000+ individual human
color perception observations. Achieves 20.1% lower STRESS than CIEDE2000
on the COMBVD dataset (3,813 color pairs).

Pipeline: XYZ -> M1 -> γ -> M2 -> hue correction -> H-K -> cubic L -> dark L
   -> hue-dependent chroma scale -> chroma power -> L-dependent chroma scale
   -> HLC interaction -> hue-dependent lightness -> neutral correction -> rotation

- https://arxiv.org/abs/2602.23010
- https://github.com/Grkmyldz148/helmlab
"""
from __future__ import annotations
from .lch import LCh
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE


class Helmlch(LCh):
    """Helmlch class."""

    BASE = "helmlab"
    NAME = "helmlch"
    SERIALIZE = ("--helmlch",)
    CHANNELS = (
        Channel("l", 0.0, 1.1436213369754669),
        Channel("c", 0.0, 1.0),
        Channel("h", flags=FLG_ANGLE)
    )
    CHANNEL_ALIASES = {
        "lightness": "l",
        "chroma": "c",
        "hue": "h"
    }
    WHITE = WHITES['2deg']['ASTM-E308-D65']
