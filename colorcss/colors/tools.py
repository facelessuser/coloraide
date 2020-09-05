"""Color tools."""
from .. import util
from ..util import convert


class _ColorTools:
    """Color utilities."""

    def _mix_channel(self, c1, c2, f1, f2=1.0, clamp_range=(None, None)):
        """
        Blend the channel.

        `f1` is the blend percent.
        When simulating transparency, `f1` can be looked at as the foreground alpha,
        while `f2` would be the background `alpha`. Usually we `f2` is always `1.0`
        as we normally overlay a transparent color on an opaque one.
        """

        return util.clamp(
            abs(c1 * f1 + c2 * f2 * (1 - f1)),
            clamp_range[0], clamp_range[1]
        )

    def _hue_mix_channel(self, c1, c2, f1, f2=1.0, scale=360.0):
        """Blend the hue style channel."""

        c1 *= scale
        c2 *= scale

        if abs(c1 % 360 - c2) > 180.0:
            if c1 < c2:
                c1 += 360.0
            else:
                c2 += 360.0

        value = abs(c1 * f1 + c2 * f2 * (1 - f1))
        if not (0.0 <= value <= 360.0):
            value = value % 360.0

        return value / scale

    def luminance(self):
        """Get perceived luminance."""

        srgb = self.convert("srgb") if self.get_colorspace() != "srgb" else this
        srgb = convert.lin_srgb([srgb._cr, srgb._cg, srgb._cb])
        vector = [0.2126, 0.7152, 0.0722]
        return sum([r * v for r, v in zip(srgb, vector)])

    def contrast_ratio(self, color):
        """Get contrast ratio."""

        lum1 = self.luminance()
        lum2 = color.luminance()

        return (lum1 + 0.05) / (lum2 + 0.05) if (lum1 > lum2) else (lum2 + 0.05) / (lum1 + 0.05)

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
            background = type(self)(self.DEF_BG)
        elif not isinstance(background, type(self)):
            background = type(self)(background)

        if self._alpha < 1.0:
            # Blend the channels using the alpha channel values as the factors
            # Afterwards, blend the alpha channels. This is different than blend.
            self._mix(background, self._alpha, background._alpha)
            self._alpha = self._alpha + background._alpha * (1.0 - self._alpha)
        return self

    def mix(self, color, percent, alpha=False, cs="lch"):
        """Blend color."""

        cs = cs.lower()
        factor = util.clamp(float(percent), 0.0, 1.0)

        this = None
        if self.get_colorspace() == cs:
            this = self
        else:
            this = self.convert(cs)

        if this is None:
            raise ValueError('Invalid colorspace value: {}'.format(str(cs)))

        this._mix(color, factor)
        if alpha:
            # This is a simple channel blend and not alpha compositing.
            this._alpha = util.mix_channel(this._alpha, color._alpha, factor)

        self.mutate(this)

    def invert(self):
        """Invert the color."""

        this = self.convert("srgb") if self.get_colorspace() != "srgb" else self
        this._cr ^= 0xFF
        this._cg ^= 0xFF
        this._cb ^= 0xFF
        self.mutate(this)

    def grayscale(self):
        """Convert the color with a grayscale filter."""

        self._grayscale()
