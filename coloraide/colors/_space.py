"""Color base."""
from .. import util
from . import _parse as parse
from . import _convert as convert
from . import _distance as distance
from . import _gamut as gamut
from . import _interpolate as interpolate
from . import _contrast as contrast
from . _range import Percent

# Technically this form can handle any number of channels as long as any
# extra are thrown away. We only support 6 currently. If we ever support
# colors with more channels, we can bump this.
RE_DEFAULT_MATCH = r"""(?xi)
color\(\s*
(?:({{color_space}})\s+)?
((?:{percent}|{float})(?:{space}(?:{percent}|{float})){{{{,6}}}}(?:{slash}(?:{percent}|{float}))?)
\s*\)
""".format(
    **parse.COLOR_PARTS
)


def split_channels(cls, color):
    """Split channels."""

    if color is None:
        color = ""

    channels = []
    color = color.strip()
    split = parse.RE_SLASH_SPLIT.split(color, maxsplit=1)
    alpha = None
    if len(split) > 1:
        alpha = parse.norm_alpha_channel(split[-1])
    for i, c in enumerate(parse.RE_CHAN_SPLIT.split(split[0]), 0):
        if c and i < cls.NUM_COLOR_CHANNELS:
            is_percent = isinstance(cls._range[i][0], Percent)
            channels.append(parse.norm_color_channel(c, not is_percent))
    if len(channels) < cls.NUM_COLOR_CHANNELS:
        diff = cls.NUM_COLOR_CHANNELS - len(channels)
        channels.extend([0.0] * diff)
    channels.append(alpha if alpha is not None else 1.0)
    return cls.null_adjust(channels)


class Space(contrast.Contrast, interpolate.Interpolate, distance.Distance, gamut.Gamut, convert.Convert):
    """Base color space object."""

    # Default color value (black)
    DEF_VALUE = ""
    # Color space name
    SPACE = ""
    # Number of channels
    NUM_COLOR_CHANNELS = 3
    # Channel names
    CHANNEL_NAMES = frozenset(["alpha"])
    # For matching the default form of `color(space coords+ / alpha)`.
    # Classes should define this if they want to use the default match.
    DEFAULT_MATCH = ""
    # Match pattern variable for classes to override so we can also
    # maintain the default and other alternatives.
    MATCH = ""
    # Should this color also be checked in a different color space? Only when set to a string (specifying a color space)
    # will the default gamut checking also check the specified space as well as the current.
    #
    # Gamut checking:
    #   The specified color space will be checked first followed by the original. Assuming the parent color space fits,
    #   the original should fit as well, but there are some cases when a parent color space that is slightly out of
    #   gamut, when evaluated with a threshold, may appear to be in gamut enough, but when checking the original color
    #   space, the values can be greatly out of specification (looking at you HSL).
    GAMUT_CHECK = None
    # White point
    WHITE = convert.WHITES["D50"]

    def __init__(self, color=None):
        """Initialize."""

        self.parent = None
        self._alpha = 0.0
        self._coords = [0.0] * self.NUM_COLOR_CHANNELS
        if isinstance(color, Space):
            self.parent = color.parent

    def __repr__(self):
        """Representation."""

        return 'color({} {} / {})'.format(
            self.space(),
            ' '.join([util.fmt_float(c, util.DEF_PREC) for c in util.no_nan(self.coords())]),
            util.fmt_float(util.no_nan(self.alpha), util.DEF_PREC)
        )

    __str__ = __repr__

    def _handle_input(self, value):
        """Handle numerical input."""

        if not util.is_number(value):
            raise TypeError("Value should be a number not type '{}'".format(type(value)))
        return float(value) if not util.is_nan(value) else value

    def coords(self):
        """Coordinates."""

        return self._coords[:]

    def clone(self):
        """Clone."""

        return self.new(self)

    def new(self, value):
        """Create new color in color space."""

        color = type(self)(value)
        color.parent = self.parent
        return color

    @classmethod
    def space(cls):
        """Get the color space."""

        return cls.SPACE

    @classmethod
    def white(cls):
        """Get the white color for this color space."""

        return cls.WHITE

    @property
    def alpha(self):
        """Alpha channel."""

        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Adjust alpha."""

        self._alpha = util.clamp(self._handle_input(value), 0.0, 1.0)

    def is_nan(self, name):
        """Check if the channel is NaN."""

        return util.is_nan(self.get(name))

    def set(self, name, value):  # noqa: A003
        """Set the given channel."""

        if name not in self.CHANNEL_NAMES:
            raise ValueError("'{}' is an invalid channel name".format(name))

        setattr(self, name, value)
        return self

    def get(self, name):
        """Get the given channel's value."""

        if name not in self.CHANNEL_NAMES:
            raise ValueError("'{}' is an invalid channel name".format(name))
        return getattr(self, name)

    def to_string(
        self, *, alpha=None, precision=None, fit=True, **kwargs
    ):
        """Convert to CSS 'color' string: `color(space coords+ / alpha)`."""

        if precision is None:
            precision = self.parent.PRECISION

        a = util.no_nan(self.alpha)
        alpha = alpha is not False and (alpha is True or a < 1.0)

        coords = util.no_nan(self.fit_coords() if fit else self.coords())
        template = "color({} {} {} {} / {})" if alpha else "color({} {} {} {})"
        values = [
            util.fmt_float(coords[0], precision),
            util.fmt_float(coords[1], precision),
            util.fmt_float(coords[2], precision)
        ]
        if alpha:
            values.append(util.fmt_float(a, max(precision, util.DEF_PREC)))

        return template.format(self.space(), *values)

    @classmethod
    def null_adjust(cls, coords):
        """Process coordinates and adjust any channels to null/NaN if required."""

        return coords

    @classmethod
    def translate_channel(cls, channel, value):
        """Set a non-alpha color channel."""

        raise NotImplementedError("Base 'Space' does not implement 'translate_channel' directly.")

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        raise NotImplementedError("Base 'Space' class does not implement 'translate_channel' directly.")

    @classmethod
    def match(cls, string, start=0, fullmatch=True):
        """Match a color by string."""

        m = cls.DEFAULT_MATCH.match(string, start)
        if (
            m is not None and
            (
                (m.group(1) and m.group(1).lower() == cls.space())
            ) and (not fullmatch or m.end(0) == len(string))
        ):
            return split_channels(cls, m.group(2)), m.end(0)
        return None, None
