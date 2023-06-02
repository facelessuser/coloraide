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
from coloraide import temperature as thermal  # noqa: E402
from coloraide import cmfs  # noqa: E402

ALL_WHITES = copy.deepcopy(WHITES)
ALL_WHITES['2deg']['D60'] = Color.CS_MAP['aces2065-1'].WHITE

# How dense do we scatter plot the diagram background colors?
RESOLUTION = 800

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

ISOTHERMS = {
    100000: (0.025, '∞'),
    10000: (0.025, '10000K'),
    6000: (0.025, '6000K'),
    4000: (0.025, '4000K'),
    3000: (-0.040, '3000K'),
    2000: (-0.034, '2000K'),
    1500: (-0.040, '1500K'),
    1000: (-0.040, '1000K')
}


def get_spline(x, y, steps=100):
    """Get spline."""

    return tuple([list(i) for i in zip(*alg.interpolate(list(zip(x, y)), method='monotone').steps(steps))])


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

        self.observer = cmfs.cie_2_deg_observer
        if observer == '10deg':
            self.observer = cmfs.cie_10_deg_observer
            self.axis_labels = ('CIE u', 'CIE v')
        elif observer != '2deg':
            raise ValueError("Unrecognized 'observer': {}".format(observer))

        self.mode = mode
        if mode not in ('1931', '1960', '1976'):
            raise ValueError("Unrecognized 'mode': {}".format(mode))

        if self.mode == "1931":
            self.axis_labels = ('CIE x', 'CIE y')
            if observer == '2deg':
                self.locus_labels = cie_xy_2_deg_offsets
                self.title = "CIE 1931 Chromaticy Diagram - 2˚ Degree Standard Observer"
            else:
                self.locus_labels = cie_xy_10_deg_offsets
                self.title = "CIE 1931 Chromaticy Diagram - 10˚ Degree Standard Observer"
        elif self.mode == "1976":
            self.axis_labels = ("CIE u'", "CIE v'")
            if observer == '2deg':
                self.locus_labels = cie_uv_2_deg_offsets
                self.title = "CIE 1976 UCS Chromaticity Diagram - 2˚ Degree Standard Observer"
            else:
                self.locus_labels = cie_uv_10_deg_offsets
                self.title = "CIE 1976 UCS Chromaticity Diagram - 10˚ Degree Standard Observer"
        else:
            self.axis_labels = ('CIE u', 'CIE v')
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
    show_legend=True, black_body=False, isotherms=False, cct=None
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

    if isotherms:
        black_body = True

    bb = thermal.DEFAULT_BLACK_BODY
    if (black_body or cct) and observer == '10deg':
        bb = thermal.BlackBodyCurve(cmf=opt.observer)

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

    # Add any specified CCT points.
    if cct:
        bx = []
        by = []
        annot = []
        for value in cct:
            temp, duv = [float(v) for v in value.split(':')]
            bu, bv = thermal.temp_to_uv_ohno_2013(temp, duv, blackbody=bb)
            if opt.mode != '1960':
                bu, bv = util.uv_1960_to_xy([bu, bv])
                if opt.mode != '1931':
                    bu, bv = util.xy_to_uv([bu, bv])
            annot.append('({}, {})'.format(round(bu, 4), round(bv, 4)))
            bx.append(bu)
            by.append(bv)
        plt.scatter(
            bx,
            by,
            marker=".",
            color=opt.default_colorized_color if colorize else opt.default_color
        )
        for pt, a in zip(zip(bx, by), annot):
            plt.annotate(
                a,
                pt,
                size=8,
                color=opt.default_colorized_color if colorize else opt.default_color
            )

    # Show the black body (Planckian locus) curve
    # Work in progress.
    if black_body:
        uaxis = []
        vaxis = []
        for kelvin in range(1000, 100001, 250):
            t = kelvin
            bu, bv = thermal.temp_to_uv_ohno_2013(t, blackbody=bb)
            if opt.mode != '1960':
                bu, bv = util.uv_1960_to_xy([bu, bv])
                if opt.mode != '1931':
                    bu, bv = util.xy_to_uv([bu, bv])
            uaxis.append(bu)
            vaxis.append(bv)

            if isotherms and kelvin in ISOTHERMS:
                duvx = []
                duvy = []
                for duv in (-0.02, 0.02) if kelvin < 100000 else (-0.01, 0.01):
                    bu, bv = thermal.temp_to_uv_ohno_2013(kelvin, duv, blackbody=bb)
                    if opt.mode != '1960':
                        bu, bv = util.uv_1960_to_xy([bu, bv])
                        if opt.mode != '1931':
                            bu, bv = util.xy_to_uv([bu, bv])
                    duvx.append(bu)
                    duvy.append(bv)

                offset, label = ISOTHERMS[kelvin]
                bu, bv = thermal.temp_to_uv_ohno_2013(kelvin, offset, blackbody=bb)
                if opt.mode != '1960':
                    bu, bv = util.uv_1960_to_xy([bu, bv])
                    if opt.mode != '1931':
                        bu, bv = util.xy_to_uv([bu, bv])

                plt.annotate(
                    label,
                    [bu, bv],
                    size=6,
                    color=opt.default_colorized_color if colorize else opt.default_color,
                    ha='center'
                )

                plt.plot(
                    duvx,
                    duvy,
                    color=opt.default_colorized_color if colorize else opt.default_color,
                    marker="",
                    linewidth=1,
                    markersize=0,
                    antialiased=True
                )
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
    parser.add_argument('--cct', '-C', action='append', help="A point specified by 'CCT:Duv'.")
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
    parser.add_argument('--isotherms', '-i', action='store_true', help="Show isotherms.")
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
        black_body=args.black_body,
        isotherms=args.isotherms,
        cct=args.cct
    )

    if args.output:
        plt.savefig(args.output, bbox_inches='tight', transparent=args.transparent, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
