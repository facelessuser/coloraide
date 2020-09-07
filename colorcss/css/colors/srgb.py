"""SRGB color class."""
from . import css_names
import re
from ...colors import srgb as generic
from ... import util
from ... import parse

RE_COMPRESS = re.compile(r'(?i)^#({hex})\1({hex})\2({hex})\3(?:({hex})\4)?$'.format(**parse.COLOR_PARTS))


class _SRGB(generic._SRGB):
    """SRGB class."""

    DEF_BG = "rgb(0 0 0 / 1)"
    START = re.compile(r'(?i)\brgba?\(')
    MATCH = re.compile(
        r"""(?xi)
        (?:
            # RGB syntax
            \brgba?\(\s*
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
            \b[a-z]{{3,}}\b
        )
        """.format(**parse.COLOR_PARTS)
    )

    HEX_MATCH = re.compile(r"(?i)#(?:({hex}{{6}})({hex}{{2}})?|({hex}{{3}})({hex})?)".format(**parse.COLOR_PARTS))

    def __init__(self, color=None):
        """Initialize."""

        super().__init__(color)

    def to_string(
        self, *, alpha=None, name=False, hex_code=False, hex_upper=False, compress=False, comma=False, percent=False,
        scale=util.INF, raw=False
    ):
        """Convert to CSS."""

        if raw:
            return super().to_string(alpha=alpha, scale=scale)

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

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel string."""

        if channel in (0, 1, 2):
            if value.startswith('#'):
                return int(value[1:], 16) * parse.RGB_CHANNEL_SCALE
            else:
                return parse.norm_rgb_channel(value)
        elif channel == -1:
            if value.startswith('#'):
                return int(value[1:], 16) * parse.RGB_CHANNEL_SCALE
            else:
                return parse.norm_alpha_channel(value)

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        if color[:3].lower().startswith('rgb'):
            start = 5 if color[:4].lower().startswith('rgba') else 4
            channels = []
            for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
                if i <= 2:
                    channels.append(cls.tx_channel(i, c))
                else:
                    channels.append(cls.tx_channel(-1, c))
            if len(channels) == 3:
                channels.append(1.0)
            return channels
        else:
            m = cls.HEX_MATCH.match(color)
            assert(m is not None)
            if m.group(1):
                return (
                    cls.tx_channel(0, "#" + color[1:3]),
                    cls.tx_channel(1, "#" + color[3:5]),
                    cls.tx_channel(2, "#" + color[5:7]),
                    cls.tx_channel(-1, "#" + m.group(2)) if m.group(2) else 1.0
                )
            else:
                return (
                    cls.tx_channel(0, "#" + color[1] * 2),
                    cls.tx_channel(1, "#" + color[2] * 2),
                    cls.tx_channel(2, "#" + color[3] * 2),
                    cls.tx_channel(-1, "#" + m.group(4)) if m.group(4) else 1.0
                )

    @classmethod
    def match(cls, string, start=0, fullmatch=True, variables=None):
        """Match a CSS color string."""

        # We will only match variables within `func()` if variables are at the root level,
        # they should be handled by `colorcss`, not the color class.
        end = None
        if variables and cls.START:
            end = parse.bracket_match(cls.START, string, start, fullmatch)
            if end is not None:
                string = parse.handle_vars(string, variables)
                start = 0

        m = cls.MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            if not string[start:start + 5].lower().startswith(('#', 'rgb(', 'rgba(')):
                string = css_names.name2hex(string[m.start(0):m.end(0)])
                if string is not None:
                    return cls.split_channels(string), end if end is not None else m.end(0)
            else:
                return cls.split_channels(string[m.start(0):m.end(0)]), end if end is not None else m.end(0)
        return None, None
