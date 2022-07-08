"""
Interpolation methods.

Originally, the base code for `interpolate`, `mix` and `steps` was ported from the
https://colorjs.io project. Since that time, there has been significant modifications
that add additional features etc. The base logic though is attributed to the original
authors.

In general, the logic mimics in many ways the `color-mix` function as outlined in the Level 5
color draft (Oct 2020), but the initial approach was modeled directly off of the work done in
color.js.
---
Original Authors: Lea Verou, Chris Lilley
License: MIT (As noted in https://github.com/LeaVerou/color.js/blob/master/package.json)
"""
from abc import ABCMeta, abstractmethod
from collections import namedtuple
from . import algebra as alg
from .types import Vector
from .spaces import Cylindrical
from .channels import FLG_ANGLE
from typing import Optional, Callable, Sequence, Mapping, Type, Dict, List, Union, cast, TYPE_CHECKING
from .types import ColorInput

if TYPE_CHECKING:  # pragma: no cover
    from .color import Color


class Lerp:
    """Linear interpolation."""

    def __init__(self, progress: Optional[Callable[..., float]]) -> None:
        """Initialize."""

        self.progress = progress

    def __call__(self, a: float, b: float, t: float) -> float:
        """Interpolate with period."""

        return alg.lerp(a, b, t if self.progress is None else self.progress(t))


class Piecewise(namedtuple('Piecewise', ['color', 'stop', 'progress', 'hue', 'premultiplied'])):
    """Piecewise interpolation input."""

    __slots__ = ()

    def __new__(
        cls,
        color: ColorInput,
        stop: Optional[float] = None,
        progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]] = None,
        hue: Optional[str] = None,
        premultiplied: Optional[bool] = None
    ) -> 'Piecewise':
        """Initialize."""

        return super().__new__(cls, color, stop, progress, hue, premultiplied)


class Interpolator(metaclass=ABCMeta):
    """Interpolator."""

    @abstractmethod
    def __init__(self) -> None:
        """Initialize."""

    @abstractmethod
    def __call__(self, p: float) -> 'Color':
        """Call the interpolator."""

    def steps(
        self,
        steps: int = 2,
        max_steps: int = 1000,
        max_delta_e: float = 0,
        delta_e: Optional[str] = None
    ) -> List['Color']:
        """Steps."""

        return color_steps(self, steps, max_steps, max_delta_e, delta_e)


class InterpolateSingle(Interpolator):
    """Interpolate a single range of two colors."""

    def __init__(
        self,
        channels1: Vector,
        channels2: Vector,
        names: Sequence[str],
        create: Type['Color'],
        progress: Optional[Union[Callable[..., float], Mapping[str, Callable[..., float]]]],
        space: str,
        outspace: str,
        premultiplied: bool
    ) -> None:
        """Initialize."""

        self.names = names
        self.channels1 = channels1
        self.channels2 = channels2
        self.create = create
        self.progress = progress
        self.space = space
        self.outspace = outspace
        self.premultiplied = premultiplied

    def __call__(self, p: float) -> 'Color':
        """Run through the coordinates and run the interpolation on them."""

        channels = []
        for i, c1 in enumerate(self.channels1):
            name = self.names[i]
            c2 = self.channels2[i]
            if alg.is_nan(c1) and alg.is_nan(c2):
                value = alg.NaN
            elif alg.is_nan(c1):
                value = c2
            elif alg.is_nan(c2):
                value = c1
            else:
                progress = None
                if isinstance(self.progress, Mapping):
                    progress = self.progress.get(name)
                    if progress is None:
                        progress = self.progress.get('all')
                else:
                    progress = self.progress
                lerper = progress if isinstance(progress, Lerp) else Lerp(progress)
                value = lerper(c1, c2, p)
            channels.append(value)
        color = self.create(self.space, channels[:-1], channels[-1])
        if self.premultiplied:
            postdivide(color)
        return color.convert(self.outspace, in_place=True) if self.outspace != color.space() else color


class InterpolatePiecewise(Interpolator):
    """Interpolate multiple ranges of colors."""

    def __init__(self, stops: Dict[int, float], interpolators: List[InterpolateSingle]):
        """Initialize."""

        self.start = stops[0]
        self.end = stops[len(stops) - 1]
        self.stops = stops
        self.interpolators = interpolators

    def __call__(self, p: float) -> 'Color':
        """Interpolate."""

        percent = p
        if percent > self.end:
            # Beyond range, just interpolate the last colors
            return self.interpolators[-1](1 + abs(p - self.end) if p > 1 else 1)

        elif percent < self.start:
            # Beyond range, just interpolate the last colors
            return self.interpolators[0](0 - abs(self.start - p) if p < 0 else 0)

        else:
            last = self.start
            for i, interpolator in enumerate(self.interpolators, 1):
                stop = self.stops[i]
                if percent <= stop:
                    r = stop - last
                    p2 = (percent - last) / r if r else 1
                    return interpolator(p2)
                last = stop

            # We shouldn't ever hit this, but provided for typing.
            # If we do hit this, it would be a bug.
            raise RuntimeError('Iterpolation could not be found for {}'.format(percent))  # pragma: no cover


def calc_stops(stops: Dict[int, float], count: int) -> Dict[int, float]:
    """Calculate stops."""

    if 0 not in stops or stops[0] is None:
        stops[0] = 0

    last = stops[0] * 100
    highest = last
    empty = None
    final = {}

    # Build up normalized stops
    for i in range(count):
        value = stops.get(i)
        if value is not None:
            value *= 100

        # Found an empty hole, track the start
        if value is None and empty is None:
            empty = i - 1
            continue
        elif value is None:
            continue

        # We can't have a stop decrease in progression
        if value < last:
            value = last

        # Track the largest explicit value set
        if value > highest:
            highest = value

        # Fill in hole if one exists.
        # Holes will be evenly space between the
        # current and last stop.
        if empty is not None:
            r = i - empty
            increment = (value - last) / r
            for j in range(empty + 1, i):
                last += increment
                final[j] = last / 100
            empty = None

        # Set the stop and track it as the last
        last = value
        final[i] = last / 100

    # If there is a hole at the end, fill in the hole,
    # equally spacing the stops from the last to 100%.
    # If the last is greater than 100%, then all will
    # be equal to the last.
    if empty is not None:
        r = (count - 1) - empty
        if highest > 100:
            increment = 0
        else:
            increment = (100 - last) / r
        for j in range(empty + 1, count):
            last += increment
            final[j] = last / 100

    return final


def process_mapping(
    progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
    aliases: Mapping[str, str]
) -> Optional[Union[Callable[..., float], Mapping[str, Callable[..., float]]]]:
    """Process a mapping, such that it is not using aliases."""

    if not isinstance(progress, Mapping):
        return progress
    return {aliases.get(k, k): v for k, v in progress.items()}


def postdivide(color: 'Color') -> None:
    """Premultiply the given transparent color."""

    alpha = color[-1]

    if alg.is_nan(alpha) or alpha in (0.0, 1.0):
        return

    channels = color._space.CHANNELS
    for i, value in enumerate(color[:-1]):

        # Wrap the angle
        if channels[i].flags & FLG_ANGLE:
            continue
        color[i] = value / alpha


def premultiply(color: 'Color') -> None:
    """Premultiply the given transparent color."""

    alpha = color[-1]

    if alg.is_nan(alpha) or alpha == 1.0:
        return

    channels = color._space.CHANNELS
    for i, value in enumerate(color[:-1]):

        # Wrap the angle
        if channels[i].flags & FLG_ANGLE:
            continue
        color[i] = value * alpha


def adjust_hues(color1: 'Color', color2: 'Color', hue: str) -> None:
    """Adjust hues."""

    if hue == "specified":
        return

    name = cast(Type[Cylindrical], color1._space).hue_name()
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


def color_steps(
    interpolator: Interpolator,
    steps: int = 2,
    max_steps: int = 1000,
    max_delta_e: float = 0,
    delta_e: Optional[str] = None
) -> List['Color']:
    """Color steps."""

    actual_steps = steps

    # Allocate at least two steps if we are doing a maximum delta E,
    if max_delta_e != 0 and actual_steps < 2:
        actual_steps = 2

    # Make sure we don't start out allocating too many colors
    if max_steps is not None:
        actual_steps = min(actual_steps, max_steps)

    ret = []
    if actual_steps == 1:
        ret = [{"p": 0.5, "color": interpolator(0.5)}]
    elif actual_steps > 1:
        step = 1 / (actual_steps - 1)
        for i in range(actual_steps):
            p = i * step
            ret.append({'p': p, 'color': interpolator(p)})

    # Iterate over all the stops inserting stops in between all colors
    # if we have any two colors with a max delta greater than what was requested.
    # We inject between every stop to ensure the midpoint does not shift.
    if max_delta_e > 0:
        # Initial check to see if we need to insert more stops
        m_delta = 0.0
        for i in range(1, len(ret)):
            m_delta = max(
                m_delta,
                cast('Color', ret[i - 1]['color']).delta_e(
                    cast('Color', ret[i]['color']),
                    method=delta_e
                )
            )

        # If we currently have delta over our limit inject more stops.
        # If inserting between every color would push us over the max_steps, halt.
        while m_delta > max_delta_e and (len(ret) * 2 - 1 <= max_steps):
            # Inject stops while measuring again to see if it was sufficient
            m_delta = 0.0
            i = 1
            offset = 0
            for i in range(1, len(ret)):
                index = i + offset
                prev = ret[index - 1]
                cur = ret[index]
                p = (cast(float, cur['p']) + cast(float, prev['p'])) / 2
                color = interpolator(p)
                m_delta = max(
                    m_delta,
                    color.delta_e(cast('Color', prev['color']), method=delta_e),
                    color.delta_e(cast('Color', cur['color']), method=delta_e)
                )
                ret.insert(index, {'p': p, 'color': color})
                offset += 1

    return [cast('Color', i['color']) for i in ret]


def color_piecewise_lerp(
    pw: List[Piecewise],
    space: str,
    out_space: str,
    progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
    hue: str,
    premultiplied: bool
) -> InterpolatePiecewise:
    """Piecewise Interpolation."""



    # Construct piecewise interpolation object
    count = len(pw)
    stops = {}
    color_map = []
    current = cast('Color', pw[0].color)
    stops[0] = pw[0].stop

    for i in range(1, len(pw)):

        # Normalize all colors as Piecewise objects
        p = pw[i]
        stops[i] = p.stop

        # Ensure input provided via Piecewise object is a Color object
        color = current._handle_color_input(p.color)

        # Create an entry interpolating the current color and the next color
        color_map.append(
            color_lerp(
                current,
                color,
                space,
                out_space,
                p.progress if p.progress is not None else progress,
                p.hue if p.hue is not None else hue,
                p.premultiplied if p.premultiplied is not None else premultiplied
            )
        )

        # The "next" color is now the "current" color
        current = color

    # Calculate stops
    stops = calc_stops(stops, count)

    # Send the interpolation list along with the stop map to the Piecewise interpolator
    return InterpolatePiecewise(stops, color_map)


def color_lerp(
    color1: 'Color',
    color2: ColorInput,
    space: str,
    out_space: str,
    progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
    hue: str,
    premultiplied: bool
) -> InterpolateSingle:
    """Color interpolation."""

    # Convert to the color space and ensure the color fits inside
    color1 = color1.convert(space)
    color2 = color1._handle_color_input(color2).convert(space)
    if not color1.CS_MAP[space].EXTENDED_RANGE:
        if not color1.in_gamut():
            color1.fit()
        if not color2.in_gamut():
            color2.fit()

    # Adjust hues if we have two valid hues
    if issubclass(color1._space, Cylindrical):
        adjust_hues(color1, color2, hue)

    if premultiplied:
        premultiply(color1)
        premultiply(color2)

    channels1 = color1[:-1]
    channels2 = color2[:-1]

    # Include alpha
    channels1.append(color1[-1])
    channels2.append(color2[-1])

    return InterpolateSingle(
        channels1=channels1,
        channels2=channels2,
        names=color1._space.CHANNELS + ('alpha',),
        create=type(color1),
        progress=process_mapping(progress, color1._space.CHANNEL_ALIASES),
        space=space,
        outspace=out_space,
        premultiplied=premultiplied
    )
