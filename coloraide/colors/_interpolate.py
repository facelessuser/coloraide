"""Interpolation methods."""
import math
import functools
from .. import util
from . _cylindrical import Cylindrical


def overlay(c1, c2, a1, a2):
    """Overlay one color channel over the other."""

    if math.isnan(c1) and math.isnan(c2):
        return 0.0
    elif math.isnan(c1):
        return c2 * a2
    elif math.isnan(c2):
        return c1 * c1

    return c1 * a1 + c2 * a2 * (1 - a1)


def interpolate(p, coords1, coords2, create, progress, outspace):
    """Run through the coordinates and run the interpolation on them."""

    coords = []
    for i, c1 in enumerate(coords1):
        c2 = coords2[i]
        if math.isnan(c1) and math.isnan(c2):
            value = 0.0
        elif math.isnan(c1):
            value = c2
        elif math.isnan(c2):
            value = c1
        else:
            value = c1 + (c2 - c1) * (p if progress is None else progress(p))
        coords.append(value)
    return create.new(coords).convert(outspace)


def prepare_coords(color, adjust=None):
    """
    Prepare the coordinates for interpolation.

    If the hue is null, we need to set it to NaN.
    If the user specified only specific channels to mix,
    then we need to set all other channels to NaN.
    """

    if isinstance(color, Cylindrical):
        if color.is_hue_null():
            name = color.hue_name()
            color.set(name, util.NAN)

    if adjust:
        to_adjust = adjust & color.CHANNEL_NAMES
        to_avoid = color.CHANNEL_NAMES - adjust
        if to_adjust:
            for channel in to_avoid:
                color.set(channel, util.NAN)


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

    if math.isnan(c1) or math.isnan(c2):
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
    """Interpolate."""

    def overlay(self, background, *, space=None, in_place=False):
        """
        Apply the given transparency with the given background.

        This gives a color that represents what the eye sees with
        the transparent color against the given background.
        """

        current_space = self.space()
        if self.alpha < 1.0:
            if space is None:
                space = current_space
            else:
                space = space.lower()

            this = self.convert(space, fit=True)
            background = background.convert(space, fit=True)

            if this is None:
                raise ValueError('Invalid colorspace value: {}'.format(space))

            # Get the coordinates and indexes of valid hues
            prepare_coords(this)
            prepare_coords(background)

            # Adjust hues if we have two valid hues
            if isinstance(this, Cylindrical):
                adjust_hues(this, background, util.DEF_HUE_ADJ)

            # Blend the channels using the alpha channel values as the factors
            # Afterwards, blend the alpha channels. This is different than blend.
            coords1 = this.coords()
            coords2 = background.coords()
            a1 = this.alpha
            a2 = background.alpha
            this._coords = [overlay(c1, coords2[i], a1, a2) for i, c1 in enumerate(coords1)]
            this.alpha = a1 + a2 * (1.0 - a1)
        else:
            this = self

        if in_place:
            return self.update(this.convert(current_space))

        return this.convert(current_space)

    def mix(self, color, percent=util.DEF_MIX, *, space=None, adjust=None, hue=util.DEF_HUE_ADJ, in_place=False):
        """Mix colors using interpolation."""

        current_space = self.space()
        if space is None:
            space = self.space()
        else:
            space = space.lower()

        obj = self.interpolate(color, space=space, out_space=current_space, adjust=adjust, hue=hue)(percent)
        if in_place:
            return self.update(obj)
        return obj

    def interpolate(self, color, *, space="lab", out_space=None, progress=None, adjust=None, hue=util.DEF_HUE_ADJ):
        """
        Return an interpolation function.

        The general interpolation comes from the CSS specification which covers:

        - the math involved to mix color coordinates.
        - explaining that the colors should be gamut mapped
        - how percentages are handled
        - how the hue adjuster works

        With that said the API is similar to https://colorjs.io. The idea of gamut mapping by
        compressing chroma is not unique to color.js, but we did port their work for that to
        be used here as well.

        The function will return an interpolation function that accepts a value (which should
        be in the range of [0..1] and we will return a color based on that value.

        While we use NaNs to mask off channels when doing the interpolation, we do not allow
        arbitrary specification of NaNs by the user, they must specify channels via `adjust`
        if they which to target specific channels for mixing. Null hues become NaNs before
        mixing occurs.

        ---
        Original Authors: Lea Verou, Chris Lilley
        License: MIT (As noted in https://github.com/LeaVerou/color.js/blob/master/package.json)
        """

        if progress is not None and not callable(progress):
            raise TypeError('Progress must be callable')

        if adjust:
            adjust = set([name.lower() for name in adjust])

        inspace = space.lower()
        outspace = self.space()

        # Convert to the color space and ensure the color fits inside
        color1 = self.convert(inspace, fit=True)
        color2 = color.convert(inspace, fit=True)

        # Get the coordinates and indexes of valid hues
        prepare_coords(color1)
        prepare_coords(color2, adjust)

        # Adjust hues if we have two valid hues
        if isinstance(color1, Cylindrical):
            adjust_hues(color1, color2, hue)

        coords1 = color1.coords()
        coords2 = color2.coords()

        # Include alpha
        coords1.append(color1.alpha)
        coords2.append(color2.alpha)

        return functools.partial(
            interpolate,
            coords1=coords1,
            coords2=coords2,
            create=color1,
            progress=progress,
            outspace=outspace
        )
