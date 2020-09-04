"""LCH class."""
from .base import _Color
from .tools import _ColorTools
from .util import parse
from .util import convert
from .variables import handle_vars
from . import util
import re


class _LCH(_ColorTools, _Color):
    """LCH class."""

    COLORSPACE = "lch"
    DEF_BG = "lch(0% 0 0 / 1.0)"
    START = re.compile(r'(?i)(?:lch|gray)\(')
    CSS_MATCH = re.compile(
        r"""(?xi)
        (?:
            lch\(\s*
            (?:
                # Space separated format
                {percent}{space}{float}{space}{angle}(?:{slash}(?:{percent}|{float}))? |
                # comma separated format
                {percent}{comma}{float}{comma}{angle}(?:{comma}(?:{percent}|{float}))?
            )
            \s*\) |
            gray\(
            (?:
               # Space separated format
               {float}(?:{slash}(?:{percent}|{float}))? |
               # comma separated format
               {float}(?:{comma}(?:{percent}|{float}))?
            )
            \)
        )
        """.format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            if color.get_colorspace() == "lch":
                self._cl, self._cc, self._ch, self._alpha = color._cl, color._cc, color._ch, color._alpha
            elif color.get_colorspace() == "srgb":
                self._cl, self._cc, self._ch = convert.rgb_to_lch(color._cr, color._cg, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "hsl":
                self._cl, self._cc, self._ch = convert.hsl_to_lch(color._ch, color._cs, color._cl)
                self._alpha = color._alpha
            elif color.get_colorspace() == "hwb":
                self._cl, self._cc, self._ch = convert.hwb_to_lch(color._ch, color._cw, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lab":
                self._cl, self._cc, self._ch = convert.lab_to_lch(color._cl, color._ca, color._cb)
                self._alpha = color._alpha
            else:
                raise TypeError("Unexpected color space '{}' received".format(color.get_colorspace()))
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cl, self._cc, self._ch, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cl = color[0]
            self._cc = color[0]
            self._ch = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    @property
    def _cl(self):
        """Lightness channel."""

        return self._c1

    @_cl.setter
    def _cl(self, value):
        """Set lightness channel."""

        self._c1 = util.clamp(value, 0.0, None)

    @property
    def _cc(self):
        """Chroma channel."""

        return self._c2

    @_cc.setter
    def _cc(self, value):
        """Set chroma channel."""

        self._c2 = util.clamp(value, 0.0, None)

    @property
    def _ch(self):
        """Hue channel."""

        return self._c3

    @_ch.setter
    def _ch(self, value):
        """Set B on LAB axis."""

        self._c3 = value if 0.0 <= value <= 360.0 else value % 360.0

    def __str__(self):
        """String."""

        return self.to_css(alpha=True)

    def is_achromatic(self, scale=16):
        """Check if the color is achromatic."""

        return self.round_half_up(self._cc, scale) <= 0

    def _grayscale(self):
        """Convert to grayscale."""

        self._cc = 0

    def _mix(self, color, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._cl = self._mix_channel(self._cl, color._cl, factor, factor2, clamp_range=(0.0, None))
        self._cc = self._mix_channel(self._cc, color._cc, factor, factor2, clamp_range=(0.0, None))
        self._ch = self._hue_mix_channel(self._ch, color._ch, factor, factor2, scale=1.0)

    def to_css(
        self, *, alpha=None, comma=False, gray=False, scale=0
    ):
        """Convert to CSS."""

        value = ''
        if gray and self.is_achromatic(scale):
            if alpha is not False and (alpha is True or self._alpha < 1.0):
                value = self._get_gray(scale=scale)
            else:
                value = self._get_graya(comma=comma, scale=scale)
        else:
            if alpha is not False and (alpha is True or self._alpha < 1.0):
                value = self._get_lcha(comma=comma, scale=scale)
            else:
                value = self._get_lch(comma=comma, scale=scale)
        return value

    def _get_lch(self, *, comma=False, scale=0):
        """Get LCH color."""

        template = "lch({}%, {}, {})" if comma else "lch({}% {} {})"

        return template.format(
            util.fmt_float(self._cl, scale),
            util.fmt_float(self._cc, scale),
            util.fmt_float(self._ch, scale)
        )

    def _get_lcha(self, *, comma=False, scale=0):
        """Get LCH color with alpha channel."""

        template = "lch({}%, {}, {}, {})" if comma else "lch({}% {} {} / {})"

        return template.format(
            util.fmt_float(self._cl, scale),
            util.fmt_float(self._cc, scale),
            util.fmt_float(self._ch, scale),
            util.fmt_float(self._alpha, max(3, scale))
        )

    def _get_gray(self, *, scale=0):
        """Get gray color with alpha."""

        template = "gray({})"

        return template.format(
            util.fmt_float(self._cl, scale)
        )

    def _get_graya(self, *, comma=False, scale=0):
        """Get gray color with alpha."""

        template = "gray({}, {})" if comma else "gray({} / {})"

        return template.format(
            util.fmt_float(self._cl, scale),
            util.fmt_float(self._alpha, max(3, scale))
        )

    @property
    def lightness(self):
        """Lightness."""

        return self._cl

    @lightness.setter
    def lightness(self, value):
        """Get true luminance."""

        self._cl = parse.norm_lab_lightness(value) if isinstance(value, str) else float(value)

    @property
    def chroma(self):
        """Chroma."""

        return self._cc

    @chroma.setter
    def chroma(self, value):
        """chroma."""

        self._cc = util.clamp(float(value), 0.0, None) if isinstance(value, str) else float(value)

    @property
    def hue(self):
        """Hue."""

        return self._ch

    @hue.setter
    def hue(self, value):
        """Shift the hue."""

        self._ch = parse.norm_hue_channel(value) * 360.0 if isinstance(value, str) else float(value)

    @classmethod
    def _split_channels(cls, color):
        """Split channels."""

        if color[:4].lower().startswith('gray'):
            start = 5
            channels = []
            alpha = None
            for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
                if i == 0:
                    channels.append(util.clamp(float(c), 0.0, None))
                else:
                    alpha = parse.norm_alpha_channel(c)
            channels.extend([0.0, 0.0])
            channels.append(1.0 if alpha is None else alpha)
        else:
            start = 4
            channels = []
            for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
                if i == 0:
                    channels.append(parse.norm_lab_lightness(c))
                if i == 2:
                    channels.append(parse.norm_hue_channel(c) * 360.0)
                elif i == 3:
                    channels.append(parse.norm_alpha_channel(c))
                else:
                    channels.append(float(c))
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

    __repr__ = __str__
