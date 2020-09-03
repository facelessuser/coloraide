"""LAB class."""
from .base import _Color
from .tools import _ColorTools
from .util import parse
from .util import convert
from . import util
import re


class _LAB(_ColorTools, _Color):
    """LAB class."""

    COLORSPACE = "lab"
    DEF_BG = "lab(0% 0 0 / 1.0)"
    CSS_MATCH = re.compile(
        r"""(?xi)
        lab\(\s*
        (?:
            # Space separated format
            {percent}{space}{float}{space}{float}(?:{slash}(?:{percent}|{float}))? |
            # comma separated format
            {percent}{comma}{float}{comma}{float}(?:{comma}(?:{percent}|{float}))?
        )
        \s*\)
        """.format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            if color.get_colorspace() == "lab":
                self._cl, self._ca, self._cb, self._alpha = color._cl, color._ca, color._cb, color._alpha
            elif color.get_colorspace() == "srgb":
                self._cl, self._ca, self._cb = convert.rgb_to_lab(color._cr, color._cg, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "hsl":
                self._cl, self._ca, self._cb = convert.hsl_to_lab(color._ch, color._cs, color._cl)
                self._alpha = color._alpha
            elif color.get_colorspace() == "hwb":
                self._cl, self._ca, self._cb = convert.hwb_to_lab(color._ch, color._cw, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lch":
                self._cl, self._ca, self._cb = convert.lch_to_lab(color._cl, color._cc, color._ch)
                self._alpha = color._alpha
            else:
                raise TypeError("Unexpected color space '{}' received".format(color.get_colorspace()))
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cl, self._ca, self._cb, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cl = color[0]
            self._ca = color[1]
            self._cb = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    @property
    def _cl(self):
        """Hue channel."""

        return self._c1

    @_cl.setter
    def _cl(self, value):
        """Set hue channel."""

        self._c1 = util.clamp(value, 0.0, None)

    @property
    def _ca(self):
        """A on LAB axis."""

        return self._c2

    @_ca.setter
    def _ca(self, value):
        """Set A on LAB axis."""

        self._c2 = float(value)

    @property
    def _cb(self):
        """B on LAB axis."""

        return self._c3

    @_cb.setter
    def _cb(self, value):
        """Set B on LAB axis."""

        self._c3 = float(value)

    def __str__(self):
        """String."""

        return self.to_css(alpha=True)

    def is_achromatic(self, scale=16):
        """Check if the color is achromatic."""

        return util.round_half_up(self._ca, scale) == 0.0 and util.round_half_up(self._cb, scale) == 0.0

    def _grayscale(self):
        """Convert to grayscale."""

        self._ca = 0
        self._cb = 0

    def _mix(self, color, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._cl = self._mix_channel(self._cl, color._cl, factor, factor2, clamp_range=(0.0, None))
        self._ca = self._mix_channel(self._ca, color._ca, factor, factor2, clamp_range=(None, None))
        self._cb = self._mix_channel(self._cb, color._cb, factor, factor2, clamp_range=(None, None))

    def to_css(
        self, *, alpha=None, comma=False, scale=0
    ):
        """Convert to CSS."""

        value = ''
        if alpha is not False and (alpha is True or self._alpha < 1.0):
            value = self._get_laba(comma=comma, scale=scale)
        else:
            value = self._get_lab(comma=comma, scale=scale)
        return value

    def _get_lab(self, *, comma=False, scale=0):
        """Get LAB color."""

        template = "lab({}%, {}, {})" if comma else "lab({}% {} {})"

        return template.format(
            util.fmt_float(self._cl, scale),
            util.fmt_float(self._ca, scale),
            util.fmt_float(self._cb, scale)
        )

    def _get_laba(self, *, comma=False, scale=0):
        """Get LAB color with alpha channel."""

        template = "lab({}%, {}, {}, {})" if comma else "lab({}% {} {} / {})"

        return template.format(
            util.fmt_float(self._cl, scale),
            util.fmt_float(self._ca, scale),
            util.fmt_float(self._cb, scale),
            util.fmt_float(self._alpha, max(3, scale))
        )

    @property
    def l(self):
        """L channel."""

        return self._cl

    @l.setter
    def l(self, value):
        """Get true luminance."""

        self._cl = parse.norm_lab_lightness(value) if isinstance(value, str) else float(value)

    @property
    def a(self):
        """A channel."""

        return self._ca

    @a.setter
    def a(self, value):
        """A axis."""

        self._ca = float(value)

    @property
    def b(self):
        """B channel."""

        return self._cb

    @b.setter
    def b(self, value):
        """B axis."""

        self._cb = float(value)

    @classmethod
    def _split_channels(cls, color):
        """Split channels."""

        start = 4
        channels = []
        for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
            if i == 0:
                channels.append(parse.norm_lab_lightness(c))
            elif i == 3:
                channels.append(parse.norm_alpha_channel(c))
            else:
                channels.append(float(c))
        if len(channels) == 3:
            channels.append(1.0)
        return channels

    @classmethod
    def css_match(cls, string):
        """Match a CSS color string."""

        m = cls.CSS_MATCH.match(string)
        if m is not None and m.end(0) == len(string):
            return cls._split_channels(string)
        return None

    __repr__ = __str__
