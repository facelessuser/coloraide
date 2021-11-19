"""HWB class."""
import re
from .. import hwb as base
from ... import parse
from ... import util
from ...util import MutableVector
from typing import Union, Optional, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color


class HWB(base.HWB):
    """HWB class."""

    DEF_VALUE = "hwb(0 0% 0% / 1)"
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
            template = "hwb({}, {}, {}, {})" if options.get("comma") else "hwb({} {} {} / {})"
            return template.format(
                util.fmt_float(coords[0], precision),
                util.fmt_percent(coords[1] * 100, precision),
                util.fmt_percent(coords[2] * 100, precision),
                util.fmt_float(self.alpha, max(util.DEF_PREC, precision))
            )
        else:
            template = "hwb({}, {}, {})" if options.get("comma") else "hwb({} {} {})"
            return template.format(
                util.fmt_float(coords[0], precision),
                util.fmt_percent(coords[1] * 100, precision),
                util.fmt_percent(coords[2] * 100, precision)
            )

    @classmethod
    def translate_channel(cls, channel: int, value: str) -> float:
        """Translate channel string."""

        if channel == 0:
            return parse.norm_angle_channel(value)
        elif channel in (1, 2):
            return parse.norm_percent_channel(value, True)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:  # pragma: no cover
            raise ValueError('{} is not a valid channel index'.format(channel))

    @classmethod
    def split_channels(cls, color: str) -> Tuple[MutableVector, float]:
        """Split channels."""

        start = 4
        channels = []
        alpha = 1.0
        for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
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
    ) -> Optional[Tuple[Tuple[MutableVector, float], int]]:
        """Match a CSS color string."""

        match = super().match(string, start, fullmatch)
        if match is not None:
            return match
        m = cls.MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            return cls.split_channels(string[m.start(0):m.end(0)]), m.end(0)
        return None
