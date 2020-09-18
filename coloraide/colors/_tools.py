"""Color tools."""
from ._gamut import _Gamut, GamutBound, GamutUnbound, GamutAngle, gamut_clip  # noqa: F401
from .. import util
from ..util import convert
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


class _ColorTools(_Gamut):
    """Color utilities."""

    def convert(self, space, fit=False):
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

    def get_coords(self, fit=False):
        """Get coordinates within this space or fit to another space."""

        if fit:
            method = self.space() if not isinstance(fit, str) else fit
            if not self.in_gamut():
                clone = self.clone()
                clone.fit(method=method)
                return clone.coords()
        return self.coords()

    def is_achromatic(self):
        """Check if the color is achromatic."""

        return self._is_achromatic(self._channels)

    def _mix_channel(self, c1, c2, f1, f2=1.0):
        """
        Blend the channel.

        `f1` is the blend percent.
        When simulating transparency, `f1` can be looked at as the foreground alpha,
        while `f2` would be the background `alpha`. Usually we `f2` is always `1.0`
        as we normally overlay a transparent color on an opaque one.
        """

        return abs(c2 * f1 + c1 * f2 * (1 - f1))

    def _hue_mix_channel(self, c1, c2, f1, f2=1.0):
        """Blend the hue style channel."""

        if math.isnan(c1) and math.isnan(c2):
            return 0.0
        elif math.isnan(c1):
            return c2
        elif math.isnan(c2):
            return c1

        if abs(c1 % 360 - c2) > 180.0:
            if c1 < c2:
                c1 += 360.0
            else:
                c2 += 360.0

        value = self._mix_channel(c1, c2, f1, f2)
        if not (0.0 <= value <= 360.0):
            value = value % 360.0

        return value

    def delta(self, color2):
        """Delta."""

        return delta_e2000(self, color2)

    def luminance(self):
        """Get perceived luminance."""

        return calc_luminance(convert.convert(self._channels, self.space(), "srgb"))

    def min_contrast(self, color, target):
        """
        Get the color with the best contrast.

        # https://drafts.csswg.org/css-color/#contrast-adjuster
        """

        lum1 = self.luminance()
        lum2 = color.luminance()
        ratio = calc_contrast_ratio(lum1, lum2)

        # We already meet the minimum or the target is impossible
        if target < 1 or ratio >= target:
            return

        required_lum = ((lum2 + 0.05) / target) - 0.05
        if required_lum < 0:
            required_lum = target * (lum2 + 0.05) - 0.05

        # Too much precision isn't helpful
        required_lum = round(required_lum, 3)

        is_dark = lum2 < lum1
        mix = self.new(WHITE if is_dark else BLACK, "srgb")
        if is_dark:
            min_mix = 0.0
            max_mix = 1.0
            last_lum = 1.0
        else:
            max_mix = 0.0
            min_mix = 1.0
            last_lum = 0.0
        last_mix = 1.0

        temp = self.clone().convert("srgb")
        c1, c2, c3 = temp._channels

        while abs(min_mix - max_mix) >= 0.002:
            mid_mix = round((max_mix + min_mix) / 2, 3)

            temp._mix([c1, c2, c3], mix._channels, mid_mix)
            lum2 = temp.luminance()

            if lum2 > required_lum:
                max_mix = mid_mix
            else:
                min_mix = mid_mix

            if ((lum2 >= required_lum and lum2 < last_lum) if is_dark else (lum2 <= required_lum and lum2 > last_lum)):
                last_lum = lum2
                last_mix = mid_mix

        # Use the best, last values
        temp._mix([c1, c2, c3], mix._channels, last_mix)
        self.mutate(temp)

    def contrast_ratio(self, color):
        """Get contrast ratio."""

        return calc_contrast_ratio(self.luminance(), color.luminance())

    def is_dark(self):
        """Check if color is dark."""

        return self.luminance() < 0.5

    def is_light(self):
        """Check if color is light."""

        return self.luminance() >= 0.5

    def alpha_composite(self, background=None):
        """
        Apply the given transparency with the given background.

        This gives a color that represents what the eye sees with
        the transparent color against the given background.
        """

        if background is None:
            background = self.new(self.DEF_BG)
        elif not isinstance(background, type(self)):
            background = self.new(background)

        if self._alpha < 1.0:
            # Blend the channels using the alpha channel values as the factors
            # Afterwards, blend the alpha channels. This is different than blend.
            self._mix(self._channels, background._channels, self._alpha, background._alpha)
            self._alpha = self._alpha + background._alpha * (1.0 - self._alpha)
        return self

    def mix(self, color, percent, alpha=False, space="lch"):
        """Blend color."""

        space = space.lower()
        factor = util.clamp(float(percent), 0.0, 1.0)

        this = None
        if self.space() == space:
            this = self
        else:
            this = self.convert(space)

        if color.space() != space:
            color = color.convert(space)

        if this is None:
            raise ValueError('Invalid colorspace value: {}'.format(space))

        this._mix(this._channels, color._channels, factor)
        if alpha:
            # This is a simple channel blend and not alpha compositing.
            this._alpha = self._mix_channel(this._alpha, color._alpha, factor)
        self.mutate(this)

    def invert(self):
        """Invert the color."""

        this = self.convert("srgb") if self.space() != "srgb" else self
        this._cr ^= 0xFF
        this._cg ^= 0xFF
        this._cb ^= 0xFF
        self.mutate(this)

    def grayscale(self):
        """Convert the color with a grayscale filter."""

        self._grayscale()

    def to_generic_string(
        self, *, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs
    ):
        """Convert to CSS."""

        alpha = alpha is not False and (alpha is True or self._alpha < 1.0)

        coords = self.get_coords(fit=fit)
        template = "color({} {} {} {} / {})" if alpha else "color({} {} {} {})"
        values = [
            util.fmt_float(coords[0], precision),
            util.fmt_float(coords[1], precision),
            util.fmt_float(coords[2], precision)
        ]
        if alpha:
            values.append(util.fmt_float(self._alpha, max(precision, util.DEF_PREC)))

        return template.format(self.space(), *values)
