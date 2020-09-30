"""Color mixing."""
from .. import util
import math


class Mix:
    """Color utilities."""

    def _mix_channel(self, c1, c2, f1, f2=1.0):
        """
        Blend the channel.

        `f1` is the blend percent.
        When simulating transparency, `f1` can be looked at as the foreground alpha,
        while `f2` would be the background `alpha`. Usually we `f2` is always `1.0`
        as we normally overlay a transparent color on an opaque one.
        """

        return abs(c2 * f1 + c1 * f2 * (1 - f1))

    def _hue_mix_channel(self, c1, c2, f1, f2=1.0, *, hue=util.DEF_HUE_ADJ):
        """Blend the hue channel."""

        if math.isnan(c1) and math.isnan(c2):
            return 0.0
        elif math.isnan(c1):
            return c2
        elif math.isnan(c2):
            return c1

        hue = hue.lower()
        if hue != "specified":
            c1 = c1 % 360
            c2 = c2 % 360

        if hue == "shorter":
            if c2 - c1 > 180:
                c1 += 360
            elif c2 - c1 < -180:
                c2 += 360

        elif hue == "longer":
            if 0 < (c1 - c1) < 180:
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

        value = self._mix_channel(c1, c2, f1, f2)

        # Normalize the result
        if not (0.0 <= value <= 360.0):
            value = value % 360.0

        return value

    def alpha_composite(self, background, *, space=None, in_place=False):
        """
        Apply the given transparency with the given background.

        This gives a color that represents what the eye sees with
        the transparent color against the given background.
        """

        current_space = self.space()
        if self._alpha < 1.0:
            if space is None:
                space = current_space
            else:
                space = space.lower()

            this = self.convert(space)
            if background.space() != background:
                background = background.convert(space)

            if this is None:
                raise ValueError('Invalid colorspace value: {}'.format(space))

            # Blend the channels using the alpha channel values as the factors
            # Afterwards, blend the alpha channels. This is different than blend.

            # We reverse our mix to give an intuitive interface:
            #    when given `color1.mix(color2, percent))`, `percent` will apply to `color2`
            #    opposed to `color1`
            # Because of this, we need to feed our colors in reverse order.
            # We are mixing our color into the background at the percentage of our our alpha.
            this._coords = [c for c in this._mix(background.coords(), this.coords(), this._alpha, background._alpha)]
            this._alpha = this._alpha + background._alpha * (1.0 - this._alpha)
        else:
            this = self

        if in_place:
            return self.update(this.convert(current_space))

        return this.convert(current_space)

    def mix(self, color, percent=util.DEF_MIX, *, alpha=True, space=None, hue=util.DEF_HUE_ADJ, in_place=False):
        """Blend color."""

        current_space = self.space()
        if space is None:
            space = current_space
        else:
            space = space.lower()

        this = self.convert(space)
        if color.space() != space:
            color = color.convert(space)

        if this is None:
            raise ValueError('Invalid colorspace value: {}'.format(space))

        this._coords = [c for c in this._mix(this.coords(), color.coords(), factor, hue=hue)]
        if alpha:
            # This is a simple channel blend and not alpha compositing.
            this._alpha = this._mix_channel(this._alpha, color._alpha, factor)

        if in_place:
            return self.update(this.convert(current_space))

        return this.convert(current_space)
