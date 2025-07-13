"""CIE diagram generator."""
import itertools
import plotly.graph_objects as go
import plotly.io as io
import argparse
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
from coloraide.spaces import Labish

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

        self.spline = alg.interpolate([*zip(x, y)], method='catrom')
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

        return tuple([*i] for i in zip(*self.spline.steps(steps)))

    def __call__(self, wave):
        """Get the uv for the given temp."""

        return self.spline(self.scale(wave))


def get_spline(x, y, steps=100):
    """Get spline."""

    return tuple([*i] for i in zip(*alg.interpolate([*zip(x, y)], method='catrom').steps(steps)))


def convert_chromaticity(xy, opt):
    """Convert chromaticities."""

    if opt.viewed_chromaticity == opt.chromaticity:
        return xy

    color = ColorAll.chromaticity(
        opt.viewed_chromaticity,
        xy,
        opt.chromaticity,
        white=opt.white
    )
    return color[opt.viewed_chromaticity_names[0]], color[opt.viewed_chromaticity_names[1]]


def get_spectral_locus_labels(locus, waves, distance, opt):
    """Get the spectral locus wavelength labels."""

    standard = opt.viewed_chromaticity == opt.chromaticity

    annotations = []
    for wave in sorted(waves):
        x, y = convert_chromaticity(locus(wave), opt)
        x1, y1 = convert_chromaticity(locus(wave - 0.05), opt)
        x2, y2 = convert_chromaticity(locus(wave + 0.05), opt)

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

        noadjust = not standard or wave < 695

        # Values really close to 700 extend past the normal locus part and cause the orientation to be off,
        # so we force values greater than 695 to orient in sanely.
        x0 = x + dx * (-distance if ((m >= 0 and not dirx) or (m < 0 and dirx and diry)) and noadjust else distance)
        y0 = y + dy * (-distance if ((m >= 0 and diry) or (m < 0 and diry)) and noadjust else distance)

        rotate = math.degrees(math.atan2(y0 - y, x0 - x)) % 360
        if rotate > 150:
            rotate += 180
            rotate %= 360

        annotations.append([wave, (x, y), (x0, y0), 0 - rotate])
    return annotations


class Polygon2D:
    """2D Polygon."""

    def __init__(self, x, y):
        """Initialize polygon."""

        self.x = [*x]
        self.y = [*y]
        self.xmin = min(self.x)
        self.xmax = max(self.x)
        self.ymin = min(self.y)
        self.ymax = max(self.y)
        self.length = len(x)

    def contains(self, p):
        """
        Test if point is within polygon using winding number algorithm.

        A bounding box is precalculated to test against before testing any ray crossings.

        This algorithm is generally defined by Dan Sunday via:
        https://web.archive.org/web/20130126163405/http://geomalgorithms.com/a03-_inclusion.html

        Copyright 2000 softSurfer, 2012 Dan Sunday
        This code may be freely used and modified for any purpose
        providing that this copyright notice is included with it.
        SoftSurfer makes no warranty for this code, and cannot be held
        liable for any real or imagined damage resulting from its use.
        Users of this code must verify correctness for their application.

        """

        px, py = p
        # If point is outside the the bounding box, it is not in the 2D polygon.
        if px > self.xmax or px < self.xmin or py > self.ymax or py < self.ymin:
            return False

        winding = 0
        for i in range(1, self.length):
            # Get the previous and and current vertex
            j = i - 1
            ax, ay = self.x[j], self.y[j]
            bx, by = self.x[i], self.y[i]

            if ay <= py:
                if by > py and ((bx - ax) * (py - ay) - (px - ax) * (by - ay)) > 0:
                    winding += 1
            elif by <= py and ((bx - ax) * (py - ay) - (px - ax) * (by - ay)) < 0:
                winding -= 1
        return winding != 0


class DiagramOptions:
    """
    Diagram options.

    Manage some diagram specifics options.

    - Handle title and axis names.
    - Handle some diagram colors specific to themes.
    """

    def __init__(self, mode="1931", observer='2deg', title=""):
        """Initialize."""

        self.observer = cmfs.CIE_1931_2DEG
        self.white = ALL_WHITES['2deg']['D65']
        if observer == '10deg':
            self.white = ALL_WHITES['10deg']['D65']
            self.observer = cmfs.CIE_1964_10DEG
            self.axis_labels = ('CIE u', 'CIE v')
        elif observer != '2deg':
            raise ValueError(f"Unrecognized 'observer': {observer}")

        self.viewed_chromaticity = None
        if mode not in ('1931', '1960', '1976'):
            if ColorAll.CS_MAP.get(mode):
                cs = ColorAll.CS_MAP[mode]
                if isinstance(ColorAll.CS_MAP[mode], Labish):
                    self.chromaticity = 'xy-1931'
                    self.viewed_chromaticity = mode
                    self.viewed_chromaticity_names = cs.names()[1:]
            if self.viewed_chromaticity is None:
                raise ValueError(f"Unrecognized 'mode': {mode}")
        else:
            if self.viewed_chromaticity is None:
                self.chromaticity = ('xy-' + mode) if mode == '1931' else ('uv-' + mode)
            else:
                self.chromaticity = ('xy-1931')
            self.viewed_chromaticity = self.chromaticity

        self.mode = mode
        if mode == "1931":
            self.spectral_locus_labels = labels_1931
            self.axis_labels = ('CIE x', 'CIE y')
            if observer == '2deg':
                self.title = "CIE 1931 Chromaticy Diagram - 2˚ Degree Standard Observer"
            else:
                self.title = "CIE 1931 Chromaticy Diagram - 10˚ Degree Standard Observer"
            self.label_distance = 0.04
        elif mode == "1976":
            self.spectral_locus_labels = labels_1960
            self.axis_labels = ("CIE u'", "CIE v'")
            if observer == '2deg':
                self.title = "CIE 1976 UCS Chromaticity Diagram - 2˚ Degree Standard Observer"
            else:
                self.title = "CIE 1976 UCS Chromaticity Diagram - 10˚ Degree Standard Observer"
            self.label_distance = 0.03
        elif mode == '1960':
            self.spectral_locus_labels = labels_1960
            self.axis_labels = ('CIE u', 'CIE v')
            if observer == '2deg':
                self.title = "CIE 1960 UCS Chromaticity Diagram - 2˚ Degree Standard Observer"
            else:
                self.title = "CIE 1960 UCS Chromaticity Diagram - 10˚ Degree Standard Observer"
            self.label_distance = 0.02
        else:
            self.spectral_locus_labels = labels_1960
            self.axis_labels = self.viewed_chromaticity_names
            if observer == '2deg':
                self.title = f"CIE {mode} Chromaticity Diagram - 2˚ Degree Standard Observer"
            else:
                self.title = f"CIE {mode} Diagram - 10˚ Degree Standard Observer"
            self.label_distance = 0.05

        self.cct = 'ohno-2013'

        if title:
            self.title = title

        self.default_color = "#000000"
        self.default_colorized_color = "#333333"
        self.locus_label_color = "#000000"
        self.locus_point_color = "#000000"
        self.locus_line_color = "#333333"


def cie_diagram(
    mode="1931", observer="2deg", colorize=True, opacity=1, rgb_spaces=None,
    white_points=None, title='', show_labels=True, axis=True,
    show_legend=True, overlay_legend=True, black_body=False, isotherms=False, cct=None, pointer=False,
    height=600, width=800
):
    """CIE diagram."""

    opt = DiagramOptions(mode=mode, observer=observer, title=title)

    fig = go.Figure(
        layout={
            'title': opt.title,
            'xaxis_title': {'text': opt.axis_labels[0]},
            'yaxis_title': {'text': opt.axis_labels[1]},
            'xaxis_scaleanchor': "y",
            'height': height,
            'width': width
        }
    )

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
    annotations = get_spectral_locus_labels(spectral_locus, opt.spectral_locus_labels, opt.label_distance, opt)

    xs, ys = spectral_locus.steps(len(xs) * 2)

    # Draw the bottom purple line
    interp = alg.interpolate([[xs[-1], ys[-1]], [xs[0], ys[0]]])
    xi, yi = zip(*[interp(i / 50) for i in range(1, 51)])
    xs.extend(xi)
    ys.extend(yi)

    spaces = []

    # Pointer gamut
    if pointer:
        for p in pointer:
            bounds, color = p.split(':')
            sx = []
            sy = []
            xy = []
            if bounds == 'max':
                pts = gamut.pointer.pointer_gamut_boundary()
                label = 'pointer'
            else:
                l = min(90, max(15, float(bounds)))
                pts = gamut.pointer.pointer_gamut_boundary(l)
                label = f'pointer L*={round(l, 2)}'
            pts.append(pts[0])
            for pt in pts:
                x, y = Color.convert_chromaticity('xy-1931', opt.chromaticity, pt[:-1])[:-1]
                if sx:
                    interp = alg.interpolate([[sx[-1], sy[-1]], [x, y]])
                    _sx, _sy = zip(*[interp(i / 50) for i in range(1, 51)])
                    sx.extend(_sx)
                    sy.extend(_sy)
                    xy.extend([convert_chromaticity((a, b), opt) for a, b in zip(_sx, _sy)])
                else:
                    sx.append(x)
                    sy.append(y)
                    xy.append(convert_chromaticity((x, y), opt))

            _x, _y = zip(*xy)
            spaces.append(
                (
                    sx,
                    sy,
                    color,
                    label,
                    Polygon2D(sx, sy),
                    _x,
                    _y
                )
            )

    # Calculate RGB triangles if one is specified
    if rgb_spaces:
        temp = Color('srgb', [])
        for space, color in rgb_spaces:
            red = temp.mutate(space, [1, 0, 0]).split_chromaticity(opt.chromaticity)
            green = temp.mutate(space, [0, 1, 0]).split_chromaticity(opt.chromaticity)
            blue = temp.mutate(space, [0, 0, 1]).split_chromaticity(opt.chromaticity)
            interp = alg.interpolate([red[:-1], green[:-1]])
            sxy = [interp(i / 50) for i in range(51)]
            interp = alg.interpolate([green[:-1], blue[:-1]])
            sxy.extend([interp(i / 50) for i in range(1, 51)])
            interp = alg.interpolate([blue[:-1], red[:-1]])
            sxy.extend([interp(i / 50) for i in range(1, 51)])
            sx, sy = zip(*sxy)
            xy = [*zip(*[convert_chromaticity((a, b), opt) for a, b in zip(sx, sy)])]
            spaces.append(
                (
                    sx,
                    sy,
                    color,
                    space,
                    Polygon2D(sx, sy),
                    xy[0],
                    xy[1]
                )
            )

    # Generate fill colors for inside the spectral locus
    if colorize:
        px = []
        py = []
        c = []
        cx = []
        cy = []
        cc = []
        poly = Polygon2D(xs, ys)
        min_range_x = float('inf')
        min_range_y = float('inf')
        max_range_x = float('-inf')
        max_range_y = float('-inf')
        for s in spaces:
            if s[4].xmin < min_range_x:
                min_range_x = s[4].xmin
            if s[4].xmax > max_range_x:
                max_range_x = s[4].xmax
            if s[4].ymin < min_range_y:
                min_range_y = s[4].ymin
            if s[4].ymax > max_range_y:
                max_range_y = s[4].ymax

        for r in itertools.product(
            alg.linspace(min(0, min_range_x), max(1, max_range_x), RESOLUTION, endpoint=True),
            alg.linspace(min(0, min_range_y), max(1, max_range_y), RESOLUTION, endpoint=True)
        ):
            in_space = False
            if spaces:
                for s in spaces:
                    if s[4].contains(r):
                        in_space = True
                        break

            if poly.contains(r):
                xy = convert_chromaticity(r, opt)
                if in_space:
                    cx.append(xy[0])
                    cy.append(xy[1])
                else:
                    px.append(xy[0])
                    py.append(xy[1])

                srgb = Color.chromaticity(
                    'srgb',
                    r,
                    opt.chromaticity,
                    scale=True,
                    scale_space='rec2020-linear',
                    white=opt.white
                )
                if in_space:
                    cc.append(srgb.convert('srgb').to_string(hex=True, fit="clip"))
                else:
                    c.append(srgb.convert('srgb').to_string(hex=True, fit="clip"))
            elif in_space:
                xy = convert_chromaticity(r, opt)
                cx.append(xy[0])
                cy.append(xy[1])
                cc.append('#888888')

        # Visible spectrum fill
        fig.add_traces(data=go.Scatter(
            x=px,
            y=py,
            mode='markers',
            marker={'color': c, 'size': 2, 'symbol': 'circle'},
            showlegend=False,
            opacity=0.3 if spaces else opacity
        ))

        # Color space fill
        if cc:
            fig.add_traces(data=go.Scatter(
                x=cx,
                y=cy,
                mode='markers',
                marker={'color': cc, 'size': 2, 'symbol': 'circle'},
                showlegend=False
            ))

    for i in range(len(xs)):
        xs[i], ys[i] = convert_chromaticity((xs[i], ys[i]), opt)

    fig.add_traces(data=go.Scatter(
        x=xs,
        y=ys,
        mode='lines',
        line={'color': opt.locus_line_color if colorize else opt.default_color, 'width': 2},
        showlegend=False,
        opacity=0.5
    ))

    if show_labels:
        # Label points
        lx = []
        ly = []
        for annotate in annotations:
            lx.append(annotate[1][0])
            ly.append(annotate[1][1])
            fig.add_annotation(
                text=f'{annotate[0]:d}',
                x=annotate[2][0],
                y=annotate[2][1],
                textangle=annotate[3],
                font={'size': 14},
                standoff=0,
                showarrow=False,
                align='center',
                opacity=0.75
            )

        fig.add_traces(data=go.Scatter(
            x=lx,
            y=ly,
            mode='markers',
            marker={
                'color': opt.locus_point_color if not colorize else opt.default_color,
                'size': 6,
                'symbol': 'circle'
            },
            opacity=0.75,
            showlegend=False
        ))

    # Plot the RGB triangles
    for item in spaces:
        # Shadow effect
        fig.add_traces(data=go.Scatter(
            x=[i + 0.0012 for i in item[5]],
            y=[i - 0.0012 for i in item[6]],
            mode='lines',
            line={'color': opt.locus_line_color, 'width': 5},
            opacity=0.3,
            showlegend=False
        ))
        fig.add_traces(data=go.Scatter(
            x=item[5],
            y=item[6],
            mode='lines',
            name=item[3],
            line={'color': item[2], 'width': 4},
            opacity=1,
            showlegend=show_legend
        ))

    # Add any specified white points.
    if white_points:
        wx = []
        wy = []
        annot = []
        for wp in white_points:
            w = ALL_WHITES[observer][wp]
            annot.append(wp)
            xy = convert_chromaticity(Color.convert_chromaticity('xy-1931', opt.chromaticity, w)[:-1], opt)
            wx.append(xy[0])
            wy.append(xy[1])
        fig.add_traces(data=go.Scatter(
            x=wx,
            y=wy,
            mode='markers',
            marker={
                'color': opt.default_colorized_color if colorize else opt.default_color,
                'size': 6,
                'symbol': 'circle'
            },
            opacity=0.75,
            showlegend=False
        ))
        for pt, a in zip(zip(wx, wy), annot):
            fig.add_annotation(
                text=a,
                x=pt[0],
                y=pt[1],
                xshift=20,
                yshift=-3,
                font={'size': 14},
                standoff=0,
                showarrow=False,
                align="center",
                opacity=0.75
            )

    # Add any specified CCT points.
    if cct:
        bx = []
        by = []
        annot = []
        for value in cct:
            temp, duv = (float(v) for v in value.split(':'))
            c = Color.blackbody('xyz-d65', temp, duv, scale=False, method=opt.cct)
            bu, bv = c.split_chromaticity(opt.chromaticity, white=opt.white)[:-1]
            annot.append(f'({round(bu, 4)}, {round(bv, 4)})')
            bx.append(bu)
            by.append(bv)
        fig.add_traces(data=go.Scatter(
            x=bx,
            y=by,
            mode='markers',
            marker={
                'color': opt.default_colorized_color if colorize else opt.default_color,
                'size': 6,
                'symbol': 'circle'
            },
            opacity=0.75,
            showlegend=False
        ))
        for pt, a in zip(zip(bx, by), annot):
            fig.add_annotation(
                text=a,
                x=pt[0],
                y=pt[1],
                font={'size': 14},
                showarrow=False,
                opacity=0.75,
                yshift=14
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
            buv = convert_chromaticity((bu, bv), opt)
            uaxis.append(buv[0])
            vaxis.append(buv[1])

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
                label = f'{kelvin}K' if kelvin != 100000 else '∞'
                rotate = 0 - (math.degrees(math.atan2(duvy[-1] - duvy[0], duvx[-1] - duvx[0])) % 360)
                offset = duv_range[0 if bottom else 1] / 2
                c = Color.blackbody('xyz-d65', kelvin, offset, scale=False, method=opt.cct)
                bu, bv = c.split_chromaticity(opt.chromaticity, white=opt.white)[:-1]

                ax, ay = convert_chromaticity([bu, bv], opt)
                vert = [0, 0] if kelvin == 100000 else alg.polar_to_rect(-20 if bottom else 15, 0 - rotate)
                horz = alg.polar_to_rect(6, 0 - rotate + 90)
                label_offset = [vert[0] + horz[0], vert[1] + horz[1]]
                fig.add_annotation(
                    text=label,
                    x=ax,
                    y=ay,
                    xshift=label_offset[0],
                    yshift=label_offset[1],
                    font={'size': 12},
                    textangle=rotate,
                    standoff=0,
                    showarrow=False
                )

                duvx, duvy = [*zip(*[convert_chromaticity((bu, bv), opt) for bu, bv in zip(duvx, duvy)])]
                fig.add_traces(data=go.Scatter(
                    x=duvx,
                    y=duvy,
                    mode='lines',
                    line={'color': opt.default_colorized_color if colorize else opt.default_color, 'width': 2},
                    showlegend=False,
                    opacity=0.5
                ))

        uaxis, vaxis = get_spline(uaxis, vaxis, len(uaxis) * 3)
        fig.add_traces(data=go.Scatter(
            x=uaxis,
            y=vaxis,
            mode='lines',
            line={'color': opt.default_colorized_color if colorize else opt.default_color, 'width': 2},
            showlegend=False,
            opacity=0.5
        ))

    if overlay_legend and show_legend:
        fig.update_layout(legend={'x': 1, 'bgcolor': 'rgba(0,0,0,0)', 'xanchor': 'right', 'yanchor': 'top'})

    return fig


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
    parser.add_argument('--no-axis', '-x', action="store_true", help="Disable display axis.")
    parser.add_argument('--no-legend', '-g', action="store_true", help="Disable legend.")
    parser.add_argument('--no-labels', '-l', action='store_true', help="Disable showing wavelength labels.")
    parser.add_argument('--no-background', '-b', action='store_true', help="Disable diagram color background.")
    parser.add_argument('--no-alpha', '-a', action='store_true', help="Disable diagram transparent background.")
    parser.add_argument('--black-body', '-k', action='store_true', help="Draw the black body curve (WIP).")
    parser.add_argument('--isotherms', '-i', action='store_true', help="Show isotherms.")
    parser.add_argument('--overlay-legend', '-L', action='store_true', help="Overlay legend on plot.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--height', '-H', type=int, default=600, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")
    args = parser.parse_args()

    fig = cie_diagram(
        mode=args.diagram,
        observer=args.cmfs,
        white_points=args.white_point,
        rgb_spaces=[r.split(':') for r in args.rgb] if args.rgb is not None else None,
        colorize=not args.no_background,
        opacity=0.8 if not args.no_alpha else 1.0,
        show_labels=not args.no_labels,
        show_legend=not args.no_legend,
        overlay_legend=args.overlay_legend,
        axis=not args.no_axis,
        title=args.title,
        black_body=args.black_body,
        isotherms=args.isotherms,
        cct=args.cct,
        pointer=args.pointer,
        height=args.height,
        width=args.width
    )

    if args.output:
        filetype = os.path.splitext(args.output)[1].lstrip('.').lower()
        if filetype == 'html':
            with open(args.output, 'w') as f:
                f.write(io.to_html(fig))
        elif filetype == 'json':
            io.write_json(fig, args.output)
        else:
            with open(args.output, 'wb') as f:
                f.write(fig.to_image(format=filetype, width=args.width, height=args.height))
    else:
        fig.show('browser')


if __name__ == "__main__":
    sys.exit(main())
