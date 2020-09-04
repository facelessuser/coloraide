"""LCH class."""
import re
from ...colors import lch as generic
from ... import util
from ... import parse


class _LCH(generic._LCH):
    """LCH class."""

    DEF_BG = "lch(0% 0 0 / 1)"
    START = re.compile(r'(?i)(?:lch|gray)\(')
    MATCH = re.compile(
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

    def to_string(
        self, *, alpha=None, comma=False, gray=False, scale=util.INF, raw=False, **kwargs
    ):
        """Convert to CSS."""

        if raw:
            return super().to_string(alpha=alpha, scale=scale)

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

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return parse.norm_lab_lightness(value)
        elif channel == 1:
            return float(value)
        elif channel == 2:
            return parse.norm_hue_channel(value) * 360.0
        elif channel == -1:
            return parse.norm_alpha_channel(value)

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        if color[:4].lower().startswith('gray'):
            start = 5
            channels = []
            alpha = None
            for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
                if i == 0:
                    channels.append(cls.tx_channel(i, c))
                else:
                    channels.append(cls.tx_channel(-1, c))
            channels.extend([0.0, 0.0])
            channels.append(1.0 if alpha is None else alpha)
        else:
            start = 4
            channels = []
            for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
                if i <= 2:
                    channels.append(cls.tx_channel(i, c))
                else:
                    channels.append(cls.tx_channel(-1, c))
            if len(channels) == 3:
                channels.append(1.0)
        return channels

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
            return cls.split_channels(string[m.start(0):m.end(0)]), end if end is not None else m.end(0)
        return None, None
