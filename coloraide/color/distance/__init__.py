"""Distance and Delta E."""
from . import distance_euclidean
from . import delta_e_76  # noqa: F401
from . import delta_e_94  # noqa: F401
from . import delta_e_cmc  # noqa: F401
from . import delta_e_2000  # noqa: F401
from . import delta_e_itp  # noqa: F401
from . import delta_e_99o  # noqa: F401
from . import delta_e_z  # noqa: F401
from . import delta_e_hyab  # noqa: F401


class Distance:
    """Distance."""

    DE_MAP = {
        '76': delta_e_76.distance,
        '94': delta_e_94.distance,
        'cmc': delta_e_cmc.distance,
        '2000': delta_e_2000.distance,
        'itp': delta_e_itp.distance,
        '99o': delta_e_99o.distance,
        'jz': delta_e_z.distance,
        'hyab': delta_e_hyab.distance
    }

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
