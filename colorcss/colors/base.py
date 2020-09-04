"""Color base."""
from .. import util
from .. import parse
import re


class _Color:
    """Base color object."""

    DEF_BG = ""
    COLORSPACE = ""
    MATCH = re.compile(
        r"""(?xi)
        \[{float}(?:{comma}{float})(?:{comma}{float})\]
        """.format(**parse.COLOR_PARTS)
    )

    def __init__(self, color=None):
        """Initialize."""

        self._c0 = 0.0
        self._c1 = 0.0
        self._c2 = 0.0
        self._c3 = 0.0

    def clone(self):
        """Clone."""

        return type(self)(self)

    @property
    def _alpha(self):
        """Alpha channel."""

        return self._c0

    @_alpha.setter
    def _alpha(self, value):
        """Set alpha channel."""

        self._c0 = util.clamp(value, 0.0, 1.0)

    @classmethod
    def get_colorspace(cls):
        """Get the color space."""

        return cls.COLORSPACE

    def mutate(self, obj):
        """Update from color."""

        if self is obj:
            return

        if not isinstance(obj, type(self)):
            obj = type(self)(obj)

        self._c1 = obj._c1
        self._c2 = obj._c2
        self._c3 = obj._c3
        self._alpha = obj._alpha

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

        return "<{} object; cs='{}' {}>".format(type(self).__name__, self.COLORSPACE, str(self))

    ###################################
    # Override for specific functionality
    ###################################

    @classmethod
    def tx_channel(cls, channel, value):
        """Set a non-alpha color channel."""

        raise NotImplementedError("Base _Color class does not implement 'tx_channel' directly.")

    @classmethod
    def split_channels(cls, color):
        """Split channels."""

        raise NotImplementedError("Base _Color class does not implement 'split_channels' directly.")

    @classmethod
    def match(cls, string, start=0, fullmatch=True):
        """Match a color by string."""

        m = cls.MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            return cls.split_channels(string[m.start(0):m.end(0)]), m.end(0)
        return None, None

    def to_string(
        self, *, alpha=None, scale=util.INF, **kwargs
    ):
        """Convert to CSS."""

        template = "[{}, {}, {}, {}]" if alpha else "[{}, {}, {}]"
        values = [
            util.fmt_float(self._c1, scale),
            util.fmt_float(self._c2, scale),
            util.fmt_float(self._c3, scale)
        ]
        if alpha:
            values.append(util.fmt_float(self._alpha, max(scale, 3)))

        return template.format(*values)
