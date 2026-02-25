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
from coloraide.cat import WHITES  # noqa: E402
from coloraide import algebra as alg  # noqa: E402
from coloraide.temperature import ohno_2013  # noqa: E402
from coloraide import cmfs  # noqa: E402
from coloraide import gamut  # noqa: E402
from coloraide.spaces import Labish, LChish

ALL_WHITES = copy.deepcopy(WHITES)
ALL_WHITES['2deg']['D60'] = ColorAll.CS_MAP['aces2065-1'].WHITE

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
    if opt.polar:
        return alg.polar_to_rect(color[opt.viewed_chromaticity_names[0]], color[opt.viewed_chromaticity_names[1]])
    return color[opt.viewed_chromaticity_names[0]], color[opt.viewed_chromaticity_names[1]]


def get_spectral_locus_labels(opt, poly):
    """Get the spectral locus wavelength labels."""

    deltax = (poly.xmax - poly.xmin)
    deltay = (poly.ymax - poly.ymin)
    distance = ((deltax + deltay) / 2) * 0.05

    annotations = []
    for wave in sorted(opt.spectral_locus_labels):
        x, y = convert_chromaticity(
            ColorAll.convert_chromaticity('xy-1931', opt.chromaticity, opt.observer.xy(wave))[:-1],
            opt
        )
        x1, y1 = convert_chromaticity(
            ColorAll.convert_chromaticity('xy-1931', opt.chromaticity, opt.observer.xy(wave - 0.05))[:-1],
            opt
        )
        x2, y2 = convert_chromaticity(
            ColorAll.convert_chromaticity('xy-1931', opt.chromaticity, opt.observer.xy(wave + 0.05))[:-1],
            opt
        )

        d1 = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
        d2 = math.sqrt((x2 - x) ** 2 + (y2 - y) ** 2)
        factor = d1 / (d1 + d2)

        diry = (y - y1) > 0
        dirx = (x - x1) > 0
        temp = (y - y1) / (x - x1)
        m1 = -(temp) ** -1 if temp else 0
        temp = (y2 - y) / (x2 - x)
        m2 = -(temp) ** -1 if temp else 0
        m = alg.lerp(m1, m2, factor)

        length = math.sqrt(1.0 + m ** 2)
        dx = 1.0 / length
        dy = m / length

        noadjust = wave < 695

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


class Polygon:
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
        # Get the previous vertex
        ax = self.x[0]
        ay = self.y[0]
        for i in range(1, self.length):
            # Get the current vertex
            bx = self.x[i]
            by = self.y[i]

            # Check if crossing
            if ay <= py:
                if by > py and ((bx - ax) * (py - ay) - (px - ax) * (by - ay)) > 0:
                    winding += 1
            elif by <= py and ((bx - ax) * (py - ay) - (px - ax) * (by - ay)) < 0:
                winding += 1

            # Current is now previous
            ax = bx
            ay = by

        # If odd, we are inside
        return bool(winding & 1)


class DiagramOptions:
    """
    Diagram options.

    Manage some diagram specifics options.

    - Handle title and axis names.
    - Handle some diagram colors specific to themes.
    """

    def __init__(self, mode="1931", title=""):
        """Initialize."""

        self.observer = cmfs.CIE_1931_2DEG
        self.white = ALL_WHITES['2deg']['D65']
        self.polar = False

        self.viewed_chromaticity = None
        if mode not in ('1931', '1960', '1976'):
            if ColorAll.CS_MAP.get(mode):
                cs = ColorAll.CS_MAP[mode]
                if isinstance(cs, Labish):
                    self.chromaticity = 'xy-1931'
                    self.viewed_chromaticity = mode
                    self.viewed_chromaticity_names = cs.names()[1:]
                elif isinstance(cs, LChish):
                    self.chromaticity = 'xy-1931'
                    self.viewed_chromaticity = mode
                    self.viewed_chromaticity_names = cs.names()[1:]
                    self.polar = True
            if self.viewed_chromaticity is None:
                raise ValueError(f"Unrecognized 'mode': {mode}")
        else:
            if self.viewed_chromaticity is None:
                self.chromaticity = ('xy-' + mode) if mode == '1931' else ('uv-' + mode)
            else:
                self.chromaticity = 'xy-1931'
            self.viewed_chromaticity = self.chromaticity

        self.mode = mode
        if mode == "1931":
            self.spectral_locus_labels = labels_1931
            self.axis_labels = ('CIE x', 'CIE y')
            self.title = "CIE 1931 Chromaticy Diagram - 2˚ Degree Standard Observer"
        elif mode == "1976":
            self.spectral_locus_labels = labels_1960
            self.axis_labels = ("CIE u'", "CIE v'")
            self.title = "CIE 1976 UCS Chromaticity Diagram - 2˚ Degree Standard Observer"
        elif mode == '1960':
            self.spectral_locus_labels = labels_1960
            self.axis_labels = ('CIE u', 'CIE v')
            self.title = "CIE 1960 UCS Chromaticity Diagram - 2˚ Degree Standard Observer"
        else:
            self.spectral_locus_labels = labels_1960
            self.axis_labels = self.viewed_chromaticity_names if not self.polar else ['a', 'b']
            self.title = f"CIE {mode} Chromaticity Diagram - 2˚ Degree Standard Observer"

        self.cct = 'ohno-2013'

        if title:
            self.title = title

        self.default_color = "#000000"
        self.default_colorized_color = "#333333"
        self.locus_label_color = "#000000"
        self.locus_point_color = "#000000"
        self.locus_line_color = "#333333"


def cie_diagram(
    mode="1931", colorize=True, opacity=1, rgb_spaces=None, white_points=None,
    title='', label_opacity=True, axis=True, show_legend=True, overlay_legend=True,
    black_body=False, isotherms=False, cct=None, pointer=False, macadam_limits=False,
    estimate_wavelength=None, wavelength_whitepoint=None, wavelength=None, resolution=800,
    height=600, width=800
):
    """CIE diagram."""

    opt = DiagramOptions(mode=mode, title=title)

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

    xys =[]
    annotations = []

    # Get points for the spectral locus
    for r in alg.linspace(360, 780, len(opt.observer)):
        xy = opt.observer.xy(r)
        xy = Color.convert_chromaticity('xy-1931', opt.chromaticity, xy)[:-1]
        xys.append(xy)

    # Draw the bottom purple line
    interp = alg.interpolate([xys[-1], xys[0]])
    xys.extend([interp(i / 50) for i in range(1, 51)])

    # Create the polygon representing the locus
    poly = Polygon(*zip(*[convert_chromaticity(r, opt) for r in xys]))

    # Create wavelength labels
    annotations = get_spectral_locus_labels(opt, poly)

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
                    _sx, _sy = zip(*[interp(i / 25) for i in range(1, 26)])
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
                    Polygon(_x, _y)
                )
            )

    # Rösch-MacAdam gamut
    if macadam_limits:
        for p in macadam_limits:
            bounds, color = p.split(':')
            sx = []
            sy = []
            xy = []
            if bounds == 'max':
                pts = gamut.visible_spectrum.macadam_limits()
                label = 'visible spectrum'
            else:
                l = min(1, max(0, float(bounds)))
                pts = gamut.visible_spectrum.macadam_limits(l)
                label = f'MacAdam Limit Y={round(l, 2)}'
            pts.append(pts[0])
            for pt in pts:
                x, y = Color.convert_chromaticity('xy-1931', opt.chromaticity, pt[:-1])[:-1]
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
                    Polygon(_x, _y)
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
            xy = [convert_chromaticity((a, b), opt) for a, b in zip(sx, sy)]
            _x, _y = zip(*xy)
            spaces.append(
                (
                    sx,
                    sy,
                    color,
                    space,
                    Polygon(_x, _y)
                )
            )

    # Generate fill colors for inside the spectral locus
    poly = Polygon(*zip(*[convert_chromaticity(r, opt) for r in xys]))
    if colorize:
        px = []
        py = []
        c = []
        cx = []
        cy = []
        cc = []
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
            alg.linspace(min(poly.xmin, min_range_x), max(poly.xmax, max_range_x), resolution),
            alg.linspace(min(poly.ymin, min_range_y), max(poly.ymax, max_range_y), resolution)
        ):
            in_space = False
            if spaces:
                for s in spaces:
                    if s[4].contains(r):
                        in_space = True
                        break

            if poly.contains(r):
                if in_space:
                    cx.append(r[0])
                    cy.append(r[1])
                else:
                    px.append(r[0])
                    py.append(r[1])

                if opt.mode not in ('1931', '1960', '1976'):
                    cs = Color.CS_MAP[opt.mode]
                    values = [''] * 3
                    l, a, b = cs.indexes()
                    values[l] = '100%'
                    if opt.polar:
                        chroma, hue = alg.rect_to_polar(r[0], r[1])
                        values[a] = str(chroma)
                        values[b] = str(hue)
                    else:
                        values[a] = str(r[0])
                        values[b] = str(r[1])
                    srgb = Color(
                        f'color({cs.SERIALIZE[0]} {values[0]} {values[1]} {values[2]})'
                    ).convert('srgb', in_place=True)
                    srgb.fit(method='scale', max_saturation=True, clip_negative=True)
                else:
                    srgb = Color.chromaticity(
                        'srgb',
                        r,
                        opt.chromaticity,
                        white=opt.white,
                        scale=True,
                        scale_space='srgb-linear',
                        clip_negative=True,
                        max_saturation=True
                    )
                if in_space:
                    cc.append(srgb.to_string(hex=True, fit="clip"))
                else:
                    c.append(srgb.to_string(hex=True, fit="clip"))
            elif in_space:
                # xy = convert_chromaticity(r, opt)
                cx.append(r[0])
                cy.append(r[1])
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

    # Spectral Locus
    fig.add_traces(data=go.Scatter(
        x=poly.x,
        y=poly.y,
        mode='lines',
        line={'color': opt.locus_line_color if colorize else opt.default_color, 'width': 2},
        showlegend=False,
        opacity=0.5
    ))

    if label_opacity > 0:
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
                opacity=label_opacity
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
            opacity=label_opacity,
            showlegend=False
        ))

    # Plot the RGB triangles
    for item in spaces:
        # Shadow effect
        fig.add_traces(data=go.Scatter(
            x=[i + 0.0012 for i in item[4].x],
            y=[i - 0.0012 for i in item[4].y],
            mode='lines',
            line={'color': opt.locus_line_color, 'width': 5},
            opacity=0.3,
            showlegend=False
        ))
        fig.add_traces(data=go.Scatter(
            x=item[4].x,
            y=item[4].y,
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
            w = ALL_WHITES['2deg'][wp]
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

    # Estimate wavelengths.
    if wavelength:
        if not estimate_wavelength:
            estimate_wavelength = []
        for w in wavelength:
            estimate_wavelength.append(float(w))
    if estimate_wavelength:
        for c in estimate_wavelength:
            x = []
            y = []
            is_wavelength = isinstance(c, float)
            color = Color(c) if not is_wavelength else Color.from_wavelength('xyy', c, scale=False)
            if wavelength_whitepoint:
                w = WHITES['2deg'][wavelength_whitepoint]
            else:
                w = color._space.WHITE
            wlabel = str(w)
            for k, v in WHITES['2deg'].items():
                if w == v:
                    wlabel = k
                    break
            dwl = color.wavelength(white=w)
            cwl = color.wavelength(white=w, complementary=True)
            if not math.isnan(dwl[1][0]):
                bu0, bv0 = convert_chromaticity(
                    color.split_chromaticity(opt.chromaticity, white=opt.white)[:-1],
                    opt
                )
                bu1, bv1 = convert_chromaticity(
                    Color.convert_chromaticity('xy-1931', opt.chromaticity, dwl[1])[:-1],
                    opt
                )
                bu2, bv2 = convert_chromaticity(
                    Color.convert_chromaticity('xy-1931', opt.chromaticity, w)[:-1],
                    opt
                )
                bu3, bv3 = convert_chromaticity(
                    Color.convert_chromaticity('xy-1931', opt.chromaticity, cwl[1])[:-1],
                    opt
                )
                x = [bu1, bu0, bu2, bu3] if not is_wavelength else [bu1, bu2, bu3]
                y = [bv1, bv0, bv2, bv3] if not is_wavelength else [bv1, bv2, bv3]
                fig.add_traces(data=go.Scatter(
                    x=x,
                    y=y,
                    mode='lines+markers',
                    marker={
                        'color': opt.default_colorized_color if colorize else opt.default_color,
                        'size': 6,
                        'symbol': 'circle'
                    },
                    opacity=0.5,
                    showlegend=False
                ))
                if not is_wavelength:
                    labels = [f'Dominant ({dwl[0]})', '', wlabel, 'Complementary']
                else:
                    labels = [f'Dominant ({dwl[0]})', wlabel, 'Complementary']
                for _x, _y, _l in zip(x, y, labels):
                    fig.add_annotation(
                        text=_l,
                        x=_x,
                        y=_y,
                        font={'size': 14},
                        showarrow=False,
                        opacity=0.75,
                        yshift=14
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
            bu, bv = convert_chromaticity((bu, bv), opt)
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
                    bu, bv = convert_chromaticity((bu, bv), opt)
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

                fig.add_traces(data=go.Scatter(
                    x=duvx,
                    y=duvy,
                    mode='lines',
                    line={'color': opt.default_colorized_color if colorize else opt.default_color, 'width': 2},
                    showlegend=False,
                    opacity=0.5
                ))

        uaxis, vaxis = zip(
            *alg.interpolate([[i, j] for i, j in zip(uaxis, vaxis)], method='sprague').steps(len(uaxis) * 3)
        )
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
    parser.add_argument('--white-point', '-w', action='append', help="A white point to plot.")
    parser.add_argument('--cct', '-C', action='append', help="A point specified by 'CCT:Duv'.")
    parser.add_argument(
        '--pointer', '-P', action='append',
        help="Show Pointer gamut by specifying an L* value and a color for the boundary '30:color'. "
             "'max' can be used show the maximum gamut instead of the gamut at a specific lightness 'max:color'."
    )
    parser.add_argument(
        '--macadam-limits', '-M', action='append',
        help="Show MacAdam limits, relative to D65, by specifying an L* value and a color for the boundary '30:color'. "
             "'max' can be used show the entire visible spectrum 'max:color'."
    )
    parser.add_argument(
        '--estimate-wavelength', '-e', action='append',
        help="Estimate the wavelength of a color and draw the dominant and complementary points."
    )
    parser.add_argument(
        '--wavelength-whitepoint', '-E',
        help="Provide a specific white point to estimate wavelengths from."
    )
    parser.add_argument(
        '--wavelength', action='append',
        help="Provide a specific wavelength and convert it to a color and plot the complementary."
    )
    parser.add_argument('--rgb', '-r', action='append', help="An RGB space to show on diagram: 'space:color'.")
    parser.add_argument('--title', '-t', default='', help="Override title with your own.")
    parser.add_argument('--no-axis', '-x', action="store_true", help="Disable display axis.")
    parser.add_argument('--no-legend', '-g', action="store_true", help="Disable legend.")
    parser.add_argument('--label-opacity', '-l', type=float, default=0.75, help="Control opacity of labels.")
    parser.add_argument('--no-background', '-b', action='store_true', help="Disable diagram color background.")
    parser.add_argument('--no-alpha', '-a', action='store_true', help="Disable diagram transparent background.")
    parser.add_argument('--black-body', '-k', action='store_true', help="Draw the black body curve (WIP).")
    parser.add_argument('--isotherms', '-i', action='store_true', help="Show isotherms.")
    parser.add_argument('--overlay-legend', '-L', action='store_true', help="Overlay legend on plot.")
    parser.add_argument('--resolution', '-R', type=int, default=800, help="Resolution of fill colors.")
    parser.add_argument('--output', '-o', default='', help='Output file.')
    parser.add_argument('--height', '-H', type=int, default=600, help="Height")
    parser.add_argument('--width', '-W', type=int, default=800, help="Width")
    args = parser.parse_args()

    fig = cie_diagram(
        mode=args.diagram,
        white_points=args.white_point,
        rgb_spaces=[r.split(':') for r in args.rgb] if args.rgb is not None else None,
        colorize=not args.no_background,
        opacity=0.8 if not args.no_alpha else 1.0,
        label_opacity=args.label_opacity,
        show_legend=not args.no_legend,
        overlay_legend=args.overlay_legend,
        axis=not args.no_axis,
        title=args.title,
        black_body=args.black_body,
        isotherms=args.isotherms,
        cct=args.cct,
        pointer=args.pointer,
        macadam_limits=args.macadam_limits,
        estimate_wavelength=args.estimate_wavelength,
        wavelength_whitepoint=args.wavelength_whitepoint,
        wavelength=args.wavelength,
        resolution=args.resolution,
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
