"""SRGB color class."""
import re
from . import color_names
from .. import srgb as base
from ... import parse
from ... import util
from typing import Optional, Union, Any, Tuple, TYPE_CHECKING
from ...util import MutableVector

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color

RE_COMPRESS = re.compile(r'(?i)^#({hex})\1({hex})\2({hex})\3(?:({hex})\4)?$'.format(**parse.COLOR_PARTS))


class SRGB(base.SRGB):
    """SRGB class."""

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

    def to_string(
        self,
        parent: 'Color',
        *,
        alpha: Optional[bool] = None,
        precision: Optional[int] = None,
        fit: Union[bool, str] = True,
        none: bool = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS."""

        if precision is None:
            precision = parent.PRECISION

        options = kwargs
        if options.get("color"):
            return super().to_string(parent, alpha=alpha, precision=precision, fit=fit, none=none, **kwargs)

        a = util.no_nan(self.alpha) if not none else self.alpha
        alpha = alpha is not False and (alpha is True or a < 1.0 or util.is_nan(a))
        compress = options.get("compress", False)

        # Handle hex and color names
        value = ''
        if options.get("hex") or options.get("names"):
            h = self._get_hex(parent, upper=options.get("upper", False), alpha=alpha, fit=fit)
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
            coords = parent.fit(method=method).coords() if fit else self.coords()
            if not none:
                coords = util.no_nans(coords)

            fmt = util.fmt_percent if percent else util.fmt_float
            if alpha:
                template = "rgba({}, {}, {}, {})" if comma else "rgb({} {} {} / {})"
                value = template.format(
                    fmt(coords[0] * factor, precision),
                    fmt(coords[1] * factor, precision),
                    fmt(coords[2] * factor, precision),
                    util.fmt_float(a, max(util.DEF_PREC, precision))
                )
            else:
                template = "rgb({}, {}, {})" if comma else "rgb({} {} {})"
                value = template.format(
                    fmt(coords[0] * factor, precision),
                    fmt(coords[1] * factor, precision),
                    fmt(coords[2] * factor, precision),
                )

        return value

    def _get_hex(
        self,
        parent: 'Color',
        *,
        upper: bool = False,
        alpha: bool = False,
        fit: Union[str, bool] = True
    ) -> str:
        """Get the hex `RGB` value."""

        method = None if not isinstance(fit, str) else fit
        coords = util.no_nans(parent.fit(method=method).coords())

        template = "#{:02x}{:02x}{:02x}{:02x}" if alpha else "#{:02x}{:02x}{:02x}"
        if upper:
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
    def translate_channel(cls, channel: int, value: str) -> float:
        """Translate channel string."""

        if channel in (0, 1, 2):
            if value.startswith('#'):
                return parse.norm_hex_channel(value)
            else:
                return parse.norm_rgb_channel(value)
        elif channel == -1:
            if value.startswith('#'):
                return parse.norm_hex_channel(value)
            else:
                return parse.norm_alpha_channel(value)
        else:  # pragma: no cover
            raise ValueError('{} is not a valid channel index'.format(channel))

    @classmethod
    def split_channels(cls, color: str) -> Tuple[MutableVector, float]:
        """Split channels."""

        if color[:3].lower().startswith('rgb'):
            start = 5 if color[:4].lower().startswith('rgba') else 4
            channels = []
            alpha = 1.0
            for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
                c = c.lower()
                if i <= 2:
                    channels.append(cls.translate_channel(i, c))
                elif i == 3:
                    alpha = cls.translate_channel(-1, c)
            return cls.null_adjust(channels, alpha)
        else:
            length = len(color)
            if length in (7, 9):
                return cls.null_adjust(
                    [
                        cls.translate_channel(0, "#" + color[1:3]),
                        cls.translate_channel(1, "#" + color[3:5]),
                        cls.translate_channel(2, "#" + color[5:7])
                    ],
                    cls.translate_channel(-1, "#" + color[7:9]) if length == 9 else 1.0
                )
            else:
                return cls.null_adjust(
                    [
                        cls.translate_channel(0, "#" + color[1] * 2),
                        cls.translate_channel(1, "#" + color[2] * 2),
                        cls.translate_channel(2, "#" + color[3] * 2)
                    ],
                    cls.translate_channel(-1, "#" + color[4] * 2) if length == 5 else 1.0
                )

    @classmethod
    def match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> Optional[Tuple[Tuple[MutableVector, float], int]]:
        """Match a CSS color string."""

        match = super().match(string, start, fullmatch)
        if match is not None:
            return match
        m = cls.MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            string = string[m.start(0):m.end(0)].lower()
            if not string.startswith(('#', 'rgb')):
                value = color_names.name2hex(string)
                if value is not None:
                    return cls.split_channels(value), m.end(0)
            else:
                return cls.split_channels(string), m.end(0)

        return None
