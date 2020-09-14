"""Color base."""
from .. import util
from ..util import parse
import re

MATCH = re.compile(
    r"(?xi)color\(\s*([-a-z0-9]+)\s+((?:{float}{sep}){{2}}{float}(?:{asep}(?:{percent}|{float}))?)\s*\)".format(
        **parse.COLOR_PARTS
    )
)


def split_channels(cls, color):
    """Split channels."""

    channels = []
    for i, c in enumerate(parse.RE_CHAN_SPLIT.split(color.strip()), 0):
        if i < cls.NUM_CHANNELS:
            channels.append(float(c))
        elif i == cls.NUM_CHANNELS:
            channels.append(parse.norm_alpha_channel(c))
    if len(channels) == cls.NUM_CHANNELS:
        channels.append(1.0)
    return channels


class _Color:
    """Base color object."""

    DEF_BG = ""
    SPACE = ""
    NUM_CHANNELS = 3

    def __init__(self, color=None):
        """Initialize."""

        self._channel_alpha = 0.0
        self._channels = [0.0] * self.NUM_CHANNELS

    def coords(self):
        """Coordinates."""

        return [util.adjust_precision(c, util.DEF_PREC) for c in self._channels]

    def clone(self):
        """Clone."""

        return self.new(self)

    def convert(self, space):
        """Convert to color space."""

        obj = self.spaces.get(space.lower())
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        result = obj(self)
        result._on_convert()
        return result

    def new(self, value, space=None):
        """Create new color in color space."""

        if space is None:
            space = self.space()

        obj = self.spaces.get(space.lower())
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        return obj(value)

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

    def mutate(self, obj):
        """Update from color."""

        if self is obj:
            self._on_convert()
            return

        if not isinstance(obj, type(self)):
            obj = type(self)(obj)

        for i, value in enumerate(obj._channels):
            self._channels[i] = value
        self._alpha = obj._alpha
        self._on_convert()

    @property
    def alpha(self):
        """Alpha channel."""

        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Adjust alpha."""

        self._alpha = self.tx_channel(-1, value) if isinstance(value, str) else float(value)

    def __str__(self):
        """String."""

        return self.to_string(alpha=True)

    def __repr__(self):
        """Representation."""

        return 'color({} {} / {})'.format(
            self.space(),
            ' '.join([util.fmt_float(c, util.DEF_PREC) for c in self.coords()]),
            util.fmt_float(self._alpha, util.DEF_PREC)
        )

    @classmethod
    def tx_channel(cls, channel, value):
        """Set a non-alpha color channel."""

        raise NotImplementedError("Base _Color class does not implement 'tx_channel' directly.")

    @classmethod
    def match(cls, string, start=0, fullmatch=True):
        """Match a color by string."""

        m = MATCH.match(string, start)
        if m is not None and m.group(1).lower() == cls.space() and (not fullmatch or m.end(0) == len(string)):
            return split_channels(cls, m.group(2)), m.end(0)
        return None, None

    def to_string(
        self, *, alpha=None, precision=util.DEF_PREC, **kwargs
    ):
        """Convert to CSS."""

        coords = self.coords()
        template = "color({} {} {} {} {})" if alpha else "color({} {} {} {})"
        values = [
            util.fmt_float(coords[0], precision),
            util.fmt_float(coords[1], precision),
            util.fmt_float(coords[2], precision)
        ]
        if alpha:
            values.append(util.fmt_float(self._alpha, max(precision, util.DEF_PREC)))

        return template.format(self.space(), *values)
