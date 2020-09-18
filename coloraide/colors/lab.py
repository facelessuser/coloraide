"""LAB class."""
from ._base import _Color
from ._tools import _ColorTools, GamutUnbound, GamutBound
from ..util import parse
from ..util import convert
from .. import util


class _LAB(_ColorTools, _Color):
    """LAB class."""

    SPACE = "lab"
    DEF_BG = "color(lab 0 0 0 / 1)"

    _gamut = (
        (GamutBound(0), GamutUnbound(100.0)),  # Technically we could/should clamp the zero side.
        (GamutUnbound(-160), GamutUnbound(160)),  # No limit, but we could impose one +/-160?
        (GamutUnbound(-160), GamutUnbound(160))  # No limit, but we could impose one +/-160?
    )

    def __init__(self, color=DEF_BG):
        """Initialize."""

        super().__init__(color)

        if isinstance(color, _Color):
            self._cl, self._ca, self._cb = convert.convert(color._channels, color.space(), self.space())
            self._alpha = color._alpha
        elif isinstance(color, str):
            values = self.match(color)[0]
            if values is None:
                raise ValueError("'{}' does not appear to be a valid color".format(color))
            self._cl, self._ca, self._cb, self._alpha = values
        elif isinstance(color, (list, tuple)):
            if not (3 <= len(color) <= 4):
                raise ValueError("A list of channel values should be of length 3 or 4.")
            self._cl = color[0]
            self._ca = color[1]
            self._cb = color[2]
            self._alpha = 1.0 if len(color) == 3 else color[3]
        else:
            raise TypeError("Unexpected type '{}' received".format(type(color)))

    def _is_achromatic(self, channels):
        """Is achromatic."""

        l, a, b = self.coords()
        return abs(a) < util.ACHROMATIC_THRESHOLD and abs(b) < util.ACHROMATIC_THRESHOLD

    @property
    def _cl(self):
        """Hue channel."""

        return self._channels[0]

    @_cl.setter
    def _cl(self, value):
        """
        Set hue channel.

        Theoretically, there is no upper bound here. HDR may use much higher.

        TODO: Do we clamp the higher end or not?
        """

        self._channels[0] = value

    @property
    def _ca(self):
        """A on LAB axis."""

        return self._channels[1]

    @_ca.setter
    def _ca(self, value):
        """
        Set A on LAB axis.

        Theoretically unbounded. It is mentioned in the
        specification that generally the range is +/- 160.

        TODO: Should we not clamp this?
        """

        self._channels[1] = value

    @property
    def _cb(self):
        """B on LAB axis."""

        return self._channels[2]

    @_cb.setter
    def _cb(self, value):
        """
        Set B on LAB axis.

        Theoretically unbounded.

        TODO: Should we not clamp this?
        """

        self._channels[2] = value

    def _grayscale(self):
        """Convert to grayscale."""

        self._ca = 0
        self._cb = 0

    def _mix(self, channels1, channels2, factor, factor2=1.0):
        """Blend the color with the given color."""

        self._cl = self._mix_channel(channels1[0], channels2[0], factor, factor2)
        self._ca = self._mix_channel(channels1[1], channels2[1], factor, factor2)
        self._cb = self._mix_channel(channels1[2], channels2[2], factor, factor2)

    @property
    def l(self):
        """L channel."""

        return self._cl

    @l.setter
    def l(self, value):
        """Get true luminance."""

        self._cl = self.tx_channel(0, value) if isinstance(value, str) else float(value)

    @property
    def a(self):
        """A channel."""

        return self._ca

    @a.setter
    def a(self, value):
        """A axis."""

        self._ca = self.tx_channel(1, value) if isinstance(value, str) else float(value)

    @property
    def b(self):
        """B channel."""

        return self._cb

    @b.setter
    def b(self, value):
        """B axis."""

        self._cb = self.tx_channel(2, value) if isinstance(value, str) else float(value)

    @classmethod
    def tx_channel(cls, channel, value):
        """Translate channel string."""

        return float(value) if channel > 0 else parse.norm_alpha_channel(value)

    def to_string(self, *, alpha=None, precision=util.DEF_PREC, fit=util.DEF_FIT, **kwargs):
        """To string."""

        return self.to_generic_string(alpha=alpha, precision=precision, fit=fit)
