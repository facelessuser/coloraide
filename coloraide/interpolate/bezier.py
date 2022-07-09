"""Bezier interpolation."""
from .. import algebra as alg
from ..spaces import Cylindrical
from ..types import Vector, ColorInput
from typing import Optional, Callable, Sequence, Mapping, Type, Dict, List, Union, cast, Any, TYPE_CHECKING
from .common import stop, Interpolator, calc_stops, process_mapping, premultiply, postdivide

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def binomial_row(n: int) -> List[int]:
    """
    Binomial row.

    Return row in Pascal's triangle.
    """

    row = [1, 1]
    for i in range(n - 1):
        r = [1]
        x = 0
        for x in range(1, len(row)):
            r.append(row[x] + row[x - 1])
        r.append(row[x])
        row = r
    return row


class InterpolateBezier(Interpolator):
    """Interpolate Bezier."""

    def __init__(
        self,
        coordinates: List[Vector],
        names: Sequence[str],
        create: Type['Color'],
        easings: List[Optional[Callable[..., float]]],
        stops: Dict[int, float],
        space: str,
        out_space: str,
        progress: Optional[Union[Callable[..., float], Mapping[str, Callable[..., float]]]],
        premultiplied: bool
    ) -> None:
        """Initialize."""

        self.start = stops[0]
        self.end = stops[len(stops) - 1]
        self.stops = stops
        self.easings = easings
        self.coordinates = coordinates
        self.length = len(self.coordinates)
        self.names = names
        self.create = create
        self.progress = progress
        self.space = space
        self.out_space = out_space
        self.premultiplied = premultiplied

    def handle_undefined(self, coords: Vector) -> Vector:
        """Handle null values."""

        backfill = None
        for x in range(1, len(coords)):
            a = coords[x - 1]
            b = coords[x]
            if alg.is_nan(a) and not alg.is_nan(b):
                coords[x - 1] = b
            elif alg.is_nan(b) and not alg.is_nan(a):
                coords[x] = a
            elif alg.is_nan(a) and alg.is_nan(b):
                # Multiple undefined values, mark the start
                backfill = x - 1
                continue

            # Replace all undefined values that occurred prior to
            # finding the current defined value
            if backfill is not None:
                coords[backfill:x - 1] = [b] * (x - 1 - backfill)
                backfill = None

        return coords

    def interpolate(
        self,
        easing: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
        p2: float,
        first: float,
        last: float
    ) -> 'Color':
        """Interpolate."""

        n = self.length - 1
        row = binomial_row(n)
        channels = []
        for i, coords in enumerate(zip(*self.coordinates)):
            name = self.names[i]
            progress = None
            if isinstance(easing, Mapping):
                progress = easing.get(name)
                if progress is None:
                    progress = easing.get('all')
            else:
                progress = easing

            # Apply easing and scale properly between the colors
            t = alg.clamp(p2 if progress is None else progress(p2), 0.0, 1.0)
            t = t * (last - first) + first

            # Find new points using a bezier curve
            x = 1 - t
            s = 0.0
            for j, c in enumerate(self.handle_undefined(list(coords)), 0):
                s += row[j] * (x ** (n - j)) * (t ** j) * c

            channels.append(s)
        color = self.create(self.space, channels[:-1], channels[-1])
        if self.premultiplied:
            postdivide(color)
        return color.convert(self.out_space, in_place=True) if self.out_space != color.space() else color

    def __call__(self, p: float) -> 'Color':
        """Interpolate."""

        percent = alg.clamp(p, 0.0, 1.0)
        if percent > self.end:
            percent = self.end
        elif percent < self.start:
            percent = self.start
        last = self.start
        for i in range(1, self.length):
            s = self.stops[i]
            if percent <= s:
                r = s - last
                p2 = (percent - last) / r if r else 1
                easing = self.easings[i - 1]  # type: Any
                if easing is None:
                    easing = self.progress
                piece = 1 / (self.length - 1)
                return self.interpolate(easing, p2, (i - 1) * piece, i * piece)
            last = s

        # We shouldn't ever hit this, but provided for typing.
        # If we do hit this, it would be a bug.
        raise RuntimeError('Iterpolation could not be found for {}'.format(percent))  # pragma: no cover


def normalize_color(color: 'Color', space: str, premultiplied: bool) -> None:
    """Normalize color."""

    # Adjust to color to space and ensure it fits
    if not color.CS_MAP[space].EXTENDED_RANGE:
        if not color.in_gamut():
            color.fit()

    # Premultiply
    if premultiplied:
        premultiply(color)

    # Normalize hue
    if issubclass(color._space, Cylindrical):
        name = cast(Type[Cylindrical], color._space).hue_name()
        color.set(name, lambda h: cast(float, h % 360))


def color_bezier_lerp(
    create: Type['Color'],
    colors: List[ColorInput],
    space: str,
    out_space: str,
    progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
    premultiplied: bool,
    **kwargs: Any
) -> InterpolateBezier:
    """Bezier interpolation."""

    # Construct piecewise interpolation object
    stops = {}  # type: Any

    if space is None:
        space = create.INTERPOLATE

    if isinstance(colors[0], stop):
        current = create(colors[0].color)
        stops[0] = colors[0].stop
    elif not callable(colors[0]):
        current = create(colors[0])
        stops[0] = None
    else:
        raise ValueError('Cannot have an easing function as the first item in an interpolation list')

    if out_space is None:
        out_space = current.space()

    current.convert(space, in_place=True)
    normalize_color(current, space, premultiplied)

    easing = None  # type: Any
    easings = []  # type: Any
    coords = [current[:]]

    i = 0
    for x in colors[1:]:

        # Normalize all colors as Piecewise objects
        if isinstance(x, stop):
            i += 1
            stops[i] = x.stop
            color = current._handle_color_input(x.color)
        elif callable(x):
            easing = x
            continue
        else:
            i += 1
            color = current._handle_color_input(x)
            stops[i] = None

        # Adjust to color to space and ensure it fits
        color = color.convert(space)
        normalize_color(color, space, premultiplied)

        # Create an entry interpolating the current color and the next color
        coords.append(color[:])
        easings.append(easing if easing is not None else progress)

        # The "next" color is now the "current" color
        easing = None
        current = color

    i += 1
    if i < 2:
        raise ValueError('Need at least two colors to interpolate')

    # Calculate stops
    stops = calc_stops(stops, i)

    # Send the interpolation list along with the stop map to the Piecewise interpolator
    return InterpolateBezier(
        coords,
        [str(c) for c in current._space.get_all_channels()],
        create,
        easings,
        stops,
        space,
        out_space,
        process_mapping(progress, current._space.CHANNEL_ALIASES),
        premultiplied
    )
