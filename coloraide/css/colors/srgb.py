"""SRGB color class."""
from . import css_names
import re
from ...colors import srgb as generic
from ... import util
from ...util import parse

RE_COMPRESS = re.compile(r'(?i)^#({hex})\1({hex})\2({hex})\3(?:({hex})\4)?$'.format(**parse.COLOR_PARTS))


class SRGB(generic.SRGB):
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
            \#(?:{hex}{{6}}(?:{hex}{{2}})?|{hex}{{3}}(?:{hex})?)\b |
            # Names
            \b(?<!\#)[a-z]{{3,}}(?!\()\b
        )
        """.format(**parse.COLOR_PARTS)
    )

    HEX_MATCH = re.compile(r"(?i)#(?:({hex}{{6}})({hex}{{2}})?|({hex}{{3}})({hex})?)\b".format(**parse.COLOR_PARTS))

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

    def to_string(
        self, *, options=None, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs
    ):
        """Convert to CSS."""

        if options is None:
            options = {}

        if options.get("color"):
            return self.to_generic_string(alpha=alpha, precision=precision, fit=fit, **kwargs)

        value = ''
        if options.get("hex") or options.get("names"):
            if alpha is not False and (alpha is True or self._alpha < 1.0):
                h = self._get_hexa(options, precision=precision, fit=fit)
            else:
                h = self._get_hex(options, precision=precision, fit=fit)
            if options.get("hex"):
                value = h
            if options.get("names"):
                length = len(h) - 1
                index = int(length / 4)
                if length in (8, 4) and h[-index:].lower() == ("f" * index):
                    h = h[:-index]
                n = css_names.hex2name(h)
                if n is not None:
                    value = n

        if not value:
            if alpha is not False and (alpha is True or self._alpha < 1.0):
                value = self._get_rgba(options, precision=precision, fit=fit)
            else:
                value = self._get_rgb(options, precision=precision, fit=fit)
        return value

    def _get_rgb(self, options, *, precision=util.DEF_PREC, fit=util.DEF_FIT):
        """Get RGB color."""

        percent = options.get("percent", False)
        comma = options.get("comma", False)

        factor = 100.0 if percent else 255.0

        if percent:
            template = "rgb({}%, {}%, {}%)" if comma else "rgb({}% {}% {}%)"
        else:
            template = "rgb({}, {}, {})" if comma else "rgb({} {} {})"

        coords = self.get_coords(fit=fit, scale=precision)
        return template.format(
            util.fmt_float(coords[0] * factor, precision),
            util.fmt_float(coords[1] * factor, precision),
            util.fmt_float(coords[2] * factor, precision)
        )

    def _get_rgba(self, options, *, precision=util.DEF_PREC, fit=util.DEF_FIT):
        """Get RGB color with alpha channel."""

        percent = options.get("percent", False)
        comma = options.get("comma", False)

        factor = 100.0 if percent else 255.0

        if percent:
            template = "rgba({}%, {}%, {}%, {})" if comma else "rgb({}% {}% {}% / {})"
        else:
            template = "rgba({}, {}, {}, {})" if comma else "rgb({} {} {} / {})"

        coords = self.get_coords(fit=fit, scale=precision)
        return template.format(
            util.fmt_float(coords[0] * factor, precision),
            util.fmt_float(coords[1] * factor, precision),
            util.fmt_float(coords[2] * factor, precision),
            util.fmt_float(self._alpha, max(util.DEF_PREC, precision))
        )

    def _get_hexa(self, options, *, precision=util.DEF_PREC, fit="clip"):
        """Get the RGB color with the alpha channel."""

        hex_upper = options.get("hex_upper", False)
        compress = options.get("compress", False)

        if not fit:
            fit == "clip"

        template = "#{:02x}{:02x}{:02x}{:02x}"
        if hex_upper:
            template = template.upper()

        coords = self.get_coords(fit=fit, scale=precision)
        value = template.format(
            int(util.round_half_up(coords[0] * 255.0)),
            int(util.round_half_up(coords[1] * 255.0)),
            int(util.round_half_up(coords[2] * 255.0)),
            int(util.round_half_up(self._alpha * 255.0))
        )

        if compress:
            m = RE_COMPRESS.match(value)
            if m:
                value = m.expand(r"#\1\2\3\4")
        return value

    def _get_hex(self, options, *, precision=util.DEF_PREC, fit="clip"):
        """Get the `RGB` value."""

        hex_upper = options.get("hex_upper", False)
        compress = options.get("compress", False)

        if not fit:
            fit == "clip"

        template = "#{:02x}{:02x}{:02x}"
        if hex_upper:
            template = template.upper()

        coords = self.get_coords(fit=fit, scale=precision)
        value = template.format(
            int(util.round_half_up(coords[0] * 255.0)),
            int(util.round_half_up(coords[1] * 255.0)),
            int(util.round_half_up(coords[2] * 255.0))
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
    def match(cls, string, start=0, fullmatch=True):
        """Match a CSS color string."""

        channels, end = super().match(string, start, fullmatch)
        if channels is not None:
            return channels, end
        m = cls.MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            if not string[start:start + 5].lower().startswith(('#', 'rgb(', 'rgba(')):
                string = css_names.name2hex(string[m.start(0):m.end(0)])
                if string is not None:
                    return cls.split_channels(string), m.end(0)
            else:
                return cls.split_channels(string[m.start(0):m.end(0)]), m.end(0)
        return None, None
