"""HSL class."""
import re
from ...colors import hsl as generic
from ... import util
from ... import parse


class _HSL(generic._HSL):
    """HSL class."""

    DEF_BG = "hsl(0 0% 0% / 1)"
    START = re.compile(r'(?i)\bhsla?\(')
    MATCH = re.compile(
        r"""(?xi)
        \bhsla?\(\s*
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

    def to_string(
        self, *, alpha=None, comma=False, scale=util.INF, raw=False, **kwargs
    ):
        """Convert to CSS."""

        if raw:
            return super().to_string(alpha=alpha, scale=scale)

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

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel."""

        if channel == 0:
            return parse.norm_hue_channel(value)
        elif channel == 1:
            return parse.norm_percent_channel(value)
        elif channel == 2:
            return parse.norm_percent_channel(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        start = 5 if color[:4].lower() == 'hsla' else 4
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
