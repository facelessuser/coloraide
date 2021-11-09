"""Lch class."""
import re
from . import base
from ...spaces import _parse
from ... import util
from ...util import MutableVector
from typing import Union, Optional, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color


class Lch(base.Lch):
    """Lch class."""

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
        self,
        parent: 'Color',
        *,
        alpha: Optional[bool] = None,
        precision: Optional[int] = None,
        fit: Union[str, bool] = True,
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
        method = None if not isinstance(fit, str) else fit
        coords = parent.fit(method=method).coords() if fit else self.coords()
        if not none:
            coords = util.no_nans(coords)

        if alpha:
            template = "lch({}, {}, {}, {})" if options.get("comma") else "lch({} {} {} / {})"
            return template.format(
                util.fmt_percent(coords[0], precision),
                util.fmt_float(coords[1], precision),
                util.fmt_float(coords[2], precision),
                util.fmt_float(a, max(util.DEF_PREC, precision))
            )
        else:
            template = "lch({}, {}, {})" if options.get("comma") else "lch({} {} {})"
            return template.format(
                util.fmt_percent(coords[0], precision),
                util.fmt_float(coords[1], precision),
                util.fmt_float(coords[2], precision)
            )

    @classmethod
    def translate_channel(cls, channel: int, value: str) -> float:
        """Translate channel string."""

        if channel == 0:
            return _parse.norm_percent_channel(value)
        elif channel == 1:
            return _parse.norm_float(value)
        elif channel == 2:
            return _parse.norm_angle_channel(value)
        elif channel == -1:
            return _parse.norm_alpha_channel(value)
        else:  # pragma: no cover
            raise ValueError('{} is not a valid channel index'.format(channel))

    @classmethod
    def split_channels(cls, color: str) -> Tuple[MutableVector, float]:
        """Split channels."""

        start = 4
        channels = []
        alpha = 1.0
        for i, c in enumerate(_parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
            c = c.lower()
            if i <= 2:
                channels.append(cls.translate_channel(i, c))
            elif i == 3:
                alpha = cls.translate_channel(-1, c)
        return cls.null_adjust(channels, alpha)

    @classmethod
    def match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> Tuple[Optional[Tuple[MutableVector, float]], Optional[int]]:
        """Match a CSS color string."""

        channels, end = super().match(string, start, fullmatch)
        if channels is not None:
            return channels, end
        m = cls.MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            return cls.split_channels(string[m.start(0):m.end(0)]), m.end(0)
        return None, None
