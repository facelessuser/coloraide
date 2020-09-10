"""LAB class."""
import re
from ...colors import lab as generic
from ... import util
from ...util import parse


class _LAB(generic._LAB):
    """LAB class."""

    DEF_BG = "lab(0% 0 0 / 1)"
    START = re.compile(r'(?i)\blab\(')
    MATCH = re.compile(
        r"""(?xi)
        \blab\(\s*
        (?:
            # Space separated format
            {percent}{space}{float}{space}{float}(?:{slash}(?:{percent}|{float}))? |
            # comma separated format
            {percent}{comma}{float}{comma}{float}(?:{comma}(?:{percent}|{float}))?
        )
        \s*\)
        """.format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

    def to_string(
        self, *, alpha=None, comma=False, precision=util.DEF_PREC, raw=False, **kwargs
    ):
        """Convert to CSS."""

        if raw:
            return super().to_string(alpha=alpha, precision=precision)

        value = ''
        if alpha is not False and (alpha is True or self._alpha < 1.0):
            value = self._get_laba(comma=comma, precision=precision)
        else:
            value = self._get_lab(comma=comma, precision=precision)
        return value

    def _get_lab(self, *, comma=False, precision=util.DEF_PREC):
        """Get LAB color."""

        template = "lab({}%, {}, {})" if comma else "lab({}% {} {})"

        return template.format(
            util.fmt_float(self._cl, precision),
            util.fmt_float(self._ca, precision),
            util.fmt_float(self._cb, precision)
        )

    def _get_laba(self, *, comma=False, precision=util.DEF_PREC):
        """Get LAB color with alpha channel."""

        template = "lab({}%, {}, {}, {})" if comma else "lab({}% {} {} / {})"

        return template.format(
            util.fmt_float(self._cl, precision),
            util.fmt_float(self._ca, precision),
            util.fmt_float(self._cb, precision),
            util.fmt_float(self._alpha, max(util.DEF_PREC, precision))
        )

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return parse.norm_lab_lightness(value)
        elif channel in (1, 2):
            return float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

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
    def match(cls, string, start=0, fullmatch=True):
        """Match a CSS color string."""

        channels, end = super().match(string, start, fullmatch)
        if channels is not None:
            return channels, end
        m = cls.MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            return cls.split_channels(string[m.start(0):m.end(0)]), m.end(0)
        return None, None
