"""CIE diagram generator."""
import itertools
import matplotlib.path as mpltpath
import matplotlib.pyplot as plt
import argparse
import matplotlib.patheffects as path_effects
import sys
import copy
import os
import math

sys.path.insert(0, os.getcwd())

try:
    from coloraide_extras.everything import ColorAll
except ImportError:
    from coloraide.everything import ColorAll
from coloraide import util  # noqa: E402
from coloraide.cat import WHITES  # noqa: E402
from coloraide import algebra as alg  # noqa: E402
from coloraide.temperature import ohno_2013  # noqa: E402
from coloraide import cmfs  # noqa: E402
from coloraide import gamut  # noqa: E402

ALL_WHITES = copy.deepcopy(WHITES)
ALL_WHITES['2deg']['D60'] = ColorAll.CS_MAP['aces2065-1'].WHITE

# How dense do we scatter plot the diagram background colors?
RESOLUTION = 800

# Pick some arbitrary labels to display.
labels_1931 = [
    390,
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
]

labels_1960 = [
    420,
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
    680
]

ISOTHERMS = {100000, 10000, 6000, 4000, 3000, 2000, 1500, 1000}


class Color(ColorAll):
    """Custom class for Pointer conversion."""


class SpectralLocus:
    """
    Setup a spline that represents the black body curve.

    Points between steps are approximated, but actual points can always be
    acquired via `exact`.

    For improved accuracy, we split spline data for low temps and high temps
    and assign the number of required data points accordingly.
    """

    def __init__(
        self,
        x,
        y,
        domain
    ) -> None:
        """Initialize."""

        self.spline = alg.interpolate(list(zip(x, y)), method='catrom')
        self.domain = domain

    def scale(self, point):
        """Scale the temperature point to match the range 0 - 1."""

        # Extrapolation
        if point <= self.domain[0]:
            point = (point - self.domain[0]) / (self.domain[-1] - self.domain[0])
        elif point >= self.domain[-1]:
            point = 1.0 + (point - self.domain[-1]) / (self.domain[-1] - self.domain[0])

        # Interpolation
        else:
            a, b = self.domain[0], self.domain[len(self.domain) - 1]
            l = b - a
            point = ((point - a) / l) if l else 0.0
        return point

    def steps(self, steps):
        """Get steps."""

        return tuple(list(i) for i in zip(*self.spline.steps(steps)))

    def __call__(self, wave):
        """Get the uv for the given temp."""

        return self.spline(self.scale(wave))


def get_spline(x, y, steps=100):
    """Get spline."""

    return tuple(list(i) for i in zip(*alg.interpolate(list(zip(x, y)), method='catrom').steps(steps)))


def get_spectral_locus_labels(locus, waves, distance):
    """Get the spectral locus wavelength labels."""

    annotations = []
    for wave in sorted(waves):
        x, y = locus(wave)
        x1, y1 = locus(wave - 0.05)
        x2, y2 = locus(wave + 0.05)
        d1 = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
        d2 = math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2)
        factor = d1 / (d1 + d2)

        diry = (y - y1) > 0
        dirx = (x - x1) > 0
        m1 = -((y - y1) / (x - x1)) ** -1
        m2 = -((y2 - y) / (x2 - x)) ** -1
        m = alg.lerp(m1, m2, factor)

        length = math.sqrt(1.0 + m ** 2)
        dx = 1.0 / length
        dy = m / length

        # Values really close to 700 extend past the normal locus part and cause the orientation to be off,
        # so we force values greater than 695 to orient in sanely.
        x0 = x + dx * (-distance if ((m >= 0 and not dirx) or (m < 0 and dirx and diry)) and wave < 695 else distance)
        y0 = y + dy * (-distance if ((m >= 0 and diry) or (m < 0 and diry)) and wave < 695 else distance)

        rotate = math.degrees(math.atan2(y0 - y, x0 - x)) % 360
        if rotate > 150:
            rotate += 180

        annotations.append([wave, (x, y), (x0, y0), rotate])
    return annotations


class DiagramOptions:
    """
    Diagram options.

    Manage some diagram specifics options.

    - Handle title and axis names.
    - Handle some diagram colors specific to themes.
    """

    def __init__(self, mode="1931", observer='2deg', theme="light", title=""):
        """Initialize."""

        self.observer = cmfs.CIE_1931_2DEG
        self.white = ALL_WHITES['2deg']['D65']
        if observer == '10deg':
            self.white = ALL_WHITES['10deg']['D65']
            self.observer = cmfs.CIE_1964_10DEG
            self.axis_labels = ('CIE u', 'CIE v')
        elif observer != '2deg':
            raise ValueError("Unrecognized 'observer': {}".format(observer))

        if mode not in ('1931', '1960', '1976'):
            raise ValueError("Unrecognized 'mode': {}".format(mode))

        self.chromaticity = ('xy-' + mode) if mode == '1931' else ('uv-' + mode)
        if mode == "1931":
            self.spectral_locus_labels = labels_1931
            self.axis_labels = ('CIE x', 'CIE y')
            if observer == '2deg':
                self.title = "CIE 1931 Chromaticy Diagram - 2˚ Degree Standard Observer"
            else:
                self.title = "CIE 1931 Chromaticy Diagram - 10˚ Degree Standard Observer"
        elif mode == "1976":
            self.spectral_locus_labels = labels_1960
            self.axis_labels = ("CIE u'", "CIE v'")
            if observer == '2deg':
                self.title = "CIE 1976 UCS Chromaticity Diagram - 2˚ Degree Standard Observer"
            else:
                self.title = "CIE 1976 UCS Chromaticity Diagram - 10˚ Degree Standard Observer"
        else:
            self.spectral_locus_labels = labels_1960
            self.axis_labels = ('CIE u', 'CIE v')
            if observer == '2deg':
                self.title = "CIE 1960 UCS Chromaticity Diagram - 2˚ Degree Standard Observer"
            else:
                self.title = "CIE 1960 UCS Chromaticity Diagram - 10˚ Degree Standard Observer"

        self.cct = 'ohno-2013'

        if title:
            self.title = title

        if theme == 'light':
            plt.style.use('seaborn-v0_8-darkgrid')
            self.default_color = "#00000088"
            self.default_colorized_color = "#333333"
            self.locus_label_color = "#00000088"
            self.locus_point_color = "#00000088"
            self.locus_line_color = "#33333388"
        elif theme == 'dark':
            plt.style.use('dark_background')
            self.default_color = "#ffffff"
            self.default_colorized_color = "#333333"
            self.locus_label_color = "#ffffff88"
            self.locus_point_color = "#ffffff"
            self.locus_line_color = "#cccccc88"


def cie_diagram(
    mode="1931", observer="2deg", colorize=True, opacity=1, rgb_spaces=None,
    white_points=None, theme='light', title='', show_labels=True, axis=True,
    show_legend=True, black_body=False, isotherms=False, cct=None, pointer=False
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

    class Color(ColorAll):
        ...

    Color.register([ohno_2013.Ohno2013(opt.observer, opt.white)], overwrite=True)

    xs = []
    ys = []
    wavelength = []
    annotations = []

    # Get points for the spectral locus
    for k, v in opt.observer.items():
        if 360 <= k <= 780:
            # Get the XYZ values in the correct format
            xy = util.xyz_to_xyY(v)[:-1]
            wavelength.append(k)
            x, y = Color.convert_chromaticity('xy-1931', opt.chromaticity, xy)[:-1]
            xs.append(x)
            ys.append(y)

    spectral_locus = SpectralLocus(xs, ys, wavelength)
    annotations = get_spectral_locus_labels(spectral_locus, opt.spectral_locus_labels, 0.04)

    xs, ys = spectral_locus.steps(len(xs) * 3)

    # Draw the bottom purple line
    xs.append(xs[0])
    ys.append(ys[0])
    spaces = []

    # Pointer gamut
    if pointer:
        for p in pointer:
            bounds, color = p.split(':')
            sx = []
            sy = []
            if bounds == 'max':
                pts = gamut.pointer.pointer_gamut_boundary()
                label = 'pointer'
            else:
                l = min(90, max(15, float(bounds)))
                pts = gamut.pointer.pointer_gamut_boundary(l)
                label = 'pointer L*={}'.format(round(l, 2))
            pts.append(pts[0])
            for pt in pts:
                x, y = Color.convert_chromaticity('xy-1931', opt.chromaticity, pt[:-1])[:-1]
                sx.append(x)
                sy.append(y)
            spaces.append(
                (
                    sx,
                    sy,
                    color,
                    label,
                    mpltpath.Path(list(zip(sx, sy)))
                )
            )

    # Calculate RGB triangles if one is specified
    if rgb_spaces:
        temp = Color('srgb', [])
        for space, color in rgb_spaces:
            red = temp.mutate(space, [1, 0, 0]).split_chromaticity(opt.chromaticity)
            green = temp.mutate(space, [0, 1, 0]).split_chromaticity(opt.chromaticity)
            blue = temp.mutate(space, [0, 0, 1]).split_chromaticity(opt.chromaticity)
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
            if path.contains_point(r):
                o = 0.01 if spaces else opacity
                if spaces:
                    for s in spaces:
                        if s[-1].contains_point(r):
                            o = 1
                            break
                px.append(r[0])
                py.append(r[1])
                srgb = Color.chromaticity(
                    'srgb',
                    r,
                    opt.chromaticity,
                    scale=True,
                    scale_space='rec2020-linear',
                    white=opt.white
                ).set('alpha', o)
                c.append(srgb.convert('srgb').to_string(hex=True, fit="clip"))

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
            lx.append(annotate[1][0])
            ly.append(annotate[1][1])
            plt.annotate(
                '{:d}'.format(annotate[0]),
                annotate[2],
                size=8,
                color=opt.locus_label_color,
                rotation=annotate[3],
                rotation_mode="anchor",
                ha='center'
            )

        plt.scatter(
            lx,
            ly,
            marker=".",
            color=opt.locus_point_color if not colorize else opt.default_color,
            zorder=100
        )

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

    # Add any specified white points.
    if white_points:
        wx = []
        wy = []
        annot = []
        for wp in white_points:
            w = ALL_WHITES[observer][wp]
            annot.append(wp)
            xy = Color.convert_chromaticity('xy-1931', opt.chromaticity, w)[:-1]
            wx.append(xy[0])
            wy.append(xy[1])
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
                ha='center',
                zorder=100
            )

    # Add any specified CCT points.
    if cct:
        bx = []
        by = []
        annot = []
        for value in cct:
            temp, duv = [float(v) for v in value.split(':')]
            c = Color.blackbody('xyz-d65', temp, duv, scale=False, method=opt.cct)
            bu, bv = c.split_chromaticity(opt.chromaticity, white=opt.white)[:-1]
            annot.append('({}, {})'.format(round(bu, 4), round(bv, 4)))
            bx.append(bu)
            by.append(bv)
        plt.scatter(
            bx,
            by,
            marker=".",
            color=opt.default_colorized_color if colorize else opt.default_color,
            s=16,
            zorder=100
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
            c = Color.blackbody('xyz-d65', t, scale=False, method=opt.cct)
            bu, bv = c.split_chromaticity(opt.chromaticity, white=opt.white)[:-1]
            uaxis.append(bu)
            vaxis.append(bv)

            if isotherms and kelvin in ISOTHERMS:
                duvx = []
                duvy = []
                duv_range = (-0.03, 0.03) if kelvin < 100000 else (-0.01, 0.01)
                for duv in duv_range:
                    c = Color.blackbody('xyz-d65', kelvin, duv, scale=False, method=opt.cct)
                    bu, bv = c.split_chromaticity(opt.chromaticity, white=opt.white)[:-1]
                    duvx.append(bu)
                    duvy.append(bv)

                bottom = kelvin < 4000
                label = '{}K'.format(kelvin) if kelvin != 100000 else '∞'
                rotate = math.degrees(math.atan2(duvy[-1] - duvy[0], duvx[-1] - duvx[0]))
                label_offset = alg.polar_to_rect(2, rotate + 90)
                offset = duv_range[0 if bottom else 1] / 2
                c = Color.blackbody('xyz-d65', kelvin, offset, scale=False, method=opt.cct)
                bu, bv = c.split_chromaticity(opt.chromaticity, white=opt.white)[:-1]
                ha = 'right' if bottom else 'left'

                plt.annotate(
                    label,
                    [bu, bv],
                    size=6,
                    color=opt.default_colorized_color if colorize else opt.default_color,
                    rotation=rotate,
                    rotation_mode="anchor",
                    textcoords="offset points",
                    xytext=label_offset,
                    ha=ha
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

    # We current only add labels when drawing RGB triangles
    if (rgb_spaces or pointer) and show_legend:
        ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')


def main():
    """Main."""

    parser = argparse.ArgumentParser(prog='diagrams', description='Generate CIE Chromaticity diagrams.')
    parser.add_argument('--diagram', '-d', default='1931', help='Diagram to generate.')
    parser.add_argument('--cmfs', '-c', default="2deg", help="CMFS to use, e.g., '2deg' (default) or '10deg'.")
    parser.add_argument('--white-point', '-w', action='append', help="A white point to plot.")
    parser.add_argument('--cct', '-C', action='append', help="A point specified by 'CCT:Duv'.")
    parser.add_argument(
        '--pointer', '-P', action='append',
        help="Show Pointer gamut by specifying an L* value and a color for the boundary '30:color'. "
             "'max' can be used show the maximum gamut instead of the gamut at a specific lightness 'max:color'."
    )
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
        cct=args.cct,
        pointer=args.pointer
    )

    if args.output:
        plt.savefig(args.output, bbox_inches='tight', transparent=args.transparent, dpi=args.dpi)
    else:
        plt.gcf().set_dpi(args.dpi)
        plt.show()


if __name__ == "__main__":
    sys.exit(main())
