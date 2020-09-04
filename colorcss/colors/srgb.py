"""SRGB color class."""
from .base import _Color
from .tools import _ColorTools
from . import css_names
from .util import parse
from .util import convert
from . import util
from .variables import handle_vars
import re

RE_COMPRESS = re.compile(r'(?i)^#({hex})\1({hex})\2({hex})\3(?:({hex})\4)?$'.format(**parse.COLOR_PARTS))


class _SRGB(_ColorTools, _Color):
    """SRGB class."""

    COLORSPACE = "srgb"
    DEF_BG = "rgb(0 0 0 / 1)"

    START = re.compile(r'(?i)rgba?\(')

    CSS_MATCH = re.compile(
        r"""(?xi)
        (?:
            # RGB syntax
            rgba?\(\s*
            (?:
                # Space separated format
                (?:
                    # Float form
                    (?:{float}{space}){{2}}{float} |
                    # Percent form
                    (?:{percent}{space}){{2}}{percent}
                )({slash}(?:{percent}|{float}))? |
                # Comma separated format
                (?:
                    # Float form
                    (?:{float}{comma}){{2}}{float} |
                    # Percent form
                    (?:{percent}{comma}){{2}}{percent}
                )({comma}(?:{percent}|{float}))?
            )
            \s*\) |
            # Hex syntax
            \#(?:{hex}{{6}}(?:{hex}{{2}})?|{hex}{{3}}(?:{hex})?) |
            # Names
            [a-z0-9]+
        )
        """.format(**parse.COLOR_PARTS)
    )

    HEX_MATCH = re.compile(r"(?i)#(?:({hex}{{6}})({hex}{{2}})?|({hex}{{3}})({hex})?)".format(**parse.COLOR_PARTS))

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)
        self._c4 = 0.0

        if isinstance(color, _Color):
            if color.get_colorspace() == "srgb":
                self._cr, self._cg, self._cb, self._alpha = color._cr, color._cg, color._cb, color._alpha
            elif color.get_colorspace() == "hsl":
                self._cr, self._cg, self._cb = convert.hsl_to_rgb(color._ch, color._cs, color._cl)
                self._alpha = color._alpha
            elif color.get_colorspace() == "hwb":
                self._cr, self._cg, self._cb = convert.hwb_to_rgb(color._ch, color._cw, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lab":
                self._cr, self._cg, self._cb = convert.lab_to_rgb(color._cl, color._ca, color._cb)
                self._alpha = color._alpha
            elif color.get_colorspace() == "lch":
                self._cr, self._cg, self._cb = convert.lch_to_rgb(color._cl, color._cc, color._ch)
                self._alpha = color._alpha
            else:
                raise TypeError("Unexpected color space '{}' received".format(color.get_colorspace()))
        elif isinstance(color, str):
            if color is None:
                color = self.DEF_BG
            values = self.css_match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cr, self._cg, self._cb, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cr = color[0]
            self._cg = color[1]
            self._cb = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))
        self._update_hue()

    def _update_hue(self):
        """Update hue."""

        if not self.is_achromatic():
            h = convert.rgb_to_hsv(self._cr, self._cg, self._cb)[0]
            self._c4 = h if 0.0 <= h <= 1.0 else h % 1.0

    def mutate(self, obj):
        """Update from color."""

        if self is obj:
            self._update_hue()
            return

        if not isinstance(obj, type(self)):
            obj = type(self)(obj)

        self._c1 = obj._c1
        self._c2 = obj._c2
        self._c3 = obj._c3
        self._alpha = obj._alpha
        self._update_hue()

    @property
    def _cr(self):
        """Red channel."""

        return self._c1

    @_cr.setter
    def _cr(self, value):
        """Set red channel."""

        self._c1 = util.clamp(value, 0.0, 1.0)

    @property
    def _cg(self):
        """Green channel."""

        return self._c2

    @_cg.setter
    def _cg(self, value):
        """Set green channel."""

        self._c2 = util.clamp(value, 0.0, 1.0)

    @property
    def _cb(self):
        """Blue channel."""

        return self._c3

    @_cb.setter
    def _cb(self, value):
        """Set blue channel."""

        self._c3 = util.clamp(value, 0.0, 1.0)

    @property
    def _ch(self):
        """Hue channel."""

        return self._c4

    @_ch.setter
    def _ch(self, value):
        """Set hue channel."""

        self._c4 = value if 0.0 <= value <= 1.0 else value % 1.0

    def __str__(self):
        """String."""

        return self.to_css(alpha=True)

    def is_achromatic(self):
        """Check if the color is achromatic."""

        r = round(self._cr * 255.0)
        g = round(self._cg * 255.0)
        b = round(self._cb * 255.0)

        return r == g and g == b

    def _grayscale(self):
        """Convert to grayscale."""

        self._cr = self.luminance()
        self._cg = self.luminance()
        self._cb = self.luminance()

    def _mix(self, color, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._cr = self._mix_channel(self._cr, color._cr, factor, factor2)
        self._cg = self._mix_channel(self._cg, color._cg, factor, factor2)
        self._cb = self._mix_channel(self._cb, color._cb, factor, factor2)
        self._update_hue()

    def to_css(
        self, *, alpha=None, name=False, hex_code=False, hex_upper=False, compress=False, comma=False, percent=False,
        scale=0
    ):
        """Convert to CSS."""

        value = ''
        if hex_code or name:
            if alpha is not False and (alpha is True or self._alpha < 1.0):
                h = self._get_hexa(compress=compress, hex_upper=hex_upper)
            else:
                h = self._get_hex(compress=compress, hex_upper=hex_upper)
            if hex_code:
                value = h
            if name:
                length = len(h) - 1
                index = int(length / 4)
                if length in (8, 4) and h[-index:].lower() == ("f" * index):
                    h = h[:-index]
                n = css_names.hex2name(h)
                if n is not None:
                    value = n
        if not value:
            if alpha is not False and (alpha is True or self._alpha < 1.0):
                value = self._get_rgba(comma=comma, percent=percent, scale=scale)
            else:
                value = self._get_rgb(comma=comma, percent=percent, scale=scale)
        return value

    def _get_rgb(self, *, comma=False, percent=False, scale=0):
        """Get RGB color."""

        factor = 100.0 if percent else 255.0

        if percent:
            template = "rgb({}%, {}%, {}%)" if comma else "rgb({}% {}% {}%)"
        else:
            template = "rgb({}, {}, {})" if comma else "rgb({} {} {})"

        return template.format(
            util.fmt_float(self._cr * factor, scale),
            util.fmt_float(self._cg * factor, scale),
            util.fmt_float(self._cb * factor, scale)
        )

    def _get_rgba(self, *, comma=False, percent=False, scale=0):
        """Get RGB color with alpha channel."""

        factor = 100.0 if percent else 255.0

        if percent:
            template = "rgba({}%, {}%, {}%, {})" if comma else "rgb({}% {}% {}% / {})"
        else:
            template = "rgba({}, {}, {}, {})" if comma else "rgb({} {} {} / {})"

        return template.format(
            util.fmt_float(self._cr * factor, scale),
            util.fmt_float(self._cg * factor, scale),
            util.fmt_float(self._cb * factor, scale),
            util.fmt_float(self._alpha, max(3, scale))
        )

    def _get_hexa(self, *, compress=False, hex_upper=False):
        """Get the RGB color with the alpha channel."""

        template = "#{:02x}{:02x}{:02x}{:02x}"
        if hex_upper:
            template = template.upper()

        value = template.format(
            round(self._cr * 255.0),
            round(self._cg * 255.0),
            round(self._cb * 255.0),
            round(self._alpha * 255.0)
        )

        if compress:
            m = RE_COMPRESS.match(value)
            if m:
                value = m.expand(r"#\1\2\3\4")
        return value

    def _get_hex(self, *, compress=False, hex_upper=False):
        """Get the `RGB` value."""

        template = "#{:02x}{:02x}{:02x}"
        if hex_upper:
            template = template.upper()

        value = template.format(
            round(self._cr * 255.0),
            round(self._cg * 255.0),
            round(self._cb * 255.0)
        )

        if compress:
            m = RE_COMPRESS.match(value)
            if m:
                value = m.expand(r"#\1\2\3")
        return value

    @property
    def red(self):
        """Adjust red."""

        return self._cr

    @red.setter
    def red(self, value):
        """Adjust red."""

        self._cr = parse.norm_rgb_channel(value) if isinstance(value, str) else float(value)
        self._update_hue()

    @property
    def green(self):
        """Adjust green."""

        return self._cg

    @green.setter
    def green(self, value):
        """Adjust green."""

        self._cg = parse.norm_rgb_channel(value) if isinstance(value, str) else float(value)
        self._update_hue()

    @property
    def blue(self):
        """Adjust blue."""

        return self._cb

    @blue.setter
    def blue(self, value):
        """Adjust blue."""

        self._cb = parse.norm_rgb_channel(value) if isinstance(value, str) else float(value)
        self._update_hue()

    @classmethod
    def _split_channels(cls, color):
        """Split channels."""

        if color[:3].lower().startswith('rgb'):
            start = 5 if color[:4].lower().startswith('rgba') else 4
            channels = []
            for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
                channels.append(parse.norm_alpha_channel(c) if i == 3 else parse.norm_rgb_channel(c))
            if len(channels) == 3:
                channels.append(1.0)
            return channels
        else:
            m = cls.HEX_MATCH.match(color)
            assert(m is not None)
            if m.group(1):
                return (
                    int(color[1:3], 16) * parse.RGB_CHANNEL_SCALE,
                    int(color[3:5], 16) * parse.RGB_CHANNEL_SCALE,
                    int(color[5:7], 16) * parse.RGB_CHANNEL_SCALE,
                    int(m.group(2), 16) * parse.RGB_CHANNEL_SCALE if m.group(2) else 1.0
                )
            else:
                return (
                    int(color[1] * 2, 16) * parse.RGB_CHANNEL_SCALE,
                    int(color[2] * 2, 16) * parse.RGB_CHANNEL_SCALE,
                    int(color[3] * 2, 16) * parse.RGB_CHANNEL_SCALE,
                    int(m.group(4), 16) * parse.RGB_CHANNEL_SCALE if m.group(4) else 1.0
                )

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
                start = 0

        m = cls.CSS_MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            if not string[start:5].lower().startswith(('#', 'rgb(', 'rgba(')):
                string = css_names.name2hex(string[m.start(0):m.end(0)])
                if string is not None:
                    return cls._split_channels(string), end if end is not None else m.end(0)
            else:
                return cls._split_channels(string[m.start(0):m.end(0)]), end if end is not None else m.end(0)
        return None, None

    __repr__ = __str__
