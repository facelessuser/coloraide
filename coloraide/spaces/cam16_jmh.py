"""
CAM16 class (JMh).

https://www.imaging.org/site/PDFS/Papers/2000/PICS-0-81/1611.pdf
https://observablehq.com/@jrus/cam16
https://arxiv.org/abs/1802.06067
https://doi.org/10.1002/col.22131
"""
from __future__ import annotations
import bisect
from ..spaces import Space, LChish
from .cam16 import Environment, CAM16, xyz_d65_to_cam16_jmh, cam16_jab_to_cam16_jmh, cam16_jmh_to_cam16_jab
from .srgb_linear import lin_srgb_to_xyz
from .srgb import lin_srgb
from ..cat import WHITES
from ..channels import Channel, FLG_ANGLE
from .. import algebra as alg
from ..types import Vector


class Achromatic:
    """
    Test if color is achromatic.

    Should work quite well through the SDR range. Can reasonably handle HDR range out to 3
    which is far enough for anything practical.

    We use a spline mainly to quickly fit the line in a way we do not have to analyze and tune.
    """

    CONVERTER = staticmethod(xyz_d65_to_cam16_jmh)
    L_IDX = 0
    C_IDX = 1
    H_IDX = 2

    def __init__(
        self,
        tuning: dict[str, tuple[int, int, int, float]],
        threshold: float,
        env: Environment,
        spline: str
    ) -> None:
        """Initialize."""

        self.threshold = threshold

        # Create a spline that maps the achromatic range for the SDR range
        points = []  # type: list[list[float]]
        self.domain = []  # type: list[float]
        self.max_colorfulness = 1e-10
        self.spline = None
        if not env.discounting:
            self.iter_achromatic_response(env, points, *tuning['low'])
            self.iter_achromatic_response(env, points, *tuning['mid'])
            self.iter_achromatic_response(env, points, *tuning['high'])
            self.max_colorfulness = round(self.max_colorfulness, 3) + 1
            self.spline = alg.interpolate(points, method=spline)
        # Transform seems to favor a particular achromatic hue, capture the one at white
        # to replace achromatic NaN hues with.
        self.hue = self.CONVERTER(lin_srgb_to_xyz(lin_srgb([1] * 3)), env)[self.H_IDX]

    def iter_achromatic_response(
        self,
        env: Environment,
        points: list[list[float]],
        start: int,
        end: int,
        step: int,
        scale: float
    ) -> None:
        """
        Iterate the achromatic response of the space.

        Save points of lightness vs colorfulness. Also, track the domain.
        """

        for p in range(start, end, step):
            c = self.CONVERTER(lin_srgb_to_xyz(lin_srgb([p / scale] * 3)), env)
            j, m = c[self.L_IDX], c[self.C_IDX]
            if m > self.max_colorfulness:
                self.max_colorfulness = m
            self.domain.append(j)
            points.append([j, m])

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

    def get_ideal_chroma(self, j: float, m: float) -> float:
        """Get the ideal chroma."""

        if j < 0.0:  # pragma: no cover
            return 0.0

        if self.spline is not None:
            point = self.scale(j)
            m2 = self.spline(point)[1]
            if abs(m2 - m) < self.threshold:
                return m
            elif m < m2:
                return m2

        # This would be for `discounting=True`,
        # which we do not run with currently.
        return m  # pragma: no cover

    def test(self, j: float, m: float) -> bool:
        """Test if the current color is achromatic."""

        # If colorfulness is past this limit, we'd have to have a lightness
        # so high, that our test has already broken down.
        if m > self.max_colorfulness:
            return False

        # This is for when "discounting" as colorfulness should be very near zero
        if self.spline is None:  # pragma: no cover
            return True

        # If we are higher than 1, we are extrapolating;
        # otherwise, use the spline.
        point = self.scale(j)
        if point < 0:  # pragma: no cover
            m2 = 0.0
        else:
            m2 = self.spline(point)[1]
        return m < m2 or abs(m2 - m) < self.threshold


class CAM16JMh(LChish, Space):
    """CAM16 class (JMh)."""

    BASE = "cam16"
    NAME = "cam16-jmh"
    SERIALIZE = ("--cam16-jmh",)
    CHANNELS = (
        Channel("j", 0.0, 100.0, limit=(0.0, None)),
        Channel("m", 0, 105.0, limit=(0.0, None)),
        Channel("h", 0.0, 360.0, flags=FLG_ANGLE)
    )
    CHANNEL_ALIASES = {
        "lightness": "j",
        "colorfulness": 'm',
        "hue": 'h'
    }
    WHITE = WHITES['2deg']['D65']
    # Assuming the same environment as our CAM16 Jab. If we used a different
    # environment (viewing conditions), we'd have to have our BASE set as
    # a Jab that shared those conditions, or resolve directly from XYZ.
    ENV = CAM16.ENV

    # Achromatic detection
    ACHROMATIC = Achromatic(
        {
            'low': (0, 25, 1, 100.0),
            'mid': (25, 101, 9, 80.0),
            'high': (101, 302, 5, 60.0)
        },
        0.032,
        ENV,
        'monotone'
    )

    def achromatic_hue(self) -> float:
        """Ideal achromatic hue."""

        return self.ACHROMATIC.hue

    def normalize(self, coords: Vector) -> Vector:
        """Normalize the color ensuring no unexpected NaN and achromatic hues are NaN."""

        coords = alg.no_nans(coords)
        j, m = coords[:2]
        if self.ACHROMATIC.test(j, m):
            coords[2] = alg.NaN
        return coords

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ from CAM16."""

        j, m = coords[:2]
        if self.ACHROMATIC.test(j, m):
            coords[1] = self.ACHROMATIC.get_ideal_chroma(j, m)
            coords[2] = self.ACHROMATIC.hue

        return cam16_jmh_to_cam16_jab(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ to CAM16."""

        jmh = cam16_jab_to_cam16_jmh(coords)
        return self.normalize(jmh)
