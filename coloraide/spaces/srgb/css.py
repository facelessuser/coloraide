"""SRGB color class."""
import re
from . import color_names
from . import base
from .. import _parse
from ... import util

RE_COMPRESS = re.compile(r'(?i)^#({hex})\1({hex})\2({hex})\3(?:({hex})\4)?$'.format(**_parse.COLOR_PARTS))


class SRGB(base.SRGB):
    """SRGB class."""

    DEF_VALUE = "rgb(0 0 0 / 1)"
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
        """.format(**_parse.COLOR_PARTS)
    )

    HEX_MATCH = re.compile(r"(?i)#(?:({hex}{{6}})({hex}{{2}})?|({hex}{{3}})({hex})?)\b".format(**_parse.COLOR_PARTS))

    def to_string(
        self, parent, *, alpha=None, precision=None, fit=True, **kwargs
    ):
        """Convert to CSS."""

        if precision is None:
            precision = parent.PRECISION

        options = kwargs
        if options.get("color"):
            return super().to_string(parent, alpha=alpha, precision=precision, fit=fit, **kwargs)

        # Handle hex and color names
        value = ''
        a = util.no_nan(self.alpha)
        alpha = alpha is not False and (alpha is True or a < 1.0)
        compress = options.get("compress", False)
        if options.get("hex") or options.get("names"):
            h = self._get_hex(parent, options, alpha=alpha, precision=precision, fit=fit)
            if options.get("hex"):
                value = h
                if compress:
                    m = RE_COMPRESS.match(value)
                    if m:
                        value = m.expand(r"#\1\2\3\4") if alpha else m.expand(r"#\1\2\3")
            if options.get("names"):
                length = len(h) - 1
                index = int(length / 4)
                if length in (8, 4) and h[-index:].lower() == ("f" * index):
                    h = h[:-index]
                n = color_names.hex2name(h)
                if n is not None:
                    value = n

        # Handle normal RGB function format.
        if not value:
            percent = options.get("percent", False)
            comma = options.get("comma", False)
            factor = 100.0 if percent else 255.0
            method = None if not isinstance(fit, str) else fit
            coords = util.no_nan(parent.fit(method=method).coords() if fit else self.coords())

            if alpha:
                if percent:
                    template = "rgba({}%, {}%, {}%, {})" if comma else "rgb({}% {}% {}% / {})"
                else:
                    template = "rgba({}, {}, {}, {})" if comma else "rgb({} {} {} / {})"
                value = template.format(
                    util.fmt_float(coords[0] * factor, precision),
                    util.fmt_float(coords[1] * factor, precision),
                    util.fmt_float(coords[2] * factor, precision),
                    util.fmt_float(a, max(util.DEF_PREC, precision))
                )
            else:
                if percent:
                    template = "rgb({}%, {}%, {}%)" if comma else "rgb({}% {}% {}%)"
                else:
                    template = "rgb({}, {}, {})" if comma else "rgb({} {} {})"
                value = template.format(
                    util.fmt_float(coords[0] * factor, precision),
                    util.fmt_float(coords[1] * factor, precision),
                    util.fmt_float(coords[2] * factor, precision)
                )
        return value

    def _get_hex(self, parent, options, *, alpha=False, precision=None, fit=None):
        """Get the hex `RGB` value."""

        hex_upper = options.get("upper", False)
        method = None if not isinstance(fit, str) else fit
        coords = util.no_nan(parent.fit(method=method).coords())

        template = "#{:02x}{:02x}{:02x}{:02x}" if alpha else "#{:02x}{:02x}{:02x}"
        if hex_upper:
            template = template.upper()

        if alpha:
            value = template.format(
                int(util.round_half_up(coords[0] * 255.0)),
                int(util.round_half_up(coords[1] * 255.0)),
                int(util.round_half_up(coords[2] * 255.0)),
                int(util.round_half_up(util.no_nan(self.alpha) * 255.0))
            )
        else:
            value = template.format(
                int(util.round_half_up(coords[0] * 255.0)),
                int(util.round_half_up(coords[1] * 255.0)),
                int(util.round_half_up(coords[2] * 255.0))
            )
        return value

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel in (0, 1, 2):
            if value.startswith('#'):
                return _parse.norm_hex_channel(value)
            else:
                return _parse.norm_rgb_channel(value)
        elif channel == -1:
            if value.startswith('#'):
                return _parse.norm_hex_channel(value)
            else:
                return _parse.norm_alpha_channel(value)

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        if color[:3].lower().startswith('rgb'):
            start = 5 if color[:4].lower().startswith('rgba') else 4
            channels = []
            alpha = 1.0
            for i, c in enumerate(_parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
                if i <= 2:
                    channels.append(cls.translate_channel(i, c))
                elif i == 3:
                    alpha = cls.translate_channel(-1, c)
            return cls.null_adjust(channels, alpha)
        else:
            m = cls.HEX_MATCH.match(color)
            assert(m is not None)
            if m.group(1):
                return cls.null_adjust(
                    (
                        cls.translate_channel(0, "#" + color[1:3]),
                        cls.translate_channel(1, "#" + color[3:5]),
                        cls.translate_channel(2, "#" + color[5:7])
                    ),
                    cls.translate_channel(-1, "#" + m.group(2)) if m.group(2) else 1.0
                )
            else:
                return cls.null_adjust(
                    (
                        cls.translate_channel(0, "#" + color[1] * 2),
                        cls.translate_channel(1, "#" + color[2] * 2),
                        cls.translate_channel(2, "#" + color[3] * 2)
                    ),
                    cls.translate_channel(-1, "#" + m.group(4) * 2) if m.group(4) else 1.0
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
                string = color_names.name2hex(string[m.start(0):m.end(0)])
                if string is not None:
                    return cls.split_channels(string), m.end(0)
            else:
                return cls.split_channels(string[m.start(0):m.end(0)]), m.end(0)
        return None, None
