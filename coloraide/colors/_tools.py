"""Color tools."""
from ._gamut import Gamut, GamutBound, GamutUnbound, GamutAngle  # noqa: F401
from .. import util
from . import _convert as convert
import math
from . _delta import delta_e2000

WHITE = [1.0] * 3
BLACK = [0.0] * 3


def calc_contrast_ratio(lum1, lum2):
    """Get contrast ratio."""

    return (lum1 + 0.05) / (lum2 + 0.05) if (lum1 > lum2) else (lum2 + 0.05) / (lum1 + 0.05)


def calc_luminance(srgb):
    """Calculate luminance from `srgb` coordinates."""

    lsrgb = convert.lin_srgb(srgb)
    vector = [0.2126, 0.7152, 0.0722]
    return sum([r * v for r, v in zip(lsrgb, vector)])


class Tools(Gamut):
    """Color utilities."""

    def convert(self, space, *, fit=False):
        """Convert to color space."""

        space = space.lower()

        if fit:
            method = None if not isinstance(fit, str) else fit
            if not self.in_gamut(space):
                clone = self.clone()
                clone.fit(space, method=method)
                result = clone.convert(space)
                result._on_convert()
                return result

        obj = self.spaces.get(space)
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        result = obj(self)
        result._on_convert()
        return result

    def fit_coords(self, space=None, *, method=util.DEF_FIT):
        """Get coordinates within this space or fit to another space."""

        space = (self.space() if space is None else space).lower()
        method = self.space() if method is None else method
        if not self.in_gamut(space=space):
            clone = self.clone()
            clone.fit(method=method)
            return clone.coords()
        return self.coords()

    def is_achromatic(self):
        """Check if the color is achromatic."""

        return self._is_achromatic(self.coords())

    def _mix_channel(self, c1, c2, f1, f2=1.0):
        """
        Blend the channel.

        `f1` is the blend percent.
        When simulating transparency, `f1` can be looked at as the foreground alpha,
        while `f2` would be the background `alpha`. Usually we `f2` is always `1.0`
        as we normally overlay a transparent color on an opaque one.
        """

        return abs(c2 * f1 + c1 * f2 * (1 - f1))

    def _hue_mix_channel(self, c1, c2, f1, f2=1.0, *, hue="shorter"):
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

    def delta(self, color2):
        """Delta."""

        return delta_e2000(self, color2)

    def luminance(self):
        """Get perceived luminance."""

        return calc_luminance(convert.convert(self.coords(), self.space(), "srgb"))

    def contrast_ratio(self, color):
        """Get contrast ratio."""

        return calc_contrast_ratio(self.luminance(), color.luminance())

    def alpha_composite(self, background, *, space=None):
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
        return this.convert(current_space)

    def mix(self, color, percent=util.DEF_MIX, *, alpha=True, space=None, hue="shorter"):
        """Blend color."""

        current_space = self.space()
        if space is None:
            space = current_space
        else:
            space = space.lower()

        factor = util.clamp(float(percent), 0.0, 1.0)

        this = self.convert(space)
        if color.space() != space:
            color = color.convert(space)

        if this is None:
            raise ValueError('Invalid colorspace value: {}'.format(space))

        this._coords = [c for c in this._mix(this.coords(), color.coords(), factor, hue=hue)]
        if alpha:
            # This is a simple channel blend and not alpha compositing.
            this._alpha = this._mix_channel(this._alpha, color._alpha, factor)
        return this.convert(current_space)

    def to_generic_string(
        self, *, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs
    ):
        """Convert to CSS."""

        alpha = alpha is not False and (alpha is True or self._alpha < 1.0)

        coords = self.fit_coords(method=fit) if fit else self.coords()
        template = "color({} {} {} {} / {})" if alpha else "color({} {} {} {})"
        values = [
            util.fmt_float(coords[0], precision),
            util.fmt_float(coords[1], precision),
            util.fmt_float(coords[2], precision)
        ]
        if alpha:
            values.append(util.fmt_float(self._alpha, max(precision, util.DEF_PREC)))

        return template.format(self.space(), *values)
