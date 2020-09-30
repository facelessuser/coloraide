"""LAB class."""
import re
from ...colors import lab as generic
from ...colors import _parse as parse
from ... import util


class LAB(generic.LAB):
    """LAB class."""

    DEF_BG = "lab(0% 0 0 / 1)"
    START = re.compile(r'(?i)\b(?:lab|gray)\(')
    MATCH = re.compile(
        r"""(?xi)
        (?:
            \blab\(\s*
            (?:
                # Space separated format
                {percent}{space}{float}{space}{float}(?:{slash}(?:{percent}|{float}))? |
                # comma separated format
                {percent}{comma}{float}{comma}{float}(?:{comma}(?:{percent}|{float}))?
            )
            \s*\) |
            # Shorthand for desaturated colors
            \bgray\(\s*
            (?:
               # Space separated format
               {float}(?:{slash}(?:{percent}|{float}))? |
               # comma separated format
               {float}(?:{comma}(?:{percent}|{float}))?
            )
            \s*\)
        )
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
        if options.get("gray") and self.is_achromatic():
            if alpha is not False and (alpha is True or self.alpha < 1.0):
                value = self._get_graya(options, precision=precision, fit=fit)
            else:
                value = self._get_gray(options, precision=precision, fit=fit)
        else:
            if alpha is not False and (alpha is True or self.alpha < 1.0):
                value = self._get_laba(options, precision=precision, fit=fit)
            else:
                value = self._get_lab(options, precision=precision, fit=fit)
        return value

    def _get_lab(self, options, *, precision=util.DEF_PREC, fit=util.DEF_FIT):
        """Get LAB color."""

        template = "lab({}%, {}, {})" if options.get("comma") else "lab({}% {} {})"

        coords = self.fit_coords(method=fit) if fit else self.coords()
        return template.format(
            util.fmt_float(coords[0], precision),
            util.fmt_float(coords[1], precision),
            util.fmt_float(coords[2], precision)
        )

    def _get_laba(self, options, *, precision=util.DEF_PREC, fit=util.DEF_FIT):
        """Get LAB color with alpha channel."""

        template = "lab({}%, {}, {}, {})" if options.get("comma") else "lab({}% {} {} / {})"

        coords = self.fit_coords(method=fit) if fit else self.coords()
        return template.format(
            util.fmt_float(coords[0], precision),
            util.fmt_float(coords[1], precision),
            util.fmt_float(coords[2], precision),
            util.fmt_float(self.alpha, max(util.DEF_PREC, precision))
        )

    def _get_gray(self, options, *, precision=util.DEF_PREC, fit=util.DEF_FIT):
        """Get gray color with alpha."""

        template = "gray({})"

        coords = self.fit_coords(method=fit) if fit else self.coords()
        return template.format(
            util.fmt_float(coords[0], precision)
        )

    def _get_graya(self, options, *, precision=util.DEF_PREC, fit=util.DEF_FIT):
        """Get gray color with alpha."""

        template = "gray({}, {})" if options.get("comma") else "gray({} / {})"

        coords = self.fit_coords(method=fit) if fit else self.coords()
        return template.format(
            util.fmt_float(coords[0], precision),
            util.fmt_float(self.alpha, max(3, precision))
        )

    @classmethod
    def translate_channel(cls, channel, value):
        """Translate channel string."""

        if channel == 0:
            return parse.norm_lab_lightness(value)
        elif channel in (1, 2):
            return float(value)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:
            raise ValueError("Unexpected channel index of '{}'".format(channel))

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        if color[:4].lower().startswith('gray'):
            start = 5
            channels = []
            alpha = None
            for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
                if i == 0:
                    channels.append(cls.translate_channel(i, c))
                else:
                    alpha = cls.translate_channel(-1, c)
            channels.extend([0.0, 0.0])
            channels.append(1.0 if alpha is None else alpha)
        else:
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
