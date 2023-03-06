# -*- coding: utf-8 -*-
"""Color vision deficiency."""
from __future__ import annotations
from .. import algebra as alg
from ..filters import Filter
from ..types import Vector, Matrix
from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..color import Color

LRGB_TO_LMS = [
    [0.178824041258, 0.4351609057000001, 0.04119349692],
    [0.034556423182, 0.27155382458, 0.038671308360000003],
    [0.000299565576, 0.0018430896, 0.01467086136]
]

INV_LMS_TO_LRGB = [
    [8.094435598032371, -13.050431460496926, 11.672058453917323],
    [-1.0248505586646686, 5.401931309674973, -11.361471490598712],
    [-0.03652974715933318, -0.412162807001268, 69.35132423820858]
]

BRETTEL_PROTAN = (
    [
        [0.0, 4.627488607809662, -35.41631055362253],
        [0.0, 3.16369912676189, -5.399531254059407],
        [0.0, -0.4919422978103762, 69.56383148385383]
    ],
    [
        [0.0, 4.411833935642649, -30.994049850721773],
        [0.0, 3.191003539598621, -5.959441367252518],
        [0.0, -0.4909690600160197, 69.54387406206783]
    ],
    [0.0, 0.016813516536000002, -0.344781556122]
)  # type: tuple[Matrix, Matrix, Vector]

BRETTEL_DEUTAN = (
    [
        [2.0450557159191893, 0.0, -20.214475708994144],
        [1.4791535953911539, 0.0, 1.8372390480560252],
        [-0.22758315411955252, 0.0, 68.34427374597703]
    ],
    [
        [2.118852691482493, 0.0, -23.090149427156845],
        [1.4486070043407802, 0.0, 3.0275592257125172],
        [-0.2252524749624347, 0.0, 68.25345331944283]
    ],
    [-0.016813516536000002, 0.0, 0.6551784438780001]
)  # type: tuple[Matrix, Matrix, Vector]

BRETTEL_TRITAN = (
    [
        [7.3505266759055665, -11.067606609018522, 0.0],
        [-0.3007366379098325, 3.4718683212256796, 0.0],
        [-4.45657862421045, 11.369094948463927, 0.0]
    ],
    [
        [8.070518330868639, -12.435785978616048, 0.0],
        [-1.0015697166361082, 4.8036412011405005, 0.0],
        [-0.1786378557258344, 3.239847528087881, 0.0]
    ],
    [0.344781556122, -0.6551784438780001, 0.0]
)  # type: tuple[Matrix, Matrix, Vector]

VIENOT_PROTAN = [
    [0.1123827612221641, 0.8876172387778365, 1.3877787807814457e-16],
    [0.11238276122216397, 0.8876172387778359, -2.7755575615628914e-17],
    [0.004005768273046939, -0.004005768273046967, 1.0]
]

VIENOT_DEUTAN = [
    [0.29275011427843584, 0.7072498857215648, 1.942890293094024e-16],
    [0.2927501142784355, 0.7072498857215644, -2.7755575615628914e-17],
    [-0.022336587034129083, 0.02233658703412908, 1.0]
]

VIENOT_TRITAN = [
    [1.0, 0.14461224330693645, -0.14461224330693617],
    [3.599551212651875e-17, 0.8592358078045897, 0.1407641921954102],
    [-4.5102810375396984e-17, 0.8592358078045896, 0.14076419219541023]
]

MACHADO_PROTAN = {
    0: [[1.000000, 0.000000, -0.000000], [0.000000, 1.000000, 0.000000], [-0.000000, -0.000000, 1.000000]],
    1: [[0.856167, 0.182038, -0.038205], [0.029342, 0.955115, 0.015544], [-0.002880, -0.001563, 1.004443]],
    2: [[0.734766, 0.334872, -0.069637], [0.051840, 0.919198, 0.028963], [-0.004928, -0.004209, 1.009137]],
    3: [[0.630323, 0.465641, -0.095964], [0.069181, 0.890046, 0.040773], [-0.006308, -0.007724, 1.014032]],
    4: [[0.539009, 0.579343, -0.118352], [0.082546, 0.866121, 0.051332], [-0.007136, -0.011959, 1.019095]],
    5: [[0.458064, 0.679578, -0.137642], [0.092785, 0.846313, 0.060902], [-0.007494, -0.016807, 1.024301]],
    6: [[0.385450, 0.769005, -0.154455], [0.100526, 0.829802, 0.069673], [-0.007442, -0.022190, 1.029632]],
    7: [[0.319627, 0.849633, -0.169261], [0.106241, 0.815969, 0.077790], [-0.007025, -0.028051, 1.035076]],
    8: [[0.259411, 0.923008, -0.182420], [0.110296, 0.804340, 0.085364], [-0.006276, -0.034346, 1.040622]],
    9: [[0.203876, 0.990338, -0.194214], [0.112975, 0.794542, 0.092483], [-0.005222, -0.041043, 1.046265]],
    10: [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]
}  # type: dict[int, Matrix]

MACHADO_DEUTAN = {
    0: [[1.000000, 0.000000, -0.000000], [0.000000, 1.000000, 0.000000], [-0.000000, -0.000000, 1.000000]],
    1: [[0.866435, 0.177704, -0.044139], [0.049567, 0.939063, 0.011370], [-0.003453, 0.007233, 0.996220]],
    2: [[0.760729, 0.319078, -0.079807], [0.090568, 0.889315, 0.020117], [-0.006027, 0.013325, 0.992702]],
    3: [[0.675425, 0.433850, -0.109275], [0.125303, 0.847755, 0.026942], [-0.007950, 0.018572, 0.989378]],
    4: [[0.605511, 0.528560, -0.134071], [0.155318, 0.812366, 0.032316], [-0.009376, 0.023176, 0.986200]],
    5: [[0.547494, 0.607765, -0.155259], [0.181692, 0.781742, 0.036566], [-0.010410, 0.027275, 0.983136]],
    6: [[0.498864, 0.674741, -0.173604], [0.205199, 0.754872, 0.039929], [-0.011131, 0.030969, 0.980162]],
    7: [[0.457771, 0.731899, -0.189670], [0.226409, 0.731012, 0.042579], [-0.011595, 0.034333, 0.977261]],
    8: [[0.422823, 0.781057, -0.203881], [0.245752, 0.709602, 0.044646], [-0.011843, 0.037423, 0.974421]],
    9: [[0.392952, 0.823610, -0.216562], [0.263559, 0.690210, 0.046232], [-0.011910, 0.040281, 0.971630]],
    10: [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],

}  # type: dict[int, Matrix]

MACHADO_TRITAN = {
    0: [[1.000000, 0.000000, -0.000000], [0.000000, 1.000000, 0.000000], [-0.000000, -0.000000, 1.000000]],
    1: [[0.926670, 0.092514, -0.019184], [0.021191, 0.964503, 0.014306], [0.008437, 0.054813, 0.936750]],
    2: [[0.895720, 0.133330, -0.029050], [0.029997, 0.945400, 0.024603], [0.013027, 0.104707, 0.882266]],
    3: [[0.905871, 0.127791, -0.033662], [0.026856, 0.941251, 0.031893], [0.013410, 0.148296, 0.838294]],
    4: [[0.948035, 0.089490, -0.037526], [0.014364, 0.946792, 0.038844], [0.010853, 0.193991, 0.795156]],
    5: [[1.017277, 0.027029, -0.044306], [-0.006113, 0.958479, 0.047634], [0.006379, 0.248708, 0.744913]],
    6: [[1.104996, -0.046633, -0.058363], [-0.032137, 0.971635, 0.060503], [0.001336, 0.317922, 0.680742]],
    7: [[1.193214, -0.109812, -0.083402], [-0.058496, 0.979410, 0.079086], [-0.002346, 0.403492, 0.598854]],
    8: [[1.257728, -0.139648, -0.118081], [-0.078003, 0.975409, 0.102594], [-0.003316, 0.501214, 0.502102]],
    9: [[1.278864, -0.125333, -0.153531], [-0.084748, 0.957674, 0.127074], [-0.000989, 0.601151, 0.399838]],
    10: [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}  # type: dict[int, Matrix]


def brettel(color: Color, severity: float, wings: tuple[Matrix, Matrix, Vector]) -> None:
    """
    Calculate color blindness using Brettel 1997.

    https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.496.7153&rep=rep1&type=pdf

    Probably the only accurate approach for tritanopia, but is more expensive to calculate.
    """

    w1, w2, sep = wings

    # Which side are we on?
    lms_c = alg.dot(LRGB_TO_LMS, color[:-1], dims=alg.D2_D1)
    if alg.dot(lms_c, sep) > 0:
        coords = alg.dot(w2, lms_c, dims=alg.D2_D1)
    else:
        coords = alg.dot(w1, lms_c, dims=alg.D2_D1)

    if severity < 1:
        color[:-1] = [alg.lerp(a, b, severity) for a, b in zip(color[:-1], coords)]
    else:
        color[:-1] = coords


def vienot(color: Color, severity: float, transform: Matrix) -> None:
    """
    Calculate color blindness using the Viénot, Brettel, and Mollon 1999 approach, best for protanopia and deuteranopia.

    Can be used for tritanopia, but will be not be accurate. Based on
    http://vision.psychol.cam.ac.uk/jdmollon/papers/colourmaps.pdf. Tritanopia is inferred from the paper as they do not
    actually go through the logic, the difference is we use LMS red instead of LMS blue.

    Covered here as well: https://ixora.io/projects/colorblindness/color-blindness-simulation-research/. Though they use
    Hunt-Pointer-Estevez transformation, but here they argue that Smith and Pokorny is still probably the way to go:
    https://daltonlens.org/understanding-cvd-simulation/#From-CIE-XYZ-to-LMS.

    Our matrices are precalculated, so all we need to do is dot and go unless we want something lower than severity 1,
    then we interpolate against the original color.
    """

    coords = alg.dot(transform, color[:-1], dims=alg.D2_D1)
    if severity < 1:
        color[:-1] = [alg.lerp(c1, c2, severity) for c1, c2 in zip(color[:-1], coords)]
    else:
        color[:-1] = coords


def machado(color: Color, severity: float, matrices: dict[int, Matrix]) -> None:
    """
    Machado approach to protanopia, deuteranopia, and tritanopia.

    https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html#Reference

    Decent results for protanopia and deuteranopia, but tritanopia is really only an approximation.
    They don't even bother to show tritanopia results.
    """

    # Calculate the approximate severity
    severity *= 10
    severity1 = int(severity)

    # Filter the color according to the severity
    m1 = matrices[severity1]
    coords = alg.dot(m1, color[:-1], dims=alg.D2_D1)

    # If severity was not exact, and it also isn't max severity,
    # let's calculate the next most severity and interpolate
    # between the two results.
    if severity1 != severity and severity1 < 10:
        # Calculate next highest severity
        severity2 = severity1 + 1
        # Calculate the weight
        weight = (severity - severity1)
        # Get the next severity in the list
        m2 = matrices[severity2]

        # It is actually stated that the two matrices should be interpolated,
        # but it ends up being faster just modifying the color on both the high
        # and low matrix and interpolating the color than interpolating the matrix
        # and then applying it to the color. The results are identical as well.
        coords2 = alg.dot(m2, color[:-1], dims=alg.D2_D1)
        coords = [alg.lerp(c1, c2, weight) for c1, c2 in zip(coords, coords2)]

    # Return the altered color
    color[:-1] = coords


class Protan(Filter):
    """Protanopia filter."""

    NAME = "protan"

    ALLOWED_SPACES = ('srgb-linear',)

    BRETTEL = BRETTEL_PROTAN
    VIENOT = VIENOT_PROTAN
    MACHADO = MACHADO_PROTAN

    def __init__(self, severe: str = 'vienot', anomalous: str = 'machado') -> None:
        """Initialize."""

        self.severe = severe
        self.anomalous = anomalous

    def brettel(self, color: Color, severity: float) -> None:
        """Tritanopia vision deficiency using Brettel method."""

        brettel(color, severity, self.BRETTEL)

    def vienot(self, color: Color, severity: float) -> None:
        """Tritanopia vision deficiency using Viénot method."""

        vienot(color, severity, self.VIENOT)

    def machado(self, color: Color, severity: float) -> None:
        """Tritanopia vision deficiency using Machado method."""

        machado(color, severity, self.MACHADO)

    def select_filter(self, method: str) -> Callable[..., None]:
        """Select the best filter."""

        if method == 'brettel':
            return self.brettel
        elif method == 'vienot':
            return self.vienot
        elif method == 'machado':
            return self.machado
        else:
            raise ValueError("Unrecognized CVD filter method '{}'".format(method))

    def get_best_filter(self, method: str | None, max_severity: bool) -> Callable[..., None]:
        """Get the best filter based on the situation."""

        if method is None:
            method = self.severe if max_severity else self.anomalous
        return self.select_filter(method)

    def filter(self, color: Color, amount: float | None = None, **kwargs: Any) -> None:  # noqa: A003
        """Filter the color."""

        method = kwargs.get('method')  # type: str | None
        amount = alg.clamp(1 if amount is None else amount, 0, 1)
        self.get_best_filter(method, amount == 1)(color, amount)


class Deutan(Protan):
    """Deuteranopia filter."""

    NAME = 'deutan'

    BRETTEL = BRETTEL_DEUTAN
    VIENOT = VIENOT_DEUTAN
    MACHADO = MACHADO_DEUTAN


class Tritan(Protan):
    """Deuteranopia filter."""

    NAME = 'tritan'

    BRETTEL = BRETTEL_TRITAN
    VIENOT = VIENOT_TRITAN
    MACHADO = MACHADO_TRITAN

    def __init__(self, severe: str = 'brettel', anomalous: str = 'brettel') -> None:
        """Initialize."""

        super().__init__(severe, anomalous)
