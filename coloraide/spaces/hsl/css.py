"""HSL class."""
import re
from .. import hsl as base
from ... import parse
from ... import util
from ...util import MutableVector
from typing import Union, Optional, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ...color import Color


class HSL(base.HSL):
    """HSL class."""

    MATCH = re.compile(
        r"""(?xi)
        \bhsla?\(\s*
        (?:
            # Space separated format
            {angle}(?:{space}{percent}){{2}}(?:{slash}(?:{strict_percent}|{float}))? |
            # comma separated format
            {strict_angle}(?:{comma}{strict_percent}){{2}}(?:{comma}(?:{strict_percent}|{strict_float}))?
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

        options = kwargs
        if precision is None:
            precision = parent.PRECISION

        if options.get("color"):
            return super().to_string(parent, alpha=alpha, precision=precision, fit=fit, none=none, **kwargs)

        a = util.no_nan(self.alpha) if not none else self.alpha
        alpha = alpha is not False and (alpha is True or a < 1.0 or util.is_nan(a))
        method = None if not isinstance(fit, str) else fit
        comma = options.get("comma")
        coords = parent.fit(method=method).coords() if fit else self.coords()
        if comma or not none:
            coords = util.no_nans(coords)

        if alpha:
            template = "hsla({}, {}, {}, {})" if comma else "hsl({} {} {} / {})"
            return template.format(
                util.fmt_float(coords[0], precision),
                util.fmt_float(coords[1], precision, self.BOUNDS[1].upper),
                util.fmt_float(coords[2], precision, self.BOUNDS[2].upper),
                util.fmt_float(a, max(util.DEF_PREC, precision))
            )
        else:
            template = "hsl({}, {}, {})" if comma else "hsl({} {} {})"
            return template.format(
                util.fmt_float(coords[0], precision),
                util.fmt_float(coords[1], precision, self.BOUNDS[1].upper),
                util.fmt_float(coords[2], precision, self.BOUNDS[2].upper)
            )

    @classmethod
    def translate_channel(cls, channel: int, value: str) -> float:
        """Translate channel."""

        if channel == 0:
            return parse.norm_angle_channel(value)
        elif channel in (1, 2):
            return parse.norm_percent_channel(value, cls.BOUNDS[channel].upper)
        elif channel == -1:
            return parse.norm_alpha_channel(value)
        else:  # pragma: no cover
            raise ValueError('{} is not a valid channel index'.format(channel))

    @classmethod
    def split_channels(cls, color: str) -> Tuple[MutableVector, float]:
        """Split channels."""

        start = 5 if color[:4].lower() == 'hsla' else 4
        channels = []
        alpha = 1.0
        for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color[start:-1].strip()), 0):
            c = c.lower()
            if i <= 2:
                channels.append(cls.translate_channel(i, c))
            elif i == 3:
                alpha = cls.translate_channel(-1, c)
        return channels, alpha

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
