"""Distance and Delta E."""
from . import distance_euclidean
from . import delta_e_76  # noqa: F401
from . import delta_e_94  # noqa: F401
from . import delta_e_cmc  # noqa: F401
from . import delta_e_2000  # noqa: F401
from . import delta_e_itp  # noqa: F401


class Distance:
    """Distance."""

    def delta_e(self, color, *, method=None, **kwargs):
        """Delta E distance."""

        color = self._handle_color_input(color)
        if method is None:
            method = self.DELTA_E

        algorithm = method.lower()

        try:
            de = globals()['delta_e_{}'.format(algorithm.replace('-', '_'))]
        except KeyError:
            raise ValueError("'{}' is not currently a supported distancing algorithm.".format(algorithm))

        return de.distance(self, color, **kwargs)

    def distance(self, color, *, space="lab"):
        """Delta."""

        color = self._handle_color_input(color)
        return distance_euclidean.distance(self, color, space=space)
