"""Distance and Delta E."""
from ... import util
from . import distance_euclidean
from . import delta_e_76
from . import delta_e_94
from . import delta_e_cmc
from . import delta_e_2000
from . import delta_e_itp
from . import delta_e_99o
from . import delta_e_jz
from . import delta_e_hyab

SUPPORTED = [
    delta_e_76, delta_e_94, delta_e_cmc, delta_e_2000,
    delta_e_itp, delta_e_99o, delta_e_jz, delta_e_hyab
]


class DeltaEMap(util.Map):
    """
    Immutable delta E mapping.

    This is not required to be used by users but is
    more for internal use to discourage people from
    accidentally altering the base class mapping.
    """

    def __init__(self, values):
        """Delta E mapping."""

        self._d = {value.__name__.split('.')[-1].replace('delta_e_', ''): value.distance for value in values}

    def _error(self):  # pragma: no cover
        """Error message."""

        return util.ERR_MAP_MSG.format(name="DE_MAP")


class Distance:
    """Distance."""

    DE_MAP = DeltaEMap(SUPPORTED)

    def delta_e(self, color, *, method=None, **kwargs):
        """Delta E distance."""

        color = self._handle_color_input(color)
        if method is None:
            method = self.DELTA_E

        algorithm = method.lower()

        try:
            return self.DE_MAP[algorithm](self, color, **kwargs)
        except KeyError:
            raise ValueError("'{}' is not currently a supported distancing algorithm.".format(algorithm))

    def distance(self, color, *, space="lab"):
        """Delta."""

        color = self._handle_color_input(color)
        return distance_euclidean.distance(self, color, space=space)
