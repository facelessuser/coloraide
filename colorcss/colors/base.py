"""Color base."""
from . import util
from .util import parse


class _Color:
    """Base color object."""

    DEF_BG = ""
    COLORSPACE = ""

    def __init__(self, color=None):
        """Initialize."""

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

    def to_css(self):
        """Convert values to CSS."""

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

        self._alpha = parse.norm_alpha_channel(value) if isinstance(value, str) else float(value)

    @classmethod
    def _split_channels(cls, color):
        """Split channels."""

    @classmethod
    def css_match(cls, string):
        """Match a if CSS color value."""

        return None
