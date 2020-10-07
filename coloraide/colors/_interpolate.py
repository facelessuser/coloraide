"""Interpolation methods."""
import math
import functools
from .. import util
from . _gamut import GamutAngle


def overlay(c1, c2, a1, a2):
    """Overlay one color channel over the other."""

    if math.isnan(c1) and math.isnan(c2):
        return 0.0
    elif math.isnan(c1):
        return c1 * a1
    elif math.isnan(c2):
        return c2 * a2

    return c1 * a1 + c2 * a2 * (1 - a1)


def _interpolate(p, progress, c1, c2):
    """Handle the actual interpolation."""

    if math.isnan(c1) and math.isnan(c2):
        return 0.0
    elif math.isnan(c1):
        return c2
    elif math.isnan(c2):
        return c1
    else:
        return c1 + (c2 - c1) * p if progress is None else progress(p)


def interpolate(p, coords1, coords2, create, progress, inspace, outspace):
    """Run through the coordinates and run the interpolation on them."""

    return create.new([_interpolate(p, progress, c1, coords2[i]) for i, c1 in enumerate(coords1)]).convert(outspace)


def process_coords(color):
    """Format the coordinates."""

    hue_index = None
    coords = color.coords()
    for i, gamut in enumerate(color._gamut):
        if isinstance(gamut[0], GamutAngle):
            hue_index = i
            if color.is_achromatic():
                # Achromatic colors should not consider hue
                coords[i] = float("NaN")
    return coords, hue_index


def adjust_hues(c1, c2, hue):
    """Adjust hues."""

    hue = hue.lower()
    if hue != "specified":
        c1 = c1 % 360
        c2 = c2 % 360

    if math.isnan(c1) or math.isnan(c2):
        return c1, c2

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

    elif hue == "specified":
        pass

    else:
        raise ValueError("Unknown hue adjuster '{}'".format(hue))
    return c1, c2


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

            this = self.convert(space)
            background = background.convert(space)

            if this is None:
                raise ValueError('Invalid colorspace value: {}'.format(space))

            # Get the coordinates and indexes of valid hues
            coords1, hue_index1 = process_coords(this)
            coords2, hue_index2 = process_coords(background)

            # Adjust hues if we have two valid hues
            if hue_index1 is not None and hue_index2 is not None:
                hue1, hue2 = adjust_hues(coords1[hue_index1], coords2[hue_index2], util.DEF_HUE_ADJ)
                coords1[hue_index1] = hue1
                coords2[hue_index2] = hue2

            # Blend the channels using the alpha channel values as the factors
            # Afterwards, blend the alpha channels. This is different than blend.
            this._coords = [overlay(c1, coords2[i], this.alpha, background.alpha) for i, c1 in enumerate(coords1)]
            this.alpha = this.alpha + background.alpha * (1.0 - this.alpha)
        else:
            this = self

        if in_place:
            return self.update(this.convert(current_space))

        return this.convert(current_space)

    def mix(self, color, percent=util.DEF_MIX, *, alpha=True, space=None, hue=util.DEF_HUE_ADJ, in_place=False):
        """Mix colors using interpolation."""

        current_space = self.space()
        if space is None:
            space = self.space()
        else:
            space = space.lower()

        obj = self.interpolate(color, space=space, out_space=current_space, alpha=alpha, hue=hue)(percent)
        if in_place:
            return self.update(obj)
        return obj

    def interpolate(self, color, space="lab", *, out_space=None, progress=None, alpha=True, hue=util.DEF_HUE_ADJ):
        """Return an interpolation function."""

        if progress is not None and not callable(progress):
            raise TypeError('Progress must be callable')

        inspace = space.lower()
        outspace = self.space()

        # Convert to the color space and ensure the color fits inside
        color1 = self.convert(inspace, fit=True)
        color2 = color.convert(inspace, fit=True)

        # Get the coordinates and indexes of valid hues
        coords1, hue_index1 = process_coords(color1)
        coords2, hue_index2 = process_coords(color2)

        # Adjust hues if we have two valid hues
        if hue_index1 is not None and hue_index2 is not None:
            hue1, hue2 = adjust_hues(coords1[hue_index1], coords2[hue_index2], hue)
            coords1[hue_index1] = hue1
            coords2[hue_index2] = hue2

        # Include alpha
        coords1.append(color1.alpha)
        # If we don't want to mix alpha, use NaN for the second alpha
        coords2.append(color2.alpha if alpha else float('NaN'))

        return functools.partial(
            interpolate,
            coords1=coords1,
            coords2=coords2,
            create=color1,
            progress=progress,
            inspace=space,
            outspace=outspace
        )
