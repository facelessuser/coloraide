"""Color base."""
from .. import util
from ..util import parse
import re

# Technically this form can handle any number of channels as long as any
# extra are thrown away. We only support 6 currently. Even if we supported
# more, we'd still have to cap for performance.
MATCH = re.compile(
    r"""(?xi)
    color\(\s*
    (?:([-a-z0-9]+)\s+)?
    ({float}(?:{space}{float}){{,5}}(?:{slash}(?:{percent}|{float}))?)
    \s*\)
    """.format(
        **parse.COLOR_PARTS
    )
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
        if i and i < cls.NUM_CHANNELS:
            channels.append(float(c))
    if len(channels) < cls.NUM_CHANNELS:
        diff = cls.NUM_CHANNELS - len(channels)
        channels.extend([0.0] * diff)
    channels.append(alpha if alpha is not None else 1.0)
    return channels


class _Color:
    """Base color object."""

    DEF_BG = ""
    SPACE = ""
    NUM_CHANNELS = 3
    IS_DEFAULT = False

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
        if (
            m is not None and
            (
                (m.group(1) and m.group(1).lower() == cls.space()) or
                (not m.group(1) and cls.IS_DEFAULT)
            ) and (not fullmatch or m.end(0) == len(string))
        ):
            return split_channels(cls, m.group(2)), m.end(0)
        return None, None
