"""
OkLrCh.

Applies a toe function to the OkLCh lightness.

> This new lightness estimate closely matches the lightness estimate of CIELab overall and is nearly equal at 50%
> lightness (Y for CIELab L is 0.18406, and  Lr 0.18419) which is useful for compatibility. Worth noting is that it is
> not possible to have a lightness scale that is perfectly uniform independent of viewing conditions and background
> color. This new lightness function is however a better trade-off for cases with a well defined reference white.

https://bottosson.github.io/posts/colorpicker/#intermission---a-new-lightness-estimate-for-oklab
"""
from . oklch import OkLCh


class OkLrCh(OkLCh):
    """OkLrCh."""

    BASE = "oklrab"
    NAME = "oklrch"
    SERIALIZE = ("--oklrch",)
