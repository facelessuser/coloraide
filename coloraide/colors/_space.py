"""Color base."""
from .. import util
from . import _parse as parse
from . import _convert as convert
from . import _delta as delta
from . import _gamut as gamut
from . import _mix as mix

# Technically this form can handle any number of channels as long as any
# extra are thrown away. We only support 6 currently. If we ever support
# colors with more channels, we can bump this.
RE_DEFAULT_MATCH = r"""(?xi)
color\(\s*
(?:({{color_space}})\s+)?
({float}(?:{space}{float}){{{{,6}}}}(?:{slash}(?:{percent}|{float}))?)
\s*\)
""".format(
    **parse.COLOR_PARTS
)


def calc_contrast_ratio(lum1, lum2):
    """Get contrast ratio."""

    return (lum1 + 0.05) / (lum2 + 0.05) if (lum1 > lum2) else (lum2 + 0.05) / (lum1 + 0.05)


def calc_luminance(srgb):
    """Calculate luminance from `srgb` coordinates."""

    lsrgb = convert.lin_srgb(srgb)
    vector = [0.2126, 0.7152, 0.0722]
    return sum([r * v for r, v in zip(lsrgb, vector)])


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


class Space(delta.Delta, gamut.Gamut, mix.Mix):
    """Base color space object."""

    DEF_BG = ""
    SPACE = ""
    NUM_COLOR_CHANNELS = 3
    IS_DEFAULT = False
    CHANNEL_NAMES = frozenset(["alpha"])
    # For matching the default form of `color(space coords+ / alpha)`.
    # Classes should define this if they want to use the default match.
    DEFAULT_MATCH = ""
    # Match pattern variable for classes to override so we can also
    # maintain the default and other alternatives.
    MATCH = ""

    def __init__(self, color=None):
        """Initialize."""

        self.spaces = {}
        self._alpha = 0.0
        self._coords = [0.0] * self.NUM_COLOR_CHANNELS
        if isinstance(color, Space):
            self.spaces = {k: v for k, v in color.spaces.items()}

    def coords(self):
        """Coordinates."""

        return self._coords[:]

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

    def convert(self, space, *, fit=False):
        """Convert to color space."""

        space = space.lower()

        if fit:
            method = None if not isinstance(fit, str) else fit
            if not self.in_gamut(space):
                clone = self.clone()
                clone.fit(space, method=method, in_place=True)
                result = clone.convert(space)
                result._on_convert()
                return result

        obj = self.spaces.get(space)
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        result = obj(self)
        result._on_convert()
        return result

    def _on_convert(self):
        """
        Run after a convert operation.

        Gives us an opportunity to normalize hues and things like that, if we desire.
        """

    def is_achromatic(self):
        """Check if the color is achromatic."""

        return self._is_achromatic(self.coords())

    def luminance(self):
        """Get perceived luminance."""

        return calc_luminance(convert.convert(self.coords(), self.space(), "srgb"))

    def contrast_ratio(self, color):
        """Get contrast ratio."""

        return calc_contrast_ratio(self.luminance(), color.luminance())

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
        self.alpha = obj.alpha
        self._on_convert()
        return self

    @property
    def alpha(self):
        """Alpha channel."""

        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Adjust alpha."""

        self._alpha = util.clamp(
            self.translate_channel(-1, value) if isinstance(value, str) else float(value),
            0.0,
            1.0
        )

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
            util.fmt_float(self.alpha, util.DEF_PREC)
        )

    __str__ = __repr__

    def to_string(
        self, *, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs
    ):
        """Convert to CSS 'color' string: `color(space coords+ / alpha)`."""

        alpha = alpha is not False and (alpha is True or self.alpha < 1.0)

        coords = self.fit_coords(method=fit) if fit else self.coords()
        template = "color({} {} {} {} / {})" if alpha else "color({} {} {} {})"
        values = [
            util.fmt_float(coords[0], precision),
            util.fmt_float(coords[1], precision),
            util.fmt_float(coords[2], precision)
        ]
        if alpha:
            values.append(util.fmt_float(self.alpha, max(precision, util.DEF_PREC)))

        return template.format(self.space(), *values)

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
                (m.group(1) and m.group(1).lower() == cls.space()) or
                (not m.group(1) and cls.IS_DEFAULT)
            ) and (not fullmatch or m.end(0) == len(string))
        ):
            return split_channels(cls, m.group(2)), m.end(0)
        return None, None
