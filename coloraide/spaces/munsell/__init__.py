"""
Munsell color space.

The Munsell system is not defined by a formula. It is defined by the Munsell Renotation data, a table that maps
Munsell Hue, Value, and Chroma to CIE xyY (CIE 1931 2 degree observer, Illuminant C). To convert, we interpolate
that table.

The data used here is `all.dat` from the RIT Munsell Color Science Laboratory
(https://www.rit.edu/science/munsell-color-science-lab-educational-resources). Unlike `real.dat`, it includes
the extrapolated colors, which are required to fully enclose the real colors near the MacAdam limits.

Channels:

- `h`: Munsell Hue as an angle. The 100 step Munsell hue circle is mapped to 360 degrees (3.6 degrees per hue step).
  `0` is `0R` (also called `10RP`) and the hue families progress in this order, each spanning 36 degrees:
  `R, YR, Y, GY, G, BG, B, PB, P, RP`. `5R` is 18 degrees, `10R` (`0YR`) is 36 degrees, `5YR` is 54 degrees, etc.
- `v`: Munsell Value. `0` is black and `10` is the perfect reflecting diffuser.
- `c`: Munsell Chroma. `0` is neutral and there is no theoretical upper limit.

Forward conversion (Munsell to XYZ):

- Value controls luminance only, via the fifth order polynomial from ASTM D1535.
- The data supplies the chromaticities of Munsell colors on a grid: for each integer Value plane, 40 hue lines
  (every 2.5 hue steps), each with nodes at every even Chroma. Between nodes, all interpolation is done in polar
  coordinates (angle and radius) about the Illuminant C white point. This avoids the radius shrinking you get when
  linearly interpolating between points on a circle.
- Between Value planes, chromaticities are linearly interpolated by luminance.

Inverse conversion (XYZ to Munsell):

- Value is solved from luminance alone (Newton's method on the ASTM polynomial).
- Hue and Chroma are then solved for so that the forward conversion reproduces the target chromaticity. The initial
  guess comes from the nearest Value plane (a lookup that does not account for the blend between planes), and a
  few Newton iterations then refine it against the exact forward conversion, so the two directions round trip.

Other notes:

- The renotation luminance is relative to magnesium oxide (`Y == 102.57` for a perfect Value of 10). ColorAide
  expects luminance relative to the perfect reflecting diffuser, so we only use the table's chromaticities and
  calculate luminance from the polynomial instead (`Y == 1` at Value 10).
- Chroma beyond the table's range is linearly extrapolated and Value beyond the table's range uses the nearest
  plane, so any color can be converted, but the further outside of the data, the less meaningful the results.
"""
from __future__ import annotations
import math
import re
from bisect import bisect_right
from functools import lru_cache
from ... import util
from ...cat import WHITES
from ...channels import Channel, FLG_ANGLE
from ...css import serialize
from ..lch import LCh
from ...types import Vector, VectorLike
from collections.abc import Sequence
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color

XC, YC = WHITES['2deg']['C']
HUE_STEP = 2.5
HUE_LINES = 40
HUE_ANGLE = 3.6
TAU = math.tau

# The Munsell hue families in order around the hue circle, each spanning 10 hue steps.
HUE_FAMILIES = ('R', 'YR', 'Y', 'GY', 'G', 'BG', 'B', 'PB', 'P', 'RP')
NUM = r'(?:\d+(?:\.\d*)?|\.\d+)'
RE_NOTATION = re.compile(
    fr'''(?ix)
    (?:
        # Chromatic: `5R 4/14`, `2.8Y 6.95/2.3`
        (?P<hue>{NUM})\s*(?P<family>RP|PB|BG|GY|YR|R|Y|G|B|P)\s*(?P<value>{NUM})\s*/\s*(?P<chroma>{NUM})
        |
        # Neutral: `N 5/`, `N5`
        N\s*(?P<neutral>{NUM})(?:\s*/)?
    )
    '''
)

# The Munsell hue lines are every 2.5 hue steps from `0R` to `7.5RP`.
Line = tuple[list[float], list[float]]
Plane = list[Line]


def value_to_y(value: float) -> float:
    """
    Convert Munsell Value to relative luminance.

    The ASTM D1535 polynomial. Negative values are mirrored so the function remains continuous through zero.
    """

    v = abs(value)
    y = v * (1.1914 + v * (-0.22533 + v * (0.23352 + v * (-0.020484 + v * 0.00081939)))) * 0.01
    return math.copysign(y, value)


def y_to_value(y: float) -> float:
    """Convert relative luminance to Munsell Value (the inverse of the ASTM D1535 polynomial)."""

    target = abs(y) * 100
    if target == 0.0:
        return 0.0

    # Priest et al. approximation is a good start, and the polynomial is monotonic, so Newton's method is stable.
    v = 10 * math.sqrt(abs(y))
    for _ in range(50):
        f = v * (1.1914 + v * (-0.22533 + v * (0.23352 + v * (-0.020484 + v * 0.00081939)))) - target
        d = 1.1914 + v * (-0.45066 + v * (0.70056 + v * (-0.081936 + v * 0.00409695)))
        dv = f / d
        v -= dv
        if v <= 0.0:
            v = 1e-12
        if abs(dv) < 1e-14 * max(1.0, v):
            break
    return math.copysign(v, y)


def normalize_angle(angle: float) -> float:
    """Normalize an angle in radians to [-pi, pi], which makes the difference of two angles the shortest way around."""

    return angle - TAU * round(angle / TAU)


def to_polar(flat: tuple[float, ...]) -> Line:
    """
    Convert a hue line's xy nodes (chroma 2, 4, 6, ...) to polar coordinates about the white point.

    A node is added for chroma 0 (the white point itself) and angles are unwrapped along the line.
    """

    thetas = [0.0]
    rhos = [0.0]
    last = 0.0
    for i in range(0, len(flat), 2):
        dx = flat[i] - XC
        dy = flat[i + 1] - YC
        theta = math.atan2(dy, dx)
        if i:
            theta = last + normalize_angle(theta - last)
        thetas.append(theta)
        rhos.append(math.sqrt(dx ** 2 + dy ** 2))
        last = theta
    thetas[0] = thetas[1]
    return thetas, rhos


def mid_line(a: Line, b: Line) -> Line:
    """Create a hue line half way between two neighboring hue lines by taking the midpoint of each pair of nodes."""

    n = min(len(a[1]), len(b[1]))
    thetas = [a[0][i] + 0.5 * normalize_angle(b[0][i] - a[0][i]) for i in range(n)]
    rhos = [(a[1][i] + b[1][i]) * 0.5 for i in range(n)]
    return thetas, rhos


@lru_cache(maxsize=1)
def get_tables() -> tuple[list[float], list[Plane]]:
    """Convert the renotation data into polar hue lines on first use, returning the luminance of each value plane."""

    from .renotation_data import MUNSELL_RENOTATION

    ys: list[float] = []
    planes: list[Plane] = []
    for value, data in sorted(MUNSELL_RENOTATION.items()):
        lines = [to_polar(flat) if flat else ([], []) for flat in data]
        # The data is missing a line or two in the darkest plane, so create it from its neighbors.
        for i, line in enumerate(lines):
            if not line[1]:
                lines[i] = mid_line(lines[i - 1], lines[(i + 1) % HUE_LINES])
        ys.append(value_to_y(value))
        planes.append(lines)
    return ys, planes


def line_point(line: Line, chroma: float) -> tuple[float, float]:
    """Get the polar coordinates on a hue line for a given chroma, extrapolating past the final node."""

    thetas, rhos = line
    s = chroma * 0.5
    j = min(int(s), len(rhos) - 2)
    s -= j
    return thetas[j] + s * (thetas[j + 1] - thetas[j]), rhos[j] + s * (rhos[j + 1] - rhos[j])


def plane_xy(lines: Plane, hue: float, chroma: float) -> tuple[float, float]:
    """Interpolate the xy chromaticity for a hue number and Chroma on a Value plane."""

    h = (hue % 100.0) / HUE_STEP
    i = int(h)
    t = h - i
    t0, r0 = line_point(lines[i % HUE_LINES], chroma)
    t1, r1 = line_point(lines[(i + 1) % HUE_LINES], chroma)
    theta = t0 + t * normalize_angle(t1 - t0)
    rho = r0 + t * (r1 - r0)
    return XC + rho * math.cos(theta), YC + rho * math.sin(theta)


def locate_plane(ys: list[float], y: float) -> tuple[int, int, float]:
    """
    Find the value planes surrounding a luminance and the blend between them.

    Planes beyond the data are clamped.
    """

    if y <= ys[0]:
        return 0, 0, 0.0
    last = len(ys) - 1
    if y >= ys[last]:
        return last, last, 0.0
    hi = bisect_right(ys, y)
    lo = hi - 1
    return lo, hi, (y - ys[lo]) / (ys[hi] - ys[lo])


def interpolate_xy(a: Plane, b: Plane, w: float, hue: float, chroma: float) -> tuple[float, float]:
    """Get the chromaticity of a color between two value planes."""

    x, y = plane_xy(a, hue, chroma)
    if w:
        x1, y1 = plane_xy(b, hue, chroma)
        x += w * (x1 - x)
        y += w * (y1 - y)
    return x, y


def guess_hue_chroma(lines: Plane, theta: float, rho: float) -> tuple[float, float]:
    """
    Get an initial hue number and chroma for a chromaticity on a single Value plane.

    Each hue line is inverted by the radius to get the line's angle and chroma at the target's radius. The hue lines
    do not cross, so these angles tile the circle and the target lands between two of them. This is not the exact
    inverse of the forward interpolation (which interpolates at equal chroma, not equal radius), but it's close.
    """

    points = []
    for thetas, rhos in lines:
        j = min(bisect_right(rhos, rho) - 1, len(rhos) - 2)
        s = (rho - rhos[j]) / (rhos[j + 1] - rhos[j])
        points.append((thetas[j] + s * (thetas[j + 1] - thetas[j]), 2 * (j + s)))

    best = (0.0, 0.0)
    nearest = TAU
    for i in range(HUE_LINES):
        t0, c0 = points[i]
        t1, c1 = points[(i + 1) % HUE_LINES]
        span = normalize_angle(t1 - t0)
        d = normalize_angle(theta - t0)
        if span > 0.0 and 0.0 <= d < span:
            t = d / span
            return (i + t) * HUE_STEP, c0 + t * (c1 - c0)
        # Fallback if something is not well ordered: remember the closest line
        if abs(d) < nearest:
            nearest = abs(d)
            best = (i * HUE_STEP, c0)
    return best  # pragma: no cover


def munsell_to_xyz(coords: VectorLike) -> Vector:
    """Convert Munsell (hue in degrees, value, chroma) to XYZ under Illuminant C."""

    hue, value, chroma = coords
    lum = value_to_y(value)
    if lum == 0.0:
        return [0.0, 0.0, 0.0]

    ys, planes = get_tables()
    lo, hi, w = locate_plane(ys, abs(lum))
    x, y = interpolate_xy(planes[lo], planes[hi], w, hue / HUE_ANGLE, abs(chroma))

    # Negative chroma is the point reflected through the white point
    if chroma < 0.0:
        x = 2 * XC - x
        y = 2 * YC - y
    return util.xy_to_xyz((x, y), lum)


def xyz_to_munsell(xyz: VectorLike) -> Vector:
    """Convert XYZ under Illuminant C to Munsell (hue in degrees, value, chroma)."""

    lum = xyz[1]
    value = y_to_value(lum)
    if lum == 0.0:
        return [0.0, 0.0, 0.0]

    tx, ty, _ = util.xyz_to_xyY(xyz, (XC, YC))
    dx = tx - XC
    dy = ty - YC
    rho = math.hypot(dx, dy)
    if rho < 1e-15:
        return [0.0, value, 0.0]

    ys, planes = get_tables()
    lo, hi, w = locate_plane(ys, abs(lum))
    a, b = planes[lo], planes[hi]
    hue, chroma = guess_hue_chroma(a if w < 0.5 else b, math.atan2(dy, dx), rho)

    # Newton's method with a finite difference Jacobian. The forward interpolation is piecewise smooth, so once we
    # are in the right cell, we converge nearly immediately.
    step = 1e-5
    x, y = interpolate_xy(a, b, w, hue, chroma)
    rx = x - tx
    ry = y - ty
    err = rx * rx + ry * ry
    for _ in range(25):
        if err < 1e-28:
            break
        x1, y1 = interpolate_xy(a, b, w, hue + step, chroma)
        x2, y2 = interpolate_xy(a, b, w, hue, chroma + step)
        j11 = (x1 - x) / step
        j21 = (y1 - y) / step
        j12 = (x2 - x) / step
        j22 = (y2 - y) / step
        det = j11 * j22 - j12 * j21
        if abs(det) < 1e-30:
            break
        dh = -(j22 * rx - j12 * ry) / det
        dc = -(j11 * ry - j21 * rx) / det

        # Backtrack if the full step makes things worse (e.g. crossing a kink in the piecewise interpolation)
        scale = 1.0
        for _ in range(8):
            nh = hue + dh * scale
            nc = max(chroma + dc * scale, 0.0)
            nx, ny = interpolate_xy(a, b, w, nh, nc)
            nrx = nx - tx
            nry = ny - ty
            nerr = nrx * nrx + nry * nry
            if nerr < err:
                break
            scale *= 0.5
        else:
            break
        hue, chroma, x, y, rx, ry, err = nh, nc, nx, ny, nrx, nry, nerr

    return [(hue % 100.0) * HUE_ANGLE, value, chroma]


def notation_to_munsell(m: re.Match[str]) -> Vector | None:
    """
    Convert a match of the Munsell notation expression to Munsell coordinates.

    A hue is a number in the range 0 - 10 followed by a hue family. `0` of a family is the same as `10` of the
    previous family (`0R` is `10RP`). Neutral colors have no hue and are given a null (`NaN`) hue.
    """

    neutral = m.group('neutral')
    if neutral is not None:
        return [math.nan, float(neutral), 0.0]

    within = float(m.group('hue'))
    if within > 10.0:
        return None
    hue = HUE_FAMILIES.index(m.group('family').upper()) * 10 + within
    return [(hue % 100.0) * HUE_ANGLE, float(m.group('value')), float(m.group('chroma'))]


def munsell_to_notation(
    coords: Vector,
    precision: int | Sequence[int],
    rounding: str,
    threshold: float,
    default: int = util.DEF_PREC
) -> str:
    """
    Convert Munsell coordinates to Munsell notation, e.g. `2.8Y 6.95/2.3`.

    Colors with chroma below the achromatic threshold, or that round to a chroma of zero, are neutral (`N 5/`).
    Precision is applied to the hue within its family, not the hue angle.
    """

    h, v, c = coords
    if c < 0.0:
        # Negative chroma has no notation, so use the equivalent color with positive chroma
        h, v, c = xyz_to_munsell(munsell_to_xyz(coords))

    is_list = not isinstance(precision, int)

    def fmt(value: float, index: int) -> str:
        return util.fmt_float(
            value,
            util.get_index(precision, index, default) if is_list else precision,  # type: ignore[arg-type]
            rounding
        )

    value = fmt(v, 1)
    chroma = fmt(c, 2)
    if abs(c) < threshold or float(chroma) == 0.0:
        return f'N {value}/'

    hue_number = (h / HUE_ANGLE) % 100.0
    family = int(hue_number // 10)
    hue = fmt(hue_number - family * 10, 0)

    # A hue of `0` in a family is the `10` of the previous family, which is also what a hue rounding to zero is
    if float(hue) == 0.0:
        family = (family - 1) % 10
        hue = '10'
    return f'{hue}{HUE_FAMILIES[family]} {value}/{chroma}'


class Munsell(LCh):
    """Munsell class."""

    BASE = "xyz-d65"
    NAME = "munsell"
    SERIALIZE = ("--munsell",)
    # Munsell is defined relative to Illuminant C, so ColorAide will chromatically adapt the XYZ D65 base for us.
    WHITE = WHITES['2deg']['C']
    CHANNEL_ALIASES = {
        "lightness": "v",
        "value": "v",
        "chroma": "c",
        "hue": "h"
    }
    CHANNELS = (
        Channel("h", flags=FLG_ANGLE),
        Channel("v", 0.0, 10.0),
        Channel("c", 0.0, 35.0)
    )

    def lightness_name(self) -> str:
        """Get lightness name."""

        return "v"

    def names(self) -> tuple[Channel, ...]:
        """Return LCh-ish names in the order L C h."""

        channels = self.channels
        return channels[1], channels[2], channels[0]

    def normalize(self, coords: Vector) -> Vector:
        """Normalize."""

        if coords[2] < 0.0:
            return self.from_base(self.to_base(coords))
        coords[0] = util.constrain_hue(coords[0])
        return coords

    def is_achromatic(self, coords: Vector) -> bool | None:
        """Check if color is achromatic."""

        # Account for both positive and negative chroma
        return abs(coords[2]) < self.achromatic_threshold

    def to_string(
        self,
        parent: Color,
        *,
        alpha: bool | None = None,
        precision: int | Sequence[int] | None = None,
        rounding: str | None = None,
        fit: str | bool | dict[str, Any] = True,
        none: bool = False,
        percent: bool | Sequence[bool] = False,
        angle: str = 'deg',
        notation: bool = False,
        **kwargs: Any
    ) -> str:
        """
        Convert to a string.

        By default, the `color(--munsell h v c)` form is used. If `notation` is enabled, Munsell notation is used
        instead (`2.8Y 6.95/2.3`, or `N 5/` for neutral colors). Notation has no way to express alpha or `none`
        values, so these are not included. `precision` and `rounding` are applied to the hue within its family
        (not the hue angle), value, and chroma.
        """

        if not notation:
            return super().to_string(
                parent,
                alpha=alpha,
                precision=precision,
                rounding=rounding,
                fit=fit,
                none=none,
                percent=percent,
                angle=angle,
                **kwargs
            )

        return munsell_to_notation(
            serialize.get_coords(parent, fit, False, False),
            parent.PRECISION if precision is None else precision,
            parent.ROUNDING if rounding is None else rounding,
            self.achromatic_threshold,
            parent.PRECISION
        )

    def match(
        self,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> tuple[tuple[Vector, float], int] | None:
        """Match Munsell notation, falling back to the normal color matching if it is not notation."""

        m = (RE_NOTATION.fullmatch if fullmatch else RE_NOTATION.match)(string, start)
        if m is not None:
            coords = notation_to_munsell(m)
            if coords is not None:
                return (coords, 1.0), m.end()
        return super().match(string, start, fullmatch)

    def to_base(self, coords: Vector) -> Vector:
        """To XYZ (Illuminant C) from Munsell."""

        return munsell_to_xyz(coords)

    def from_base(self, coords: Vector) -> Vector:
        """From XYZ (Illuminant C) to Munsell."""

        return xyz_to_munsell(coords)
