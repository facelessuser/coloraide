"""Piecewise linear interpolation."""
from .. import algebra as alg
from ..spaces import Cylindrical
from ..types import Vector, ColorInput
from typing import Optional, Callable, Sequence, Mapping, Type, Dict, List, Union, cast, Tuple, Any, TYPE_CHECKING
from .common import stop, Interpolator, calc_stops, process_mapping, premultiply, postdivide

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def adjust_hues(color1: 'Color', color2: 'Color', hue: str) -> None:
    """Adjust hues."""

    if hue == "specified":
        return

    name = cast(Cylindrical, color1._space).hue_name()
    c1 = color1.get(name)
    c2 = color2.get(name)

    c1 = c1 % 360
    c2 = c2 % 360

    if alg.is_nan(c1) or alg.is_nan(c2):
        color1.set(name, c1)
        color2.set(name, c2)
        return

    if hue == "shorter":
        if c2 - c1 > 180:
            c1 += 360
        elif c2 - c1 < -180:
            c2 += 360

    elif hue == "longer":
        if 0 < (c2 - c1) < 180:
            c1 += 360
        elif -180 < (c2 - c1) <= 0:
            c2 += 360

    elif hue == "increasing":
        if c2 < c1:
            c2 += 360

    elif hue == "decreasing":
        if c1 < c2:
            c1 += 360

    else:
        raise ValueError("Unknown hue adjuster '{}'".format(hue))

    color1.set(name, c1)
    color2.set(name, c2)


class InterpolatePiecewise(Interpolator):
    """Interpolate multiple ranges of colors."""

    def __init__(
        self,
        color_map: List[Tuple[Vector, Vector]],
        names: Sequence[str],
        create: Type['Color'],
        easings: List[Optional[Callable[..., float]]],
        stops: Dict[int, float],
        space: str,
        out_space: str,
        progress: Optional[Union[Callable[..., float], Mapping[str, Callable[..., float]]]],
        premultiplied: bool
    ):
        """Initialize."""

        self.start = stops[0]
        self.end = stops[len(stops) - 1]
        self.stops = stops
        self.color_map = color_map
        self.names = names
        self.create = create
        self.easings = easings
        self.space = space
        self.out_space = out_space
        self.progress = progress
        self.premultiplied = premultiplied

    def interpolate(
        self,
        colors: Tuple[Vector, Vector],
        easing: Optional[Union[Callable[..., float], Mapping[str, Callable[..., float]]]],
        p: float
    ) -> 'Color':
        """Interpolate."""

        channels = []
        for i, values in enumerate(zip(*colors)):
            c1, c2 = values
            name = self.names[i]
            if alg.is_nan(c1) and alg.is_nan(c2):
                value = alg.NaN
            elif alg.is_nan(c1):
                value = c2
            elif alg.is_nan(c2):
                value = c1
            else:
                progress = None
                if isinstance(easing, Mapping):
                    progress = easing.get(name)
                    if progress is None:
                        progress = easing.get('all')
                else:
                    progress = easing
                t = alg.clamp(progress(p), 0.0, 1.0) if progress is not None else p
                value = alg.lerp(c1, c2, t)
            channels.append(value)
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
        for i, colors in enumerate(self.color_map, 1):
            s = self.stops[i]
            if percent <= s:
                r = s - last
                p2 = (percent - last) / r if r else 1
                easing = self.easings[i - 1]  # type: Any
                if easing is None:
                    easing = self.progress
                return self.interpolate(colors, easing, p2)
            last = s

        # We shouldn't ever hit this, but provided for typing.
        # If we do hit this, it would be a bug.
        raise RuntimeError('Iterpolation could not be found for {}'.format(percent))  # pragma: no cover


def normalize_color(color: 'Color', space: str, premultiplied: bool) -> None:
    """Normalize the color."""

    # Adjust to color to space and ensure it fits
    if not color.CS_MAP[space].EXTENDED_RANGE:
        if not color.in_gamut():
            color.fit()

    # Premultiply
    if premultiplied:
        premultiply(color)


def color_piecewise_lerp(
    create: Type['Color'],
    colors: List[Union[ColorInput, stop, Callable[..., float]]],
    space: str,
    out_space: str,
    progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
    hue: str,
    premultiplied: bool,
    **kwargs: Any
) -> InterpolatePiecewise:
    """Piecewise Interpolation."""

    # Construct piecewise interpolation object
    stops = {}  # type: Any
    color_map = []

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

        # Adjust hues if we have two valid hues
        color2 = color.clone()
        if isinstance(current._space, Cylindrical):
            adjust_hues(current, color2, hue)

        # Create an entry interpolating the current color and the next color
        color_map.append((current[:], color2[:]))
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
    return InterpolatePiecewise(
        color_map,
        current._space.channels,
        create,
        easings,
        stops,
        space,
        out_space,
        process_mapping(progress, current._space.CHANNEL_ALIASES),
        premultiplied
    )
