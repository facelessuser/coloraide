"""
Interpolation methods.

A lot of code was ported and or adapted from the https://colorjs.io project. Particularly
the `interpolate` method and the functions built on top of it, such as `mix` and `steps`.

While we deviate in some ways, a lot of it, at the time of this comment, are a direct port.

In general, the logic mimics in many ways the `color-mix` function as outlined in the Level 5
color draft (Oct 2020), but the approach was modeled directly off of the work done in color.js.
---
Original Authors: Lea Verou, Chris Lilley
License: MIT (As noted in https://github.com/LeaVerou/color.js/blob/master/package.json)
"""
import math
from .. import util
from . _cylindrical import Cylindrical
from . _range import Angle
from collections.abc import Sequence


class InterpolateSingle:
    """Interpolate a single range of two colors."""

    def __init__(self, channels1, channels2, create, progress, outspace, premultiplied):
        """Initialize."""

        self.channels1 = channels1
        self.channels2 = channels2
        self.create = create
        self.progress = progress
        self.outspace = outspace
        self.premultiplied = premultiplied

    def interpolate(self, p):
        """Run through the coordinates and run the interpolation on them."""

        channels = []
        for i, c1 in enumerate(self.channels1):
            c2 = self.channels2[i]
            if util.is_nan(c1) and util.is_nan(c2):
                value = 0.0
            elif util.is_nan(c1):
                value = c2
            elif util.is_nan(c2):
                value = c1
            else:
                value = c1 + (c2 - c1) * (p if self.progress is None else self.progress(p))
            channels.append(value)
        color = self.create.new(channels[:-1], channels[-1])
        if self.premultiplied:
            postdivide(color)
        return color.convert(self.outspace) if self.outspace != color.space() else color


class InterpolateMulti:
    """Interpolate multiple ranges of colors."""

    def __init__(self, interpolators, progress):
        """Initialize."""

        self.interpolators = interpolators
        self.progress = progress

    def interpolate(self, p):
        """Interpolate."""

        p = (p if self.progress is None else self.progress(p))
        percent = p * 100

        if percent > 100:
            # Beyond range, just interpolate the last colors
            return self.interpolators[-1][1].interpolate(1 + p / len(self.interpolators))

        elif percent < 0:
            # Beyond range, just interpolate the last colors
            return self.interpolators[0][1].interpolate(0 + p / len(self.interpolators))

        else:
            last = 0
            for stop, interpolator in self.interpolators:
                if percent <= stop:
                    r = stop - last
                    p2 = (percent - last) / r if r else 1
                    return interpolator.interpolate(p2)
                last = stop


def postdivide(color):
    """Premultiply the given transparent color."""

    if color.alpha >= 1.0:
        return

    channels = color.coords()
    gamut = color._range
    alpha = color.alpha
    coords = []
    for i, value in enumerate(channels):
        a = gamut[i][0]

        # Wrap the angle
        if isinstance(a, Angle):
            coords.append(value)
            continue
        coords.append(value / alpha if alpha != 0 else value)
    color._coords = coords


def premultiply(color):
    """Premultiply the given transparent color."""

    if color.alpha >= 1.0:
        return

    channels = color.coords()
    gamut = color._range
    alpha = color.alpha
    coords = []
    for i, value in enumerate(channels):
        a = gamut[i][0]

        # Wrap the angle
        if isinstance(a, Angle):
            coords.append(value)
            continue
        coords.append(value * alpha)
    color._coords = coords


def adjust_hues(color1, color2, hue):
    """Adjust hues."""

    hue = hue.lower()
    if hue == "specified":
        return

    name = color1.hue_name()
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


class Interpolate:
    """Interpolate between colors."""

    def steps(self, color, *, steps=2, max_steps=1000, max_delta_e=0, **interpolate_args):
        """
        Discrete steps.

        This is built upon the interpolate function, and will return a list of
        colors containing a minimum of colors equal to `steps` or steps as specified
        derived from the `max_delta_e` parameter (whichever is greatest).

        Number of colors can be capped with `max_steps`.

        Default delta E method used is delta E 76.
        """

        interpolator = self.interpolate(color, **interpolate_args)

        if not isinstance(color, Sequence) and max_delta_e > 0:
            color = [self, color]

        if max_delta_e <= 0:
            actual_steps = steps
        else:
            actual_steps = 0
            current = self
            for c in color:
                total_delta = current.delta_e(c)
                actual_steps += total_delta / max_delta_e
                current = c
            actual_steps = max(steps, math.ceil(actual_steps) + 1)

        if max_steps is not None:
            actual_steps = min(actual_steps, max_steps)

        ret = []
        if actual_steps == 1:
            ret = [{"p": 0.5, "color": interpolator.interpolate(0.5)}]
        else:
            step = 1 / (actual_steps - 1)
            for i in range(actual_steps):
                p = i * step
                ret.append({'p': p, 'color': interpolator.interpolate(p)})

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
                    color = interpolator.interpolate(p)
                    m_delta = max(m_delta, color.delta_e(prev['color']), color.delta_e(cur['color']))
                    ret.insert(i, {'p': p, 'color': color})
                    i += 2

        return [i['color'] for i in ret]

    def mix(self, color, percent=util.DEF_MIX, **interpolate_args):
        """
        Mix colors using interpolation.

        This uses the interpolate method to find the center point between the two colors.
        The basic mixing logic is outlined in the CSS level 5 draft.
        """

        return self.interpolate(color, **interpolate_args).interpolate(percent)

    def average(self, colors, weights=None, *, space='lab', out_space=True, hue=util.DEF_HUE_ADJ, sort_hue=False):
        """Mix multiple colors returning an average of all the colors."""

        space = space.lower()
        outspace = self.space() if out_space is None else out_space.lower()

        if not isinstance(colors, Sequence):
            colors = [colors]

        if len(colors) == 0:
            return self.convert(outspace)

        if weights is None:
            weights = [1] * (len(colors) + 1)
        elif len(weights) != len(colors) + 1:
            raise ValueError(
                '{:d} weights were given, but there are {:d} colors to average'.format(len(weights), len(colors) + 1)
            )

        # Normalize weights
        avg = len(weights) / sum(weights)
        weights = [w * avg for w in weights]
        colors = [c.convert(space, fit=True) for c in [self] + colors]

        # Sort cylindrical colors by hue
        if sort_hue and isinstance(colors[0], Cylindrical):
            indicies, colors = zip(
                *sorted(
                    enumerate(colors),
                    key=lambda value: value[1].hue if not value[1].is_nan('hue') else -1
                )
            )
            weights = [weights[x] for x in indicies]

        # Get the average alpha
        alpha = 0
        opaque = True
        for i, color in enumerate(colors, 0):
            a = util.no_nan(color.alpha)
            if a != 1:
                opaque = False
            alpha += a * weights[i]
        alpha = alpha / len(weights) if not opaque else 1

        # Interpolate between the color channels, ignore alpha as we calculate it separately.
        # Don't modify `NaN`.
        percent = 1
        current = colors[0]
        for i, color in enumerate(colors, 0):
            k = weights[i]
            color.update([x * k for x in color.coords()], 1)
            if i == 0:
                continue
            percent *= (i / (i + 1))
            current = current.mix(
                color,
                percent,
                space=space,
                hue=hue
            )

        current.alpha = alpha
        return current.convert(outspace)

    def interpolate(
        self, color, *, space="lab", out_space=None, progress=None, hue=util.DEF_HUE_ADJ,
        premultiplied=False
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

        if progress is not None and not callable(progress):
            raise TypeError('Progress must be callable')

        inspace = space.lower()
        outspace = self.space() if out_space is None else out_space.lower()

        # Handle multiple colors
        if isinstance(color, Sequence):
            if len(color) == 0:
                color = [self]
            count = len(color)
            stops = 100 / count
            color_map = []
            start = 0
            current = self
            for c in color:
                stop = start + stops
                color_map.append(
                    [
                        stop,
                        current.interpolate(c, space=inspace, out_space=outspace, hue=hue, premultiplied=premultiplied)
                    ]
                )
                current = c
                start = stop

            return InterpolateMulti(color_map, progress)
        else:
            # Convert to the color space and ensure the color fits inside
            color1 = self.convert(inspace, fit=True)
            color2 = color.convert(inspace, fit=True)

            # Adjust hues if we have two valid hues
            if isinstance(color1, Cylindrical):
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
                channels1=channels1,
                channels2=channels2,
                create=color1,
                progress=progress,
                outspace=outspace,
                premultiplied=premultiplied
            )
