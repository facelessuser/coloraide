"""Color base."""
from abc import ABCMeta
from .. import util
from . import _parse

# Technically this form can handle any number of channels as long as any
# extra are thrown away. We only support 6 currently. If we ever support
# colors with more channels, we can bump this.
RE_DEFAULT_MATCH = r"""(?xi)
color\(\s*
(?:({{color_space}})\s+)?
((?:{percent}|{float})(?:{space}(?:{percent}|{float})){{{{,{{channels:d}}}}}}(?:{slash}(?:{percent}|{float}))?)
\s*\)
""".format(
    **_parse.COLOR_PARTS
)


# From CIE 2004 Colorimetry T.3 and T.8
# B from https://en.wikipedia.org/wiki/Standard_illuminant#White_point
WHITES = {
    "A": (0.44758, 0.40745),
    "B": (0.34842, 0.35161),
    "C": (0.31006, 0.31616),
    "D50": (0.34570, 0.35850),  # Use 4 digits like everyone
    "D55": (0.33243, 0.34744),
    "D65": (0.31270, 0.32900),  # Use 4 digits like everyone
    "D75": (0.29903, 0.31488),
    "E": (1 / 3, 1 / 3),
    "F2": (0.37210, 0.37510),
    "F7": (0.31290, 0.32920),
    "F11": (0.38050, 0.37690)
}


class Angle(float):
    """Angle type."""


class Percent(float):
    """Percent type."""


class OptionalPercent(float):
    """Optional percent type."""


class GamutBound(tuple):
    """Bounded gamut value."""


class GamutUnbound(tuple):
    """Unbounded gamut value."""


class Cylindrical:
    """Cylindrical space."""

    @classmethod
    def hue_name(cls):
        """Hue channel name."""

        return "h"

    @classmethod
    def hue_index(cls):  # pragma: no cover
        """Get hue index."""

        return cls.CHANNEL_NAMES.index(cls.hue_name())


class Labish:
    """Lab-ish color spaces."""

    @classmethod
    def labish_names(cls):
        """Return Lab-ish names in the order L a b."""

        return cls.CHANNEL_NAMES[:3]

    @classmethod
    def labish_indexes(cls):  # pragma: no cover
        """Return the index of the Lab-ish channels."""

        names = cls.labish_names()
        return [cls.CHANNEL_NAMES.index(name) for name in names]


class Lchish(Cylindrical):
    """Lch-ish color spaces."""

    @classmethod
    def lchish_names(cls):  # pragma: no cover
        """Return Lch-ish names in the order L c h."""

        return cls.CHANNEL_NAMES[:3]

    @classmethod
    def lchish_indexes(cls):  # pragma: no cover
        """Return the index of the Lab-ish channels."""

        names = cls.lchish_names()
        return [cls.CHANNEL_NAMES.index(name) for name in names]


class BaseSpace(ABCMeta):
    """Ensure on subclass that the subclass has new instances of mappings."""

    def __init__(cls, name, bases, clsdict):
        """Copy mappings on subclass."""

        if len(cls.mro()) > 2:
            cls.CHANNEL_ALIASES = dict(cls.CHANNEL_ALIASES)


class Space(
    metaclass=BaseSpace
):
    """Base color space object."""

    # Color space name
    SPACE = ""
    # Serialized name
    SERIALIZE = None
    # Number of channels
    NUM_COLOR_CHANNELS = 3
    # Channel names
    CHANNEL_NAMES = ("alpha",)
    # Channel aliases
    CHANNEL_ALIASES = {}
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
    WHITE = "D50"

    def __init__(self, color, alpha=None):
        """Initialize."""

        self._alpha = util.NaN
        self._coords = [util.NaN] * self.NUM_COLOR_CHANNELS

        if isinstance(color, Space):
            for index, channel in enumerate(color.coords()):
                self.set(self.CHANNEL_NAMES[index], channel)
            self.alpha = color.alpha
        elif isinstance(color, (list, tuple)):
            if len(color) != self.NUM_COLOR_CHANNELS:  # pragma: no cover
                # Only likely to happen with direct usage internally.
                raise ValueError(
                    "A list of channel values should be at a minimum of {}.".format(self.NUM_COLOR_CHANNELS)
                )
            for index in range(self.NUM_COLOR_CHANNELS):
                self.set(self.CHANNEL_NAMES[index], color[index])
            self.alpha = 1.0 if alpha is None else alpha
        else:  # pragma: no cover
            # Only likely to happen with direct usage internally.
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def __repr__(self):
        """Representation."""

        gamut = self.RANGE
        values = []
        for i, coord in enumerate(self.coords()):
            fmt = util.fmt_percent if isinstance(gamut[i][0], Percent) else util.fmt_float
            values.append(fmt(coord, util.DEF_PREC))

        return 'color({} {} / {})'.format(
            self._serialize()[0],
            ' '.join(values),
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

    @classmethod
    def space(cls):
        """Get the color space."""

        return cls.SPACE

    @classmethod
    def _serialize(cls):
        """Get the serialized name."""

        return (cls.space(),) if cls.SERIALIZE is None else cls.SERIALIZE

    @classmethod
    def white(cls):
        """Get the white color for this color space."""

        return WHITES[cls.WHITE]

    @property
    def alpha(self):
        """Alpha channel."""

        return self._alpha

    @alpha.setter
    def alpha(self, value):
        """Adjust alpha."""

        self._alpha = util.clamp(self._handle_input(value), 0.0, 1.0)

    def set(self, name, value):  # noqa: A003
        """Set the given channel."""

        name = self.CHANNEL_ALIASES.get(name, name)
        if name not in self.CHANNEL_NAMES:
            raise ValueError("'{}' is an invalid channel name".format(name))

        setattr(self, name, value)
        return self

    def get(self, name):
        """Get the given channel's value."""

        name = self.CHANNEL_ALIASES.get(name, name)
        if name not in self.CHANNEL_NAMES:
            raise ValueError("'{}' is an invalid channel name".format(name))
        return getattr(self, name)

    def to_string(
        self, parent, *, alpha=None, precision=None, fit=True, none=False, **kwargs
    ):
        """Convert to CSS 'color' string: `color(space coords+ / alpha)`."""

        if precision is None:
            precision = parent.PRECISION

        a = util.no_nan(self.alpha) if not none else self.alpha
        alpha = alpha is not False and (alpha is True or a < 1.0 or util.is_nan(a))

        method = None if not isinstance(fit, str) else fit
        coords = parent.fit(method=method).coords() if fit else self.coords()
        if not none:
            coords = util.no_nan(coords)
        gamut = self.RANGE
        template = "color({} {} / {})" if alpha else "color({} {})"

        values = []
        for i, coord in enumerate(coords):
            fmt = util.fmt_percent if isinstance(gamut[i][0], Percent) else util.fmt_float
            values.append(fmt(coord, precision))

        if alpha:
            return template.format(
                self._serialize()[0], ' '.join(values), util.fmt_float(a, max(precision, util.DEF_PREC))
            )
        else:
            return template.format(self._serialize()[0], ' '.join(values))

    @classmethod
    def null_adjust(cls, coords, alpha):
        """Process coordinates and adjust any channels to null/NaN if required."""

        return coords, alpha

    @classmethod
    def match(cls, string, start=0, fullmatch=True):
        """Match a color by string."""

        m = cls.DEFAULT_MATCH.match(string, start)
        if (
            m is not None and
            (
                (m.group(1) and m.group(1).lower() in cls._serialize())
            ) and (not fullmatch or m.end(0) == len(string))
        ):

            # Break channels up into a list
            split = _parse.RE_SLASH_SPLIT.split(m.group(2).strip(), maxsplit=1)

            # Get alpha channel
            alpha = _parse.norm_alpha_channel(split[-1].lower()) if len(split) > 1 else 1.0

            # Parse color channels
            channels = []
            for i, c in enumerate(_parse.RE_CHAN_SPLIT.split(split[0]), 0):
                if c and i < cls.NUM_COLOR_CHANNELS:
                    c = c.lower()
                    # If the channel is a percentage, force it to scale from 0 - 100, not 0 - 1.
                    is_percent = isinstance(cls.RANGE[i][0], Percent)

                    # Don't bother restricting anything yet. CSS doesn't have any defined
                    # spaces that use percentages and only percentages anymore.
                    # They may never have spaces again that do this, or they might.
                    # Custom spaces can restrict colors further, if desired, but we do not
                    # desire to restrict further unless forced.
                    # ```
                    # is_optional_percent = isinstance(cls.RANGE[i][0], OptionalPercent)
                    # is_none = c == 'none'
                    # has_percent = c.endswith('%')
                    #
                    # if not is_none:
                    #     if is_percent and not has_percent:
                    #         # We have an invalid percentage channel
                    #         return None, None
                    #     elif (not is_percent and not is_optional_percent) and has_percent:
                    #         # Percents are not allowed for this channel.
                    #         return None, None
                    # ```

                    channels.append(_parse.norm_color_channel(c, not is_percent))

            # Missing channels are filled with `NaN`
            if len(channels) < cls.NUM_COLOR_CHANNELS:
                diff = cls.NUM_COLOR_CHANNELS - len(channels)
                channels.extend([util.NaN] * diff)

            # Apply null adjustments (null hues) if applicable
            return cls.null_adjust(channels, alpha), m.end(0)

        return None, None
