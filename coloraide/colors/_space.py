"""Color base."""
from .. import util
from . import _parse as parse

# Technically this form can handle any number of channels as long as any
# extra are thrown away. We only support 6 currently. If we ever support
# colors with more channels, we can bump this.
RE_GENERIC_MATCH = r"""(?xi)
color\(\s*
(?:({{color_space}})\s+)?
({float}(?:{space}{float}){{{{,6}}}}(?:{slash}(?:{percent}|{float}))?)
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
            channels.append(float(c))
    if len(channels) < cls.NUM_COLOR_CHANNELS:
        diff = cls.NUM_COLOR_CHANNELS - len(channels)
        channels.extend([0.0] * diff)
    channels.append(alpha if alpha is not None else 1.0)
    return channels


class Space:
    """Base color space object."""

    DEF_BG = ""
    SPACE = ""
    NUM_COLOR_CHANNELS = 3
    IS_DEFAULT = False
    CHANNEL_NAMES = frozenset(["alpha"])
    GENERIC_MATCH = ""
    MATCH = ""

    def __init__(self, color=None):
        """Initialize."""

        self.spaces = {}
        self._channel_alpha = 0.0
        self._coords = [0.0] * self.NUM_COLOR_CHANNELS
        if isinstance(color, Space):
            self.spaces = {k: v for k, v in color.spaces.items()}

    def coords(self):
        """Coordinates."""

        return self._coords[:]

    def raw(self):
        """Get all the color data unaltered."""

        return self.coords() + [self.alpha]

    def clone(self):
        """Clone."""

        return self.new(self)

    def new(self, value, space=None):
        """Create new color in color space."""

        if space is None:
            space = self.space()

        obj = self.spaces.get(space.lower())
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        color = obj(value)
        color.spaces = {k: v for k, v in self.spaces.items()}
        return color

    def _on_convert(self):
        """
        Run after a convert operation.

        Gives us an opportunity to normalize hues and things like that, if we desire.
        """

    @property
    def _alpha(self):
        """Alpha channel."""

        return self._channel_alpha

    @_alpha.setter
    def _alpha(self, value):
        """Set alpha channel."""

        self._channel_alpha = util.clamp(value, 0.0, 1.0)

    @classmethod
    def space(cls):
        """Get the color space."""

        return cls.SPACE

    def update(self, obj):
        """Update from color."""

        if self is obj:
            self._on_convert()
            return

        if not isinstance(obj, type(self)):
            obj = type(self)(obj)

        for i, value in enumerate(obj.coords()):
            self._coords[i] = value
        self._alpha = obj._alpha
        self._on_convert()
        return self

    @property
    def alpha(self):
        """Alpha channel."""

        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Adjust alpha."""

        self._alpha = self._tx_channel(-1, value) if isinstance(value, str) else float(value)

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

    def __repr__(self):
        """Representation."""

        return 'color({} {} / {})'.format(
            self.space(),
            ' '.join([util.fmt_float(c, util.DEF_PREC) for c in self.coords()]),
            util.fmt_float(self._alpha, util.DEF_PREC)
        )

    __str__ = __repr__

    @classmethod
    def _tx_channel(cls, channel, value):
        """Set a non-alpha color channel."""

        raise NotImplementedError("Base _Color class does not implement '_tx_channel' directly.")

    @classmethod
    def generic_match(cls, string, start=0, fullmatch=True):
        """Match a color by string using the default, generic format."""

        m = cls.GENERIC_MATCH.match(string, start)
        if (
            m is not None and
            (
                (m.group(1) and m.group(1).lower() == cls.space()) or
                (not m.group(1) and cls.IS_DEFAULT)
            ) and (not fullmatch or m.end(0) == len(string))
        ):
            return split_channels(cls, m.group(2)), m.end(0)
        return None, None

    @classmethod
    def match(cls, string, start=0, fullmatch=True):
        """Match a color by string."""

        return cls.generic_match(string, start, fullmatch)
