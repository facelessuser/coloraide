"""HSL class."""
from .base import _Color
from .tools import _ColorTools
from .util import parse
from . import util
from .util import convert
import re


class _HSL(_ColorTools, _Color):
    """HSL class."""

    COLORSPACE = "hsl"
    DEF_BG = "hsl(0 0% 0% / 1.0)"
    CSS_MATCH = re.compile(
        r"""(?xi)
        hsla?\(\s*
        (?:
            # Space separated format
            {angle}{space}{percent}{space}{percent}(?:{slash}(?:{percent}|{float}))? |
            # comma separated format
            {angle}{comma}{percent}{comma}{percent}(?:{comma}(?:{percent}|{float}))?
        )
        \s*\)
        """.format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            if color.get_colorspace() == "hsl":
                self._ch, self._cs, self._cl, self._alpha = color._ch, color._cs, color._cl, color._alpha
            elif color.get_colorspace() == "srgb":
                self._ch, self._cs, self._cl = convert.rgb_to_hsl(color._cr, color._cg, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "hwb":
                self._ch, self._cs, self._cl = convert.hwb_to_hsl(color._ch, color._cw, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lab":
                self._ch, self._cs, self._cl = convert.lab_to_hsl(color._cl, color._ca, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lch":
                self._ch, self._cs, self._cl = convert.lch_to_hsl(color._cl, color._cc, color._ch)
                self._alpha = color._alpha
            else:
                raise TypeError("Unexpected color space '{}' received".format(color.get_colorspace()))
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._ch, self._cs, self._cl, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._ch = color[0]
            self._cs = color[1]
            self._cl = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    @property
    def _ch(self):
        """Hue channel."""

        return self._c1

    @_ch.setter
    def _ch(self, value):
        """Set hue channel."""

        self._c1 = value if 0.0 <= value <= 1.0 else value % 1.0

    @property
    def _cs(self):
        """Saturation channel."""

        return self._c2

    @_cs.setter
    def _cs(self, value):
        """Set saturation channel."""

        self._c2 = util.clamp(value, 0.0, 1.0)

    @property
    def _cl(self):
        """Lightness channel."""

        return self._c3

    @_cl.setter
    def _cl(self, value):
        """Set lightness channel."""

        self._c3 = util.clamp(value, 0.0, 1.0)

    def __str__(self):
        """String."""

        return self.to_css(alpha=True)

    def is_achromatic(self, scale=16):
        """Check if the color is achromatic."""

        return util.round_half_up(self._cs * 360.0, scale) <= 0.0

    def _grayscale(self):
        """Convert to grayscale."""

        self._c1 = 0.0
        self._cs = 0.0

    def _mix(self, color, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._ch = self._hue_mix_channel(self._ch, color._ch, factor, factor2)
        self._cl = self._mix_channel(self._cl, color._cl, factor, factor2)
        self._cs = self._mix_channel(self._cs, color._cs, factor, factor2)

    def to_css(
        self, *, alpha=None, comma=False, scale=0
    ):
        """Convert to CSS."""

        value = ''
        if alpha is not False and (alpha is True or self._alpha < 1.0):
            value = self._get_hsla(comma=comma, scale=scale)
        else:
            value = self._get_hsl(comma=comma, scale=scale)
        return value

    def _get_hsl(self, *, comma=False, scale=0):
        """Get RGB color."""

        template = "hsl({}, {}%, {}%)" if comma else "hsl({} {}% {}%)"

        return template.format(
            util.fmt_float(self._ch * 360.0, scale),
            util.fmt_float(self._cs * 100.0, scale),
            util.fmt_float(self._cl * 100.0, scale)
        )

    def _get_hsla(self, *, comma=False, scale=0):
        """Get RGB color with alpha channel."""

        template = "hsla({}, {}%, {}%, {})" if comma else "hsl({} {}% {}% / {})"

        return template.format(
            util.fmt_float(self._ch * 360.0, scale),
            util.fmt_float(self._cs * 100.0, scale),
            util.fmt_float(self._cl * 100.0, scale),
            util.fmt_float(self._alpha, max(3, scale))
        )

    @property
    def hue(self):
        """Hue channel."""

        return self._ch

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._ch = parse.norm_hue_channel(value) if isinstance(value, str) else float(value)

    @property
    def saturation(self):
        """Saturation channel."""

        return self._cs

    @saturation.setter
    def saturation(self, value):
        """Saturate or unsaturate the color by the given factor."""

        self._cs = parse.norm_percent_channel(value) if isinstance(value, str) else float(value)

    @property
    def lightness(self):
        """Lightness channel."""

        return self._cl

    @lightness.setter
    def lightness(self, value):
        """Set lightness channel."""

        self._cl = parse.norm_percent_channel(value) if isinstance(value, str) else float(value)

    @classmethod
    def _split_channels(cls, color):
        """Split channels."""

        start = 5 if color[:4].lower() == 'hsla' else 4
        channels = []
        for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
            if i == 0:
                channels.append(parse.norm_hue_channel(c))
            elif i == 3:
                channels.append(parse.norm_alpha_channel(c))
            else:
                channels.append(parse.norm_percent_channel(c))
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
