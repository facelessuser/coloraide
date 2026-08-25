"""Check if color is in visible gamut."""
from __future__ import annotations
import math
from ..cat import WHITES
from .. import algebra as alg
from .. import util
from . import Gamut
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  #pragma: no cover
    from ..color import Color

XYw = WHITES['2deg']['D65']
XYZ_D65 = util.xy_to_xyz(WHITES['2deg']['D65'])


class VisibleSpectrum(Gamut):
    """The visible spectrum."""

    NAME = 'visible-spectrum'

    def in_gamut(
        self,
        color: Color,
        tolerance: float,
        xy_tolerance: float | None = 1e-3,
        ignore_luminance: bool = False,
        **kwargs: Any
    ) -> bool:
        """See if color is within the spectral locus."""

        if xy_tolerance is None:
            xy_tolerance = tolerance

        # Get white and xyY coordinates
        white = color.white('xy-1931')
        xyY = color.split_chromaticity('xy-1931')
        xy = xyY[:2]
        l = xyY[-1]

        # Get the dominant wavelength which will yield the point on the spectral locus in our direction
        wave, dominant = color.wavelength()[:2]

        # See if we have an achromatic color
        if math.isnan(wave):
            oog_chroma = False
        else:
            # Calculate magnitude with vector normalized such that white is the origin
            xy_temp = alg.subtract(xy, white, dims=alg.D1)
            m1 = math.sqrt(xy_temp[0] ** 2 + xy_temp[1] ** 2)
            xy_temp = alg.subtract(dominant, white, dims=alg.D1)
            m2 = math.sqrt(xy_temp[0] ** 2 + xy_temp[1] ** 2)
            oog_chroma = m1 > (m2 + xy_tolerance)

        oog_lum = False if ignore_luminance else (l > (1 + tolerance) or l < (0 - tolerance))

        # See if we are within tolerance
        return not oog_lum and not oog_chroma

    def fit(
        self,
        color: Color,
        xy_tolerance: float | None = 1e-3,
        ignore_luminance: bool = False,
        **kwargs: Any
    ) -> None:
        """Fit color to the visible spectrum."""

        if xy_tolerance is None:
            xy_tolerance = 0.0

        # Get white and xyY coordinates
        white = color.white('xy-1931')
        xyY = color.split_chromaticity('xy-1931')
        xy = xyY[:2]
        l = xyY[-1]

        # Get the dominant wavelength which will yield the point on the spectral locus in our direction
        wave, dominant = color.wavelength()[:2]

        # See if we have an achromatic color
        if math.isnan(wave):
            dominant = white
            oog_chroma = False
        else:
            # Calculate magnitude with vector normalized such that white is the origin
            xy_temp = alg.subtract(xy, white, dims=alg.D1)
            m1 = math.sqrt(xy_temp[0] ** 2 + xy_temp[1] ** 2)
            xy_temp = alg.subtract(dominant, white, dims=alg.D1)
            m2 = math.sqrt(xy_temp[0] ** 2 + xy_temp[1] ** 2)

            # Adjust range to pull in color relative to the spectral locus
            if xy_tolerance:
                m2 += xy_tolerance
                h = math.degrees(math.atan2(xy_temp[1], xy_temp[0])) % 360
                dominant = list(alg.add(alg.polar_to_rect(m2, h), white, dims=alg.D1))

            # Check if color is outside the spectral locus
            oog_chroma = m1 > m2

        oog_lum = False if ignore_luminance else (l > 1 or l < 0)

        # Adjust color is out of luminance range or outside the spectral locus limits
        if oog_lum or l < 0 or oog_chroma:
            color.update(
                color.chromaticity(
                    color.space(),
                    [*(dominant if oog_chroma else xy), alg.clamp(l, 0, 1)],
                    'xy-1931',
                    white=white,
                    scale=False
                )
            )
