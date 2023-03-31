"""Tools for dynamic achromatic response."""
from __future__ import annotations
from .. import algebra as alg
import bisect
from typing import Any
from ..types import Vector, VectorLike
from abc import ABCMeta, abstractmethod
import math


class Achromatic(metaclass=ABCMeta):
    """Calculate a spline that follows a color's achromatic response."""

    L_IDX = 0
    C_IDX = 1
    H_IDX = 2

    def __init__(
        self,
        data: list[Vector] | None = None,
        threshold_upper: float = float('inf'),
        threshold_lower: float = float('inf'),
        threshold_cutoff: float = float('inf'),
        spline: str = 'linear',
        mirror: bool = False,
        **kwargs: Any
    ) -> None:
        """
        Initialize.

        `tuning`: Either a dictionary of `low`, `mid`, and `high`, each specifying a start, end, step, and scale
            used to build a portion of the spline representing the achromatic response or a list containing the
            the pre-calculated spline points.
        `threshold_upper`: threshold above achromatic curve.
        `threshold_lower`: threshold below achromatic curve.
        `threshold_cutoff`: threshold of chroma above which we will assume colors are not achromatic.
        `spline`: spline type.
        `mirror`: Mirror response across lightness axis at zero.
        """

        self.mirror = mirror
        self.threshold_upper = threshold_upper
        self.threshold_lower = threshold_lower
        self.threshold_cutoff = threshold_cutoff

        self.domain = []  # type: list[float]
        self.min_colorfulness = 1e10
        self.min_lightness = 1e10
        self.spline_type = spline

        # Create a spline that maps the achromatic range for the SDR range
        if data is not None:
            self.setup_achromatic_response(data, **kwargs)

    def dump(self) -> list[VectorLike] | None:  # pragma: no cover
        """Dump data points."""

        if self.spline_type == 'linear':
            return list(zip(*self.spline.points))
        else:
            # Strip off the data points used to coerce the spline through the end.
            return list(zip(*self.spline.points))[1:-1]

    @abstractmethod
    def convert(self, coords: Vector, **kwargs: Any) -> Vector:
        """Convert an sRGB color to the desired space."""

    def calc_achromatic_response(
        self,
        parameters: list[tuple[int, int, int, float]],
        **kwargs: Any
    ) -> None:  # pragma: no cover
        """
        Calculate the achromatic response.

        Used to precalculate the best response.
        """

        points = []  # type: list[list[float]]
        for segment in parameters:
            start, end, step, scale = segment
            for p in range(start, end, step):
                color = self.convert([p / scale] * 3, **kwargs)
                l, c, h = color[self.L_IDX], color[self.C_IDX], color[self.H_IDX]
                if l < self.min_lightness:
                    self.min_lightness = l
                if c < self.min_colorfulness:
                    self.min_colorfulness = c
                self.domain.append(l)
                points.append([l, c, h % 360])
        self.spline = alg.interpolate(points, method=self.spline_type)
        self.hue = self.convert([1] * 3, **kwargs)[self.H_IDX] % 360
        self.ihue = (self.hue - 180) % 360

    def setup_achromatic_response(
        self,
        tuning: list[Vector],
        **kwargs: Any
    ) -> None:
        """Setup the achromatic response."""

        points = []  # type: list[list[float]]
        for entry in tuning:
            l, c, h = entry
            if l < self.min_lightness:
                self.min_lightness = l
            if c < self.min_colorfulness:
                self.min_colorfulness = c
            points.append([l, c, h])
            self.domain.append(l)
        self.spline = alg.interpolate(points, method=self.spline_type)
        self.hue = self.convert([1] * 3, **kwargs)[self.H_IDX] % 360
        self.ihue = (self.hue - 180) % 360

    def scale(self, point: float) -> float:
        """Scale the lightness to match the range."""

        if point <= self.domain[0]:
            point = (point - self.domain[0]) / (self.domain[-1] - self.domain[0])
        elif point >= self.domain[-1]:
            point = 1.0 + (point - self.domain[-1]) / (self.domain[-1] - self.domain[0])
        else:
            regions = len(self.domain) - 1
            size = (1 / regions)
            index = 0
            adjusted = 0.0
            index = bisect.bisect(self.domain, point) - 1
            a, b = self.domain[index:index + 2]
            l = b - a
            adjusted = ((point - a) / l) if l else 0.0
            point = size * index + (adjusted * size)
        return point

    def get_ideal_chroma(self, l: float) -> float:
        """Get the ideal chroma."""

        if math.isnan(l):
            return 0.0

        elif self.mirror and l < 0.0:
            return self.spline(self.scale(abs(l)))[1]

        return self.spline(self.scale(l))[1]

    def get_ideal_hue(self, l: float) -> float:
        """Get the ideal chroma."""

        if math.isnan(l):
            return 0.0

        elif self.mirror and l < 0.0:
            return (self.spline(self.scale(abs(l)))[2] - 180) % 360

        return self.spline(self.scale(l))[2]

    def get_ideal_ab(self, l: float) -> tuple[float, float]:
        """Get the ideal rectangular form of chroma and hue, the components a and b."""

        if math.isnan(l):
            return 0.0, 0.0

        return alg.polar_to_rect(self.get_ideal_chroma(l), self.get_ideal_hue(l))

    def test(self, l: float, c: float, h: float) -> bool:
        """Test if the current color is achromatic."""

        # If colorfulness is past this limit, we'd have to have a lightness
        # so high, that our test has already broken down.
        if c > self.threshold_cutoff or (not self.mirror and l < 0.0):
            return False

        # If we are higher than 1, we are extrapolating;
        # otherwise, use the spline.
        flip = self.mirror and l < 0.0
        la = abs(l)
        point = self.scale(la if flip else l)
        if la < self.min_lightness and c < self.min_colorfulness:  # pragma: no cover
            return True
        else:
            c2, h2 = self.spline(point)[1:]
            if flip:
                h2 = (h2 - 180) % 360
        diff = c2 - c
        hdiff = abs(h % 360 - h2)
        if hdiff > 180:  # pragma: no cover
            hdiff = 360 - hdiff
        return (
            ((diff >= 0 and diff < self.threshold_upper) or (diff < 0 and abs(diff) < self.threshold_lower)) and
            (c2 < 1e-5 or hdiff < 0.01)
        )
