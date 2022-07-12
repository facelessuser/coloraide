"""Common tools."""
import math
import functools
from abc import ABCMeta, abstractmethod
from .. import algebra as alg
from ..channels import FLG_ANGLE
from ..types import ColorInput
from typing import Optional, Callable, Mapping, Dict, List, Union, cast, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color


def midpoint(t: float, h: float = 0.5) -> float:
    """Midpoint easing function."""

    return 0.0 if h <= 0 or h >= 1 else math.pow(t, math.log(0.5) / math.log(h))


def hint(mid: float) -> Callable[..., float]:
    """A generate a midpoint easing function."""

    return functools.partial(midpoint, h=mid)


class stop:
    """Color stop."""

    __slots__ = ('color', 'stop')

    def __init__(self, color: ColorInput, value: float) -> None:
        """Color stops."""

        self.color = color
        self.stop = value


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


def calc_stops(stops: Dict[int, float], count: int) -> Dict[int, float]:
    """Calculate stops."""

    # Ensure the first stop is set to zero if not explicitly set
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
        total = len(ret)
        while m_delta > max_delta_e and (total * 2 - 1 <= max_steps):
            # Inject stops while measuring again to see if it was sufficient
            m_delta = 0.0
            i = 1
            index = 1
            while index < total:
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
                total += 1
                index += 2

    return [cast('Color', i['color']) for i in ret]
