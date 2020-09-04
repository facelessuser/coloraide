"""HWB class."""
from .base import _Color
from .tools import _ColorTools
from .util import parse
from .util import convert
from .variables import handle_vars
from . import util
import re


class _HWB(_ColorTools, _Color):
    """HWB class."""

    COLORSPACE = "hwb"
    DEF_BG = "hwb(0 0% 0% / 1.0)"
    START = re.compile(r'(?i)hwb\(')
    CSS_MATCH = re.compile(
        r"""(?xi)
        hwb\(\s*
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
            if color.get_colorspace() == "hwb":
                self._ch, self._cw, self._cb, self._alpha = color._ch, color._cw, color._cb, color._alpha
            elif color.get_colorspace() == "srgb":
                self._ch, self._cw, self._cb = convert.rgb_to_hwb(color._cr, color._cg, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "hsl":
                self._ch, self._cw, self._cb = convert.hsl_to_hwb(color._ch, color._cs, color._cl)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lab":
                self._ch, self._cw, self._cb = convert.lab_to_hwb(color._cl, color._ca, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lch":
                self._ch, self._cw, self._cb = convert.lch_to_hwb(color._cl, color._cc, color._ch)
                self._alpha = color._alpha
            else:
                raise TypeError("Unexpected color space '{}' received".format(color.get_colorspace()))
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._ch, self._cw, self._cb, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._ch = color[0]
            self._cw = color[1]
            self._cb = color[2]
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
    def _cw(self):
        """Whiteness channel."""

        return self._c2

    @_cw.setter
    def _cw(self, value):
        """Set whiteness channel."""

        self._c2 = util.clamp(value, 0.0, 1.0)

    @property
    def _cb(self):
        """Blackness channel."""

        return self._c3

    @_cb.setter
    def _cb(self, value):
        """Set blackness channel."""

        self._c3 = util.clamp(value, 0.0, 1.0)

    def __str__(self):
        """String."""

        return self.to_css(alpha=True)

    __repr__ = __str__

    def is_achromatic(self, scale=16):
        """Check if the color is achromatic."""

        return util.round_half_up(self._cw * 100.0, scale) + util.round_half_up(self._cb * 100.0, scale) >= 100.0

    def _grayscale(self):
        """Convert to grayscale."""

        factor = 1.0 / (self._cw + self._cb)
        self._c2 = self._cw + factor
        self._c3 = self._cb + factor

    def _mix(self, color, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._ch = self._hue_mix_channel(self._ch, color._ch, factor, factor2)
        self._cw = self._mix_channel(self._cw, color._cw, factor, factor2)
        self._cb = self._mix_channel(self._cb, color._cb, factor, factor2)

    def to_css(
        self, *, alpha=None, comma=False, scale=0
    ):
        """Convert to CSS."""

        value = ''
        if alpha is not False and (alpha is True or self._alpha < 1.0):
            value = self._get_hwba(comma=comma, scale=scale)
        else:
            value = self._get_hwb(comma=comma, scale=scale)
        return value

    def _get_hwb(self, *, comma=False, scale=0):
        """Get RGB color."""

        template = "hwb({}, {}%, {}%)" if comma else "hwb({} {}% {}%)"

        return template.format(
            util.fmt_float(self._ch * 360.0, scale),
            util.fmt_float(self._cw * 100.0, scale),
            util.fmt_float(self._cb * 100.0, scale)
        )

    def _get_hwba(self, *, comma=False, scale=0):
        """Get RGB color with alpha channel."""

        template = "hwb({}, {}%, {}%, {})" if comma else "hwb({} {}% {}% / {})"

        return template.format(
            util.fmt_float(self._ch * 360.0, scale),
            util.fmt_float(self._cw * 100.0, scale),
            util.fmt_float(self._cb * 100.0, scale),
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
    def whiteness(self):
        """Whiteness channel."""

        return self._cw

    @whiteness.setter
    def whiteness(self, value):
        """Set whiteness channel."""

        self._cw = parse.norm_percent_channel(value) if isinstance(value, str) else float(value)

    @property
    def blackness(self):
        """Blackness channel."""

        return self._cb

    @blackness.setter
    def blackness(self, value):
        """Set blackness channel."""

        self._cb = parse.norm_percent_channel(value) if isinstance(value, str) else float(value)

    @classmethod
    def _split_channels(cls, color):
        """Split channels."""

        start = 4
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
    def css_match(cls, string, start=0, fullmatch=True, variables=None):
        """Match a CSS color string."""

        # We will only match variables within `func()` if variables are at the root level,
        # they should be handled by `colorcss`, not the color class.
        end = None
        if variables and cls.START:
            end = parse.bracket_match(cls.START, string, start, fullmatch)
            if end is not None:
                string = handle_vars(string, variables)

        m = cls.CSS_MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            return cls._split_channels(string[m.start(0):m.end(0)]), end if end is not None else m.end(0)
        return None, None
