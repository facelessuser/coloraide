"""Lch class."""
import re
from . import base
from ...spaces import _parse
from ... import util


class Lch(base.Lch):
    """Lch class."""

    DEF_VALUE = "lch(0% 0 0 / 1)"
    START = re.compile(r'(?i)\blch\(')
    MATCH = re.compile(
        r"""(?xi)
        \blch\(\s*
        (?:
            # Space separated format
            {percent}{space}{float}{space}{angle}(?:{slash}(?:{percent}|{float}))? |
            # comma separated format
            {percent}{comma}{float}{comma}{angle}(?:{comma}(?:{percent}|{float}))?
        )
        \s*\)
        """.format(**_parse.COLOR_PARTS)
    )

    def to_string(
        self, parent, *, alpha=None, precision=None, fit=True, **kwargs
    ):
        """Convert to CSS."""

        if precision is None:
            precision = parent.PRECISION

        options = kwargs
        if options.get("color"):
            return super().to_string(parent, alpha=alpha, precision=precision, fit=fit, **kwargs)

        a = util.no_nan(self.alpha)
        alpha = alpha is not False and (alpha is True or a < 1.0)
        method = None if not isinstance(fit, str) else fit
        coords = util.no_nan(parent.fit(method=method).coords() if fit else self.coords())

        if alpha:
            template = "lch({}%, {}, {}, {})" if options.get("comma") else "lch({}% {} {} / {})"
            return template.format(
                util.fmt_float(coords[0], precision),
                util.fmt_float(coords[1], precision),
                util.fmt_float(coords[2], precision),
                util.fmt_float(a, max(util.DEF_PREC, precision))
            )
        else:
            template = "lch({}%, {}, {})" if options.get("comma") else "lch({}% {} {})"
            return template.format(
                util.fmt_float(coords[0], precision),
                util.fmt_float(coords[1], precision),
                util.fmt_float(coords[2], precision)
            )

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return _parse.norm_percent_channel(value)
        elif channel == 1:
            return _parse.norm_float(value)
        elif channel == 2:
            return _parse.norm_angle_channel(value)
        elif channel == -1:
            return _parse.norm_alpha_channel(value)

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        start = 4
        channels = []
        alpha = 1.0
        for i, c in enumerate(_parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
            if i <= 2:
                channels.append(cls.translate_channel(i, c))
            elif i == 3:
                alpha = cls.translate_channel(-1, c)
        return cls.null_adjust(channels, alpha)

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
