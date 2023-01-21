"""CIE diagram generator."""
import itertools
import matplotlib.path as mpltpath
import matplotlib.pyplot as plt
import argparse
import matplotlib.patheffects as path_effects
import sys
import copy
import os

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll as Color
except ImportError:
    from coloraide.everything import ColorAll as Color
from coloraide import util  # noqa: E402
from coloraide.cat import WHITES  # noqa: E402
from coloraide import algebra as alg  # noqa: E402

ALL_WHITES = copy.deepcopy(WHITES)
ALL_WHITES['2deg']['D60'] = Color.CS_MAP['aces2065-1'].WHITE

# How dense do we scatter plot the diagram background colors?
RESOLUTION = 800

CCT = [1000, 1500, 2000, 2500, 3000, 6000, 10000, 15000, 20000, 25000]

# CIE 1931 2 degree observer
# http://www-cvrl.ucsd.edu/cmfs.htm
cie_2_deg_observer = {
    360: (0.0001299, 0.000003917, 0.0006061),
    365: (0.0002321, 0.000006965, 0.001086),
    370: (0.0004149, 0.00001239, 0.001946),
    375: (0.0007416, 0.00002202, 0.003486),
    380: (0.001368, 0.000039, 0.006450001),
    385: (0.002236, 0.000064, 0.01054999),
    390: (0.004243, 0.00012, 0.02005001),
    395: (0.00765, 0.000217, 0.03621),
    400: (0.01431, 0.000396, 0.06785001),
    405: (0.02319, 0.00064, 0.1102),
    410: (0.04351, 0.00121, 0.2074),
    415: (0.07763, 0.00218, 0.3713),
    420: (0.13438, 0.004, 0.6456),
    425: (0.21477, 0.0073, 1.0390501),
    430: (0.2839, 0.0116, 1.3856),
    435: (0.3285, 0.01684, 1.62296),
    440: (0.34828, 0.023, 1.74706),
    445: (0.34806, 0.0298, 1.7826),
    450: (0.3362, 0.038, 1.77211),
    455: (0.3187, 0.048, 1.7441),
    460: (0.2908, 0.06, 1.6692),
    465: (0.2511, 0.0739, 1.5281),
    470: (0.19536, 0.09098, 1.28764),
    475: (0.1421, 0.1126, 1.0419),
    480: (0.09564, 0.13902, 0.8129501),
    485: (0.05795001, 0.1693, 0.6162),
    490: (0.03201, 0.20802, 0.46518),
    495: (0.0147, 0.2586, 0.3533),
    500: (0.0049, 0.323, 0.272),
    505: (0.0024, 0.4073, 0.2123),
    510: (0.0093, 0.503, 0.1582),
    515: (0.0291, 0.6082, 0.1117),
    520: (0.06327, 0.71, 0.07824999),
    525: (0.1096, 0.7932, 0.05725001),
    530: (0.1655, 0.862, 0.04216),
    535: (0.2257499, 0.9148501, 0.02984),
    540: (0.2904, 0.954, 0.0203),
    545: (0.3597, 0.9803, 0.0134),
    550: (0.4334499, 0.9949501, 0.008749999),
    555: (0.5120501, 1, 0.005749999),
    560: (0.5945, 0.995, 0.0039),
    565: (0.6784, 0.9786, 0.002749999),
    570: (0.7621, 0.952, 0.0021),
    575: (0.8425, 0.9154, 0.0018),
    580: (0.9163, 0.87, 0.001650001),
    585: (0.9786, 0.8163, 0.0014),
    590: (1.0263, 0.757, 0.0011),
    595: (1.0567, 0.6949, 0.001),
    600: (1.0622, 0.631, 0.0008),
    605: (1.0456, 0.5668, 0.0006),
    610: (1.0026, 0.503, 0.00034),
    615: (0.9384, 0.4412, 0.00024),
    620: (0.8544499, 0.381, 0.00019),
    625: (0.7514, 0.321, 0.0001),
    630: (0.6424, 0.265, 0.00004999999),
    635: (0.5419, 0.217, 0.00003),
    640: (0.4479, 0.175, 0.00002),
    645: (0.3608, 0.1382, 0.00001),
    650: (0.2835, 0.107, 0),
    655: (0.2187, 0.0816, 0),
    660: (0.1649, 0.061, 0),
    665: (0.1212, 0.04458, 0),
    670: (0.0874, 0.032, 0),
    675: (0.0636, 0.0232, 0),
    680: (0.04677, 0.017, 0),
    685: (0.0329, 0.01192, 0),
    690: (0.0227, 0.00821, 0),
    695: (0.01584, 0.005723, 0),
    700: (0.01135916, 0.004102, 0),
    705: (0.008110916, 0.002929, 0),
    710: (0.005790346, 0.002091, 0),
    715: (0.004106457, 0.001484, 0),
    720: (0.002899327, 0.001047, 0),
    725: (0.00204919, 0.00074, 0),
    730: (0.001439971, 0.00052, 0),
    735: (0.0009999493, 0.0003611, 0),
    740: (0.0006900786, 0.0002492, 0),
    745: (0.0004760213, 0.0001719, 0),
    750: (0.0003323011, 0.00012, 0),
    755: (0.0002348261, 0.0000848, 0),
    760: (0.0001661505, 0.00006, 0),
    765: (0.000117413, 0.0000424, 0),
    770: (0.00008307527, 0.00003, 0),
    775: (0.00005870652, 0.0000212, 0),
    780: (0.00004150994, 0.00001499, 0),
    785: (0.00002935326, 0.0000106, 0),
    790: (0.00002067383, 0.0000074657, 0),
    795: (0.00001455977, 0.0000052578, 0),
    800: (0.00001025398, 0.0000037029, 0),
    805: (0.000007221456, 0.0000026078, 0),
    810: (0.000005085868, 0.0000018366, 0),
    815: (0.000003581652, 0.0000012934, 0),
    820: (0.000002522525, 0.00000091093, 0),
    825: (0.000001776509, 0.00000064153, 0),
    830: (0.000001251141, 0.00000045181, 0)
}

# CIE 1931 2 degree observer
# http://www-cvrl.ucsd.edu/cmfs.htm
cie_10_deg_observer = {
    360: (0.0000001222, 0.000000013398, 0.000000535027),
    365: (0.00000091927, 0.00000010065, 0.0000040283),
    370: (0.0000059586, 0.0000006511, 0.0000261437),
    375: (0.000033266, 0.000003625, 0.00014622),
    380: (0.000159952, 0.000017364, 0.000704776),
    385: (0.00066244, 0.00007156, 0.0029278),
    390: (0.0023616, 0.0002534, 0.0104822),
    395: (0.0072423, 0.0007685, 0.032344),
    400: (0.0191097, 0.0020044, 0.0860109),
    405: (0.0434, 0.004509, 0.19712),
    410: (0.084736, 0.008756, 0.389366),
    415: (0.140638, 0.014456, 0.65676),
    420: (0.204492, 0.021391, 0.972542),
    425: (0.264737, 0.029497, 1.2825),
    430: (0.314679, 0.038676, 1.55348),
    435: (0.357719, 0.049602, 1.7985),
    440: (0.383734, 0.062077, 1.96728),
    445: (0.386726, 0.074704, 2.0273),
    450: (0.370702, 0.089456, 1.9948),
    455: (0.342957, 0.106256, 1.9007),
    460: (0.302273, 0.128201, 1.74537),
    465: (0.254085, 0.152761, 1.5549),
    470: (0.195618, 0.18519, 1.31756),
    475: (0.132349, 0.21994, 1.0302),
    480: (0.080507, 0.253589, 0.772125),
    485: (0.041072, 0.297665, 0.5706),
    490: (0.016172, 0.339133, 0.415254),
    495: (0.005132, 0.395379, 0.302356),
    500: (0.003816, 0.460777, 0.218502),
    505: (0.015444, 0.53136, 0.159249),
    510: (0.037465, 0.606741, 0.112044),
    515: (0.071358, 0.68566, 0.082248),
    520: (0.117749, 0.761757, 0.060709),
    525: (0.172953, 0.82333, 0.04305),
    530: (0.236491, 0.875211, 0.030451),
    535: (0.304213, 0.92381, 0.020584),
    540: (0.376772, 0.961988, 0.013676),
    545: (0.451584, 0.9822, 0.007918),
    550: (0.529826, 0.991761, 0.003988),
    555: (0.616053, 0.99911, 0.001091),
    560: (0.705224, 0.99734, 0),
    565: (0.793832, 0.98238, 0),
    570: (0.878655, 0.955552, 0),
    575: (0.951162, 0.915175, 0),
    580: (1.01416, 0.868934, 0),
    585: (1.0743, 0.825623, 0),
    590: (1.11852, 0.777405, 0),
    595: (1.1343, 0.720353, 0),
    600: (1.12399, 0.658341, 0),
    605: (1.0891, 0.593878, 0),
    610: (1.03048, 0.527963, 0),
    615: (0.95074, 0.461834, 0),
    620: (0.856297, 0.398057, 0),
    625: (0.75493, 0.339554, 0),
    630: (0.647467, 0.283493, 0),
    635: (0.53511, 0.228254, 0),
    640: (0.431567, 0.179828, 0),
    645: (0.34369, 0.140211, 0),
    650: (0.268329, 0.107633, 0),
    655: (0.2043, 0.081187, 0),
    660: (0.152568, 0.060281, 0),
    665: (0.11221, 0.044096, 0),
    670: (0.0812606, 0.0318004, 0),
    675: (0.05793, 0.0226017, 0),
    680: (0.0408508, 0.0159051, 0),
    685: (0.028623, 0.0111303, 0),
    690: (0.0199413, 0.0077488, 0),
    695: (0.013842, 0.0053751, 0),
    700: (0.00957688, 0.00371774, 0),
    705: (0.0066052, 0.00256456, 0),
    710: (0.00455263, 0.00176847, 0),
    715: (0.0031447, 0.00122239, 0),
    720: (0.00217496, 0.00084619, 0),
    725: (0.0015057, 0.00058644, 0),
    730: (0.00104476, 0.00040741, 0),
    735: (0.00072745, 0.000284041, 0),
    740: (0.000508258, 0.00019873, 0),
    745: (0.00035638, 0.00013955, 0),
    750: (0.000250969, 0.000098428, 0),
    755: (0.00017773, 0.000069819, 0),
    760: (0.00012639, 0.000049737, 0),
    765: (0.000090151, 0.0000355405, 0),
    770: (0.0000645258, 0.000025486, 0),
    775: (0.000046339, 0.0000183384, 0),
    780: (0.0000334117, 0.000013249, 0),
    785: (0.000024209, 0.0000096196, 0),
    790: (0.0000176115, 0.0000070128, 0),
    795: (0.000012855, 0.0000051298, 0),
    800: (0.00000941363, 0.00000376473, 0),
    805: (0.000006913, 0.00000277081, 0),
    810: (0.00000509347, 0.00000204613, 0),
    815: (0.0000037671, 0.00000151677, 0),
    820: (0.00000279531, 0.00000112809, 0),
    825: (0.000002082, 0.00000084216, 0),
    830: (0.00000155314, 0.0000006297, 0)
}

# Pick some arbitrary labels to display.
labels = {
    380,
    460,
    470,
    480,
    490,
    500,
    510,
    520,
    530,
    540,
    550,
    560,
    570,
    580,
    590,
    600,
    620,
    700
}


def get_spline(x, y, steps=100):
    """Get spline."""

    return tuple([list(i) for i in zip(*alg.interpolate(list(zip(x, y)), method='monotone').steps(steps))])


def black_body_curve_xy(t):
    """
    Calculate the black body curve for `xy` coordinates.

    Good for between 1667K - 25000K.
    """

    if 1667 <= t <= 4000:
        xc = (
            -0.2661239 * (10 ** 9) / (t ** 3) - 0.2343589 * (10 ** 6) / (t ** 2) + 0.8776956 * (10 ** 3) / t + 0.179910
        )
    elif 4000 <= t <= 25000:
        xc = (
            -3.0258469 * (10 ** 9) / (t ** 3) + 2.1070379 * (10 ** 6) / (t ** 2) + 0.2226347 * (10 ** 3) / t + 0.240390
        )
    else:
        raise ValueError('Cannot calculate a color for {:f}k'.format(t))

    if 1667 <= t <= 2222:
        yc = -1.1063814 * (xc ** 3) - 1.34811020 * (xc ** 2) + 2.18555832 * xc - 0.20219683
    elif 2222 <= t <= 4000:
        yc = -0.9549476 * (xc ** 3) - 1.37418593 * (xc ** 2) + 2.09137015 * xc - 0.16748867
    elif 4000 <= t <= 25000:
        yc = 3.0817580 * (xc ** 3) - 5.87338670 * (xc ** 2) + 3.75112997 * xc - 0.37001483

    return xc, yc


def black_body_curve(t, mode='1931'):
    """
    Calculate the black body curve for `uv` coordinates.

    Good for between 1000K - 15000K.
    """

    if t > 15000:
        x, y = black_body_curve_xy(t)
        if mode == '1931':
            return x, y

        u, v = util.xy_to_uv_1960([x, y])
        if mode == '1976':
            return u, v * (3 / 2)

        return u, v

    u = (
        (0.860117757 + 1.54118254 * (10 ** -4) * t + 1.28641212 * (10 ** -7) * (t ** 2)) /
        (1 + 8.42420235 * (10 ** -4) * t + 7.08145163 * (10 ** -7) * (t ** 2))
    )

    v = (
        (0.317398726 + 4.22806245 * (10 ** -5) * t + 4.20481691 * (10 ** -8) * (t ** 2)) /
        (1 - 2.89741816 * (10 ** -5) * t + 1.61456053 * (10 ** -7) * (t ** 2))
    )

    if mode == '1931':
        return util.uv_1960_to_xy([u, v])
    if mode == '1976':
        return u, v * (3 / 2)

    return u, v


def cie_xy_2_deg_offsets(wavelength):
    """
    Setup labels for CIE 2 deg for `xy` diagrams.

    I'm sure there is a more automated way to do this.
    We could calculate slope and calculate a line with
    inverse slope and maybe detect direction and calculate
    needed distance for new point, but this was easy for
    the limited charts we are doing.
    """

    offset = (0, 0)
    if wavelength == 520:
        offset = (-5, 10)
    elif wavelength == 510:
        offset = (-15, 0)
    elif wavelength == 530:
        offset = (5, 12)
    elif wavelength < 490:
        offset = (-15, -8)
    elif wavelength < 500:
        offset = (-15, -5)
    elif wavelength < 520:
        offset = (-15, -3)
    else:
        offset = (15, 5)
    return offset


def cie_xy_10_deg_offsets(wavelength):
    """
    Setup labels for CIE 2 deg for `xy` diagrams.

    I'm sure there is a more automated way to do this.
    We could calculate slope and calculate a line with
    inverse slope and maybe detect direction and calculate
    needed distance for new point, but this was easy for
    the limited charts we are doing.
    """

    offset = (0, 0)
    if wavelength == 520:
        offset = (0, 12)
    elif wavelength == 530:
        offset = (5, 12)
    elif wavelength == 510:
        offset = (-15, 5)
    elif wavelength < 490:
        offset = (-15, -5)
    elif wavelength < 500:
        offset = (-15, -5)
    elif wavelength < 520:
        offset = (-15, -3)
    else:
        offset = (15, 5)
    return offset


def cie_uv_2_deg_offsets(wavelength):
    """
    Setup labels for CIE 2 deg for `uv` diagrams.

    I'm sure there is a more automated way to do this.
    We could calculate slope and calculate a line with
    inverse slope and maybe detect direction and calculate
    needed distance for new point, but this was easy for
    the limited charts we are doing.
    """

    offset = (0, 0)
    if wavelength == 500:
        offset = (-15, -5)
    elif wavelength == 520:
        offset = (-10, 8)
    elif wavelength == 530:
        offset = (-5, 8)
    elif wavelength > 540:
        offset = (3, 8)
    elif wavelength > 520:
        offset = (0, 8)
    elif wavelength == 510:
        offset = (-15, 0)
    elif wavelength == 380:
        offset = (5, -15)
    elif wavelength < 510:
        offset = (-15, -5)
    return offset


def cie_uv_10_deg_offsets(wavelength):
    """
    Setup labels for CIE 2 deg for `uv` diagrams.

    I'm sure there is a more automated way to do this.
    We could calculate slope and calculate a line with
    inverse slope and maybe detect direction and calculate
    needed distance for new point, but this was easy for
    the limited charts we are doing.
    """

    offset = (0, 0)
    if wavelength == 500:
        offset = (-15, 0)
    elif wavelength == 520:
        offset = (-5, 8)
    elif wavelength == 530:
        offset = (-3, 8)
    elif wavelength > 530:
        offset = (0, 8)
    elif wavelength == 510:
        offset = (-15, 8)
    elif wavelength == 380:
        offset = (10, -15)
    elif wavelength < 510:
        offset = (-15, -5)
    return offset


class DiagramOptions:
    """
    Diagram options.

    Manage some diagram specifics options.

    - Handle title and axis names.
    - Handle some diagram colors specific to themes.
    """

    def __init__(self, mode="1931", observer='2deg', theme="light", title=""):
        """Initialize."""

        self.observer = cie_2_deg_observer
        self.axis_labels = ('CIE x', 'CIE y')
        if observer == '10deg':
            self.observer = cie_10_deg_observer
            self.axis_labels = ('CIE u', 'CIE v')
        elif observer != '2deg':
            raise ValueError("Unrecognized 'observer': {}".format(observer))

        self.mode = mode
        if mode not in ('1931', '1960', '1976'):
            raise ValueError("Unrecognized 'mode': {}".format(mode))

        if self.mode == "1931":
            if observer == '2deg':
                self.locus_labels = cie_xy_2_deg_offsets
                self.title = "CIE 1931 Chromaticy Diagram - 2˚ Degree Standard Observer"
            else:
                self.locus_labels = cie_xy_10_deg_offsets
                self.title = "CIE 1931 Chromaticy Diagram - 10˚ Degree Standard Observer"
        elif self.mode == "1976":
            if observer == '2deg':
                self.locus_labels = cie_uv_2_deg_offsets
                self.title = "CIE 1976 UCS Chromaticity Diagram - 2˚ Degree Standard Observer"
            else:
                self.locus_labels = cie_uv_10_deg_offsets
                self.title = "CIE 1976 UCS Chromaticity Diagram - 10˚ Degree Standard Observer"
        else:
            if observer == '2deg':
                self.locus_labels = cie_uv_2_deg_offsets
                self.title = "CIE 1960 UCS Chromaticity Diagram - 2˚ Degree Standard Observer"
            else:
                self.locus_labels = cie_uv_10_deg_offsets
                self.title = "CIE 1960 UCS Chromaticity Diagram - 10˚ Degree Standard Observer"

        if title:
            self.title = title

        if theme == 'light':
            plt.style.use('seaborn-v0_8-darkgrid')
            self.default_color = "#00000088"
            self.default_colorized_color = "#00000088"
            self.locus_label_color = "#00000088"
            self.locus_point_color = "#00000088"
            self.locus_line_color = "#33333388"
        elif theme == 'dark':
            plt.style.use('dark_background')
            self.default_color = "#ffffff"
            self.default_colorized_color = "#00000088"
            self.locus_label_color = "#ffffff88"
            self.locus_point_color = "#ffffff"
            self.locus_line_color = "#cccccc88"


def cie_diagram(
    mode="1931", observer="2deg", colorize=True, opacity=1, rgb_spaces=None,
    white_points=None, theme='light', title='', show_labels=True, axis=True,
    show_legend=True, black_body=False
):
    """CIE diagram."""

    opt = DiagramOptions(theme=theme, mode=mode, observer=observer, title=title)
    figure = plt.figure()
    ax = plt.axes(
        xlabel=opt.axis_labels[0],
        ylabel=opt.axis_labels[1]
    )
    ax.set_aspect('equal')
    if axis is False:
        plt.axis('off')
    figure.add_axes(ax)
    plt.title(opt.title)
    if show_labels:
        plt.margins(0.15)

    xs = []
    ys = []
    annotations = []

    # Get points for the spectral locus
    for k, v in opt.observer.items():
        # Get the XYZ values in the correct format
        x, y = util.xyz_to_xyY(v, (0.31270, 0.32900))[:2]
        if opt.mode == "1976":
            x, y = util.xy_to_uv([x, y])
        elif opt.mode == "1960":
            x, y = util.xy_to_uv_1960([x, y])
        xs.append(x)
        ys.append(y)

        # Prepare annotation labels for all points on the spectral locus.
        if k in labels:
            annotations.append((k, (x, y)))

    xs, ys = get_spline(xs, ys, len(xs) * 3)

    # Draw the bottom purple line
    xs.append(xs[0])
    ys.append(ys[0])

    # Calculate RGB triangles if one is specified
    spaces = []
    if rgb_spaces:
        temp = Color('srgb', [])
        for space, color in rgb_spaces:
            if opt.mode == '1931':
                red = temp.mutate(space, [1, 0, 0]).xy()
                green = temp.mutate(space, [0, 1, 0]).xy()
                blue = temp.mutate(space, [0, 0, 1]).xy()
            elif opt.mode == '1976':
                red = temp.mutate(space, [1, 0, 0]).uv()
                green = temp.mutate(space, [0, 1, 0]).uv()
                blue = temp.mutate(space, [0, 0, 1]).uv()
            else:
                red = temp.mutate(space, [1, 0, 0]).uv('1960')
                green = temp.mutate(space, [0, 1, 0]).uv('1960')
                blue = temp.mutate(space, [0, 0, 1]).uv('1960')
            sx = [red[0], green[0], blue[0], red[0]]
            sy = [red[1], green[1], blue[1], red[1]]
            spaces.append(
                (
                    sx,
                    sy,
                    color,
                    space,
                    mpltpath.Path(list(zip(sx, sy)))
                )
            )

    # Generate fill colors for inside the spectral locus
    if colorize:
        [plt.fill(s[0], s[1], '#888888') for s in spaces]

        px = []
        py = []
        c = []
        path = mpltpath.Path(list(zip(xs, ys)))
        for r in itertools.product(
            (x / RESOLUTION for x in range(0, RESOLUTION + 1)),
            (x / RESOLUTION for x in range(0, RESOLUTION + 1))
        ):
            srgb = Color('srgb', [])
            if path.contains_point(r):
                if opt.mode == "1931":
                    xyz = util.xy_to_xyz(r)
                elif opt.mode == "1976":
                    xyz = util.xy_to_xyz(util.uv_to_xy(r))
                else:
                    xyz = util.xy_to_xyz(util.uv_1960_to_xy(r))
                o = 0.01 if spaces else opacity
                if spaces:
                    for s in spaces:
                        if s[-1].contains_point(r):
                            o = 1
                            break
                px.append(r[0])
                py.append(r[1])
                srgb.update('xyz-d65', xyz, o)
                m = max(srgb[:-1])
                srgb.update('srgb', [(i / m if m != 0 else 0) for i in srgb[:-1]], srgb[-1])
                c.append(srgb.to_string(hex=True, fit="clip"))

        plt.scatter(
            px, py,
            edgecolors=None,
            c=c,
            s=1
        )

    # Plot spectral locus and label it
    plt.plot(
        xs,
        ys,
        color=opt.locus_line_color if colorize else opt.default_color,
        marker="",
        linewidth=1.5,
        markersize=2,
        antialiased=True
    )

    if show_labels:
        # Label points
        lx = []
        ly = []
        for annotate in annotations:
            offset = opt.locus_labels(annotate[0])
            lx.append(annotate[1][0])
            ly.append(annotate[1][1])
            plt.annotate(
                '{:d}'.format(annotate[0]),
                annotate[1],
                size=8,
                color=opt.locus_label_color,
                textcoords="offset points",
                xytext=offset,
                ha='center'
            )
        plt.scatter(
            lx,
            ly,
            marker=".",
            color=opt.locus_point_color if not colorize else opt.default_color,
            zorder=100
        )

    # Add any specified white points.
    if white_points:
        wx = []
        wy = []
        annot = []
        for wp in white_points:
            w = ALL_WHITES[observer][wp]
            annot.append(wp)
            if opt.mode == '1931':
                wx.append(w[0])
                wy.append(w[1])
            elif opt.mode == '1976':
                uv = util.xyz_to_uv(util.xy_to_xyz(w))
                wx.append(uv[0])
                wy.append(uv[1])
            else:
                uv = util.xy_to_uv_1960(w)
                wx.append(uv[0])
                wy.append(uv[1])
        plt.scatter(
            wx,
            wy,
            marker=".",
            color=opt.default_colorized_color if colorize else opt.default_color
        )
        for pt, a in zip(zip(wx, wy), annot):
            plt.annotate(
                a,
                pt,
                size=8,
                color=opt.default_colorized_color if colorize else opt.default_color,
                textcoords="offset points",
                xytext=(15, -3),
                ha='center'
            )

    # Show the black body (Planckian locus) curve
    # Work in progress.
    if black_body:
        uaxis = []
        vaxis = []
        bres = 40
        boffset = 1000
        brange = 24000
        for cct in range(0, bres + 1):
            t = cct / bres * brange + boffset
            bu, bv = black_body_curve(t, opt.mode)
            uaxis.append(bu)
            vaxis.append(bv)
        uaxis, vaxis = get_spline(uaxis, vaxis, len(uaxis) * 4)
        plt.plot(
            uaxis,
            vaxis,
            color=opt.default_colorized_color if colorize else opt.default_color,
            marker="",
            linewidth=1,
            markersize=0,
            antialiased=True
        )
        # `plt.scatter(uaxis, vaxis, c=opt.default_color)`

    # Plot the RGB triangles
    for item in spaces:
        plt.plot(
            item[0],
            item[1],
            marker='o',
            color=item[2],
            label=item[3],
            linewidth=2,
            markersize=0,
            path_effects=[
                path_effects.SimpleLineShadow(alpha=0.2, offset=(1, -1)),
                path_effects.Normal()
            ]
        )

    # We current only add labels when drawing RGB triangles
    if rgb_spaces and show_legend:
        ax.legend()


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='diagrams', description='Generate CIE Chromaticity diagrams.')
    parser.add_argument('--diagram', '-d', default='1931', help='Diagram to generate.')
    parser.add_argument('--cmfs', '-c', default="2deg", help="CMFS to use, e.g., '2deg' (default) or '10deg'.")
    parser.add_argument('--white-point', '-w', action='append', help="A white point to plot.")
    parser.add_argument('--rgb', '-r', action='append', help="An RGB space to show on diagram: 'space:color'.")
    parser.add_argument('--title', '-t', default='', help="Override title with your own.")
    parser.add_argument('--transparent', '-p', action="store_true", help="Export with transparent background.")
    parser.add_argument('--no-axis', '-x', action="store_true", help="Disable display axis.")
    parser.add_argument('--no-legend', '-g', action="store_true", help="Disable legend.")
    parser.add_argument('--no-labels', '-l', action='store_true', help="Disable showing wavelength labels.")
    parser.add_argument('--no-background', '-b', action='store_true', help="Disable diagram color background.")
    parser.add_argument('--no-alpha', '-a', action='store_true', help="Disable diagram transparent background.")
    parser.add_argument('--dark', action="store_true", help="Use dark theme.")
    parser.add_argument('--black-body', '-k', action='store_true', help="Draw the black body curve (WIP).")
    parser.add_argument('--dpi', default=200, type=int, help="DPI of image.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    args = parser.parse_args()

    cie_diagram(
        mode=args.diagram,
        observer=args.cmfs,
        theme='light' if not args.dark else 'dark',
        white_points=args.white_point,
        rgb_spaces=[r.split(':') for r in args.rgb] if args.rgb is not None else None,
        colorize=not args.no_background,
        opacity=0.3 if not args.no_alpha else 1.0,
        show_labels=not args.no_labels,
        show_legend=not args.no_legend,
        axis=not args.no_axis,
        title=args.title,
        black_body=args.black_body
    )

    if args.output:
        plt.savefig(args.output, bbox_inches='tight', transparent=args.transparent, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
