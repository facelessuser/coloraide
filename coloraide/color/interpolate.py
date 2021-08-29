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
import math
from abc import ABCMeta, abstractmethod
from collections.abc import Sequence, Mapping, Callable
from collections import namedtuple
from .. import util
from ..spaces import Cylindrical, Angle


class Lerp:
    """Linear interpolation."""

    def __init__(self, progress):
        """Initialize."""

        self.progress = progress

    def __call__(self, a, b, t):
        """Interpolate with period."""

        return a + (b - a) * (t if not isinstance(self.progress, Callable) else self.progress(t))


class Piecewise(namedtuple('Piecewise', ['color', 'stop', 'progress', 'hue', 'premultiplied'])):
    """Piecewise interpolation input."""

    __slots__ = ()

    def __new__(cls, color, stop=None, progress=None, hue=util.DEF_HUE_ADJ, premultiplied=False):
        """Initialize."""

        return super().__new__(cls, color, stop, progress, hue, premultiplied)


class Interpolator(metaclass=ABCMeta):
    """Interpolator."""

    @abstractmethod
    def __init__(self):
        """Initialize."""

    @abstractmethod
    def __call__(self, p):
        """Call the interpolator."""

    @abstractmethod
    def get_delta(self):
        """Initialize."""

    def steps(self, steps=2, max_steps=1000, max_delta_e=0):
        """Steps."""

        return color_steps(self, steps, max_steps, max_delta_e)


class InterpolateSingle(Interpolator):
    """Interpolate a single range of two colors."""

    def __init__(self, channels1, channels2, names, create, progress, space, outspace, premultiplied):
        """Initialize."""

        self.names = names
        self.channels1 = channels1
        self.channels2 = channels2
        self.create = create
        self.progress = progress
        self.space = space
        self.outspace = outspace
        self.premultiplied = premultiplied

    def get_delta(self):
        """Get the delta."""

        return self.create(self.space, self.channels1).delta_e(self.create(self.space, self.channels2))

    def __call__(self, p):
        """Run through the coordinates and run the interpolation on them."""

        channels = []
        for i, c1 in enumerate(self.channels1):
            name = self.names[i]
            c2 = self.channels2[i]
            if util.is_nan(c1) and util.is_nan(c2):
                value = 0.0
            elif util.is_nan(c1):
                value = c2
            elif util.is_nan(c2):
                value = c1
            else:
                progress = None
                if isinstance(self.progress, Mapping):
                    progress = self.progress.get(name, self.progress.get('all'))
                else:
                    progress = self.progress
                lerp = progress if isinstance(progress, Lerp) else Lerp(progress)
                value = lerp(c1, c2, p)
            channels.append(value)
        color = self.create(self.space, channels[:-1], channels[-1])
        if self.premultiplied:
            postdivide(color)
        return color.convert(self.outspace, in_place=True) if self.outspace != color.space() else color


class InterpolatePiecewise(Interpolator):
    """Interpolate multiple ranges of colors."""

    def __init__(self, stops, interpolators):
        """Initialize."""

        self.start = stops[0]
        self.end = stops[len(stops) - 1]
        self.stops = stops
        self.interpolators = interpolators

    def get_delta(self):
        """Get the delta total."""

        return [i.get_delta() for i in self.interpolators]

    def __call__(self, p):
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


def calc_stops(stops, count):
    """Calculate stops."""

    # Ensure the first stop is set to zero if not explicitly set
    if 0 not in stops:
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


def postdivide(color):
    """Premultiply the given transparent color."""

    if color.alpha >= 1.0:
        return

    channels = color.coords()
    gamut = color._space.RANGE
    alpha = color.alpha
    coords = []
    for i, value in enumerate(channels):
        a = gamut[i][0]

        # Wrap the angle
        if isinstance(a, Angle):
            coords.append(value)
            continue
        coords.append(value / alpha if alpha != 0 else value)
    color._space._coords = coords


def premultiply(color):
    """Premultiply the given transparent color."""

    if color.alpha >= 1.0:
        return

    channels = color.coords()
    gamut = color._space.RANGE
    alpha = color.alpha
    coords = []
    for i, value in enumerate(channels):
        a = gamut[i][0]

        # Wrap the angle
        if isinstance(a, Angle):
            coords.append(value)
            continue
        coords.append(value * alpha)
    color._space._coords = coords


def adjust_hues(color1, color2, hue):
    """Adjust hues."""

    hue = hue.lower()
    if hue == "specified":
        return

    name = color1._space.hue_name()
    c1 = color1.get(name)
    c2 = color2.get(name)

    c1 = c1 % 360
    c2 = c2 % 360

    if util.is_nan(c1) or util.is_nan(c2):
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
        elif -180 < (c2 - c1) < 0:
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


def color_steps(interpolator, steps=2, max_steps=1000, max_delta_e=0):
    """Color steps."""

    if max_delta_e <= 0:
        actual_steps = steps
    else:
        actual_steps = 0
        deltas = interpolator.get_delta()
        if not isinstance(deltas, Sequence):
            deltas = [deltas]
        actual_steps = sum([d / max_delta_e for d in deltas])
        actual_steps = max(steps, math.ceil(actual_steps) + 1)

    if max_steps is not None:
        actual_steps = min(actual_steps, max_steps)

    ret = []
    if actual_steps == 1:
        ret = [{"p": 0.5, "color": interpolator(0.5)}]
    else:
        step = 1 / (actual_steps - 1)
        for i in range(actual_steps):
            p = i * step
            ret.append({'p': p, 'color': interpolator(p)})

    # Iterate over all the stops inserting stops in between if all colors
    # if we have any two colors with a max delta greater than what was requested.
    # We inject between every stop to ensure the midpoint does not shift.
    if max_delta_e > 0:
        # Initial check to see if we need to insert more stops
        m_delta = 0
        for i, entry in enumerate(ret):
            if i == 0:
                continue
            m_delta = max(m_delta, entry['color'].delta_e(ret[i - 1]['color']))

        while m_delta > max_delta_e:
            # Inject stops while measuring again to see if it was sufficient
            m_delta = 0
            i = 1
            while i < len(ret) and len(ret) < max_steps:
                prev = ret[i - 1]
                cur = ret[i]
                p = (cur['p'] + prev['p']) / 2
                color = interpolator(p)
                m_delta = max(m_delta, color.delta_e(prev['color']), color.delta_e(cur['color']))
                ret.insert(i, {'p': p, 'color': color})
                i += 2

    return [i['color'] for i in ret]


def color_piecewise_lerp(pw, space, out_space, progress, hue, premultiplied):
    """Piecewise Interpolation."""

    # Ensure we have something we can interpolate with
    count = len(pw)
    if count == 1:
        pw = [pw[0], pw[0]]
        count += 1

    # Calculate stops
    stops = {}
    for i, x in enumerate(pw, 0):
        if not isinstance(x, Piecewise):
            pw[i] = Piecewise(x)
        elif x.stop is not None:
            stops[i] = x.stop
    stops = calc_stops(stops, count)

    # Construct piecewise interpolation object
    color_map = []
    current = pw[0].color
    for i in range(1, count):
        p = pw[i]
        color = current._handle_color_input(p.color)

        color_map.append(
            current.interpolate(
                color,
                space=space,
                out_space=out_space,
                progress=p.progress if p.progress is not None else progress,
                hue=p.hue if p.hue is not None else hue,
                premultiplied=p.premultiplied if p.premultiplied is not None else premultiplied
            )
        )
        current = color

    return InterpolatePiecewise(stops, color_map)


def color_lerp(color1, color2, space, out_space, progress, hue, premultiplied):
    """Color interpolation."""

    # Convert to the color space and ensure the color fits inside
    color1 = color1.convert(space, fit=True)
    color2 = color1._handle_color_input(color2).convert(space, fit=True)

    # Adjust hues if we have two valid hues
    if isinstance(color1._space, Cylindrical):
        adjust_hues(color1, color2, hue)

    if premultiplied:
        premultiply(color1)
        premultiply(color2)

    channels1 = color1.coords()
    channels2 = color2.coords()

    # Include alpha
    channels1.append(color1.alpha)
    channels2.append(color2.alpha)

    return InterpolateSingle(
        names=color1._space.CHANNEL_NAMES,
        channels1=channels1,
        channels2=channels2,
        create=type(color1),
        progress=progress,
        space=space,
        outspace=out_space,
        premultiplied=premultiplied
    )


class Interpolate:
    """Interpolate between colors."""

    def mask(self, channel, *, invert=False, in_place=False):
        """Mask color channels."""

        this = self if in_place else self.clone()
        masks = set([channel] if isinstance(channel, str) else channel)
        for name in self._space.CHANNEL_NAMES:
            if (not invert and name in masks) or (invert and name not in masks):
                this.set(name, util.NaN)
        return this

    def steps(self, color, *, steps=2, max_steps=1000, max_delta_e=0, **interpolate_args):
        """
        Discrete steps.

        This is built upon the interpolate function, and will return a list of
        colors containing a minimum of colors equal to `steps` or steps as specified
        derived from the `max_delta_e` parameter (whichever is greatest).

        Number of colors can be capped with `max_steps`.

        Default delta E method used is delta E 76.
        """

        return self.interpolate(color, **interpolate_args).steps(steps, max_steps, max_delta_e)

    def mix(self, color, percent=util.DEF_MIX, *, in_place=False, **interpolate_args):
        """
        Mix colors using interpolation.

        This uses the interpolate method to find the center point between the two colors.
        The basic mixing logic is outlined in the CSS level 5 draft.
        """

        if not self._is_color(color) and not isinstance(color, (str, Piecewise)):
            raise TypeError("Unexpected type '{}'".format(type(color)))
        color = self.interpolate(color, **interpolate_args)(percent)
        return self.mutate(color) if in_place else color

    def interpolate(
        self, color, *, space="lab", out_space=None, stop=0, progress=None, hue=util.DEF_HUE_ADJ, premultiplied=False
    ):
        """
        Return an interpolation function.

        The function will return an interpolation function that accepts a value (which should
        be in the range of [0..1] and will return a color based on that value.

        While we use NaNs to mask off channels when doing the interpolation, we do not allow
        arbitrary specification of NaNs by the user, they must specify channels via `adjust`
        if they which to target specific channels for mixing. Null hues become NaNs before
        mixing occurs.
        """

        space = space.lower()
        out_space = self.space() if out_space is None else out_space.lower()

        # A piecewise object was provided, so treat it as such,
        # or we've changed the stop of the base color, so run it through piecewise.
        if (
            isinstance(color, Piecewise) or
            (stop != 0 and (isinstance(color, str) or self._is_color(color)))
        ):
            color = [color]

        if not isinstance(color, str) and isinstance(color, Sequence):
            # We have a sequence, so use piecewise interpolation
            return color_piecewise_lerp(
                [Piecewise(self, stop=stop)] + list(color),
                space,
                out_space,
                progress,
                hue,
                premultiplied
            )
        else:
            # We have a sequence, so use piecewise interpolation
            return color_lerp(
                self,
                color,
                space,
                out_space,
                progress,
                hue,
                premultiplied
            )
