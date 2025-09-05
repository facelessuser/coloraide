"""
Rec. 2020 color space (display referred).

Uses the display referred EOTF as specified in BT.1886.

- https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.2020-2-201510-I!!PDF-E.pdf
- https://www.itu.int/dms_pubrec/itu-r/rec/bt/r-rec-bt.1886-0-201103-i!!pdf-e.pdf
"""
from __future__ import annotations
from .srgb_linear import sRGBLinear
from .. import algebra as alg
from ..types import Vector

GAMMA = 2.40
IGAMMA = 1 / GAMMA


def inverse_eotf_bt1886(rgb: Vector) -> Vector:
    """
    Inverse ITU-R BT.1886 EOTF.

    ```
    igamma = 1 / gamma

    d = lw ** igamma - lb ** igamma
    a = d ** gamma
    b = lb ** igamma / d
    return [math.copysign(a * alg.spow(abs(l) / a, igamma) - b, l) for l in rgb]
    ```

    When using `lb == 0`, `lw == 1`, and gamma of `2.4`, this simplifies to a simple power of `1 / 2.4`.
    """

    return [alg.spow(v, IGAMMA) for v in rgb]


def eotf_bt1886(rgb: Vector) -> Vector:
    """
    ITU-R BT.1886 EOTF.

    ```
    igamma = 1 / gamma

    d = lw ** igamma - lb ** igamma
    a = d ** gamma
    b = lb ** igamma / d
    return [math.copysign(a * alg.spow(max(abs(v) + b, 0), gamma), v) for v in rgb]
    ```

    When using `lb == 0`, `lw == 1`, and gamma of `2.4`, this simplifies to a simple power of `2.4`.
    """

    return [alg.spow(v, GAMMA) for v in rgb]


class Rec2020(sRGBLinear):
    """Rec 2020 class."""

    BASE = "rec2020-linear"
    NAME = "rec2020"

    def linear(self) -> str:
        """Return linear version of the RGB (if available)."""

        return self.BASE

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from Rec. 2020."""

        return eotf_bt1886(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to Rec. 2020."""

        return inverse_eotf_bt1886(coords)
