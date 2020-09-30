"""HWB class."""
import re
from ...colors import hwb as generic
from ...colors import _parse as parse
from ... import util


class HWB(generic.HWB):
    """HWB class."""

    DEF_BG = "hwb(0 0% 0% / 1)"
    START = re.compile(r'(?i)\bhwb\(')
    MATCH = re.compile(
        r"""(?xi)
        \bhwb\(\s*
        (?:
            # Space separated format
            {angle}{space}{percent}{space}{percent}(?:{slash}(?:{percent}|{float}))? |
            # comma separated format
            {angle}{comma}{percent}{comma}{percent}(?:{comma}(?:{percent}|{float}))?
        )
        \s*\)
        """.format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

    def to_string(
        self, *, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs
    ):
        """Convert to CSS."""

        options = kwargs
        if options.get("color"):
            return self.to_generic_string(alpha=alpha, precision=precision, fit=fit, **kwargs)

        value = ''
        if alpha is not False and (alpha is True or self._alpha < 1.0):
            value = self._get_hwba(options, precision=precision, fit=fit)
        else:
            value = self._get_hwb(options, precision=precision, fit=fit)
        return value

    def _get_hwb(self, options, *, precision=util.DEF_PREC, fit=util.DEF_FIT):
        """Get RGB color."""

        template = "hwb({}, {}%, {}%)" if options.get("comma") else "hwb({} {}% {}%)"

        coords = self.fit_coords(method=fit) if fit else self.coords()
        return template.format(
            util.fmt_float(coords[0], precision),
            util.fmt_float(coords[1], precision),
            util.fmt_float(coords[2], precision)
        )

    def _get_hwba(self, options, *, precision=util.DEF_PREC, fit=util.DEF_FIT):
        """Get RGB color with alpha channel."""

        template = "hwb({}, {}%, {}%, {})" if options.get("comma") else "hwb({} {}% {}% / {})"

        coords = self.fit_coords(method=fit) if fit else self.coords()
        return template.format(
            util.fmt_float(coords[0], precision),
            util.fmt_float(coords[1], precision),
            util.fmt_float(coords[2], precision),
            util.fmt_float(self._alpha, max(util.DEF_PREC, precision))
        )

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return parse.norm_hue_channel(value)
        elif channel in (1, 2):
            return parse.norm_percent_channel(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        start = 4
        channels = []
        for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
            if i <= 2:
                channels.append(cls.translate_channel(i, c))
            else:
                channels.append(cls.translate_channel(-1, c))
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
