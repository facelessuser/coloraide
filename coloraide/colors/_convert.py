"""Convert utilities."""
import math
from .. import util

KAPPA = 24389 / 27  # `29^3 / 3^3`
EPSILON = 216 / 24389  # `6^3 / 29^3`
D50_REF_WHITE = [0.96422, 1.00000, 0.82521]  # D50 reference white

CONVERT_SPACES = ("srgb", "hsl", "hwb", "lch", "lab", "hsv", "display-p3", "a98-rgb", "prophoto-rgb", "rec2020", "xyz")


############
# HSV
############
def hsv_to_srgb(h, s, v):
    """HSV to RGB."""

    return hsl_to_srgb(*hsv_to_hsl(h, s, v))


def hsv_to_hsl(h, s, v):
    """
    HSV to HSL.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    s /= 100.0
    v /= 100.0
    l = v * (1.0 - s / 2.0)

    return [
        h,
        0.0 if (l == 0.0 or l == 0.0) else ((v - l) / min(l, 1.0 - l)) * 100,
        l * 100
    ]


def hsv_to_hwb(h, s, v):
    """HSV to HWB."""

    return srgb_to_hwb(*hsv_to_srgb(h, s, v))


def hsv_to_xyz(h, s, v):
    """HSV to XYZ."""

    r, g, b = hsv_to_srgb(h, s, v)
    return srgb_to_xyz(r, g, b)


def hsv_to_lab(h, s, v):
    """HSV to LAB."""

    return srgb_to_lab(*hsv_to_srgb(h, s, v))


def hsv_to_lch(h, s, v):
    """HSV to LCH."""

    return srgb_to_lch(*hsv_to_srgb(h, s, v))


def hsv_to_display_p3(h, s, v):
    """HSV to Display P3."""

    srgb = hsv_to_srgb(h, s, v)
    return srgb_to_display_p3(*srgb)


def hsv_to_a98_rgb(h, s, v):
    """HSV to A98 RGB."""

    srgb = hsv_to_srgb(h, s, v)
    return srgb_to_a98_rgb(*srgb)


def hsv_to_prophoto_rgb(h, s, v):
    """HSV to ProPhoto RGB."""

    srgb = hsv_to_srgb(h, s, v)
    return srgb_to_prophoto_rgb(*srgb)


def hsv_to_rec2020(h, s, v):
    """HSV to ProPhoto RGB."""

    srgb = hsv_to_srgb(h, s, v)
    return srgb_to_rec2020(*srgb)


############
# SRGB
############
def srgb_to_hsv(r, g, b):
    """SRGB to HSV."""

    return hsl_to_hsv(*srgb_to_hsl(r, g, b))


def srgb_to_hsl(r, g, b):
    """SRGB to HSL."""

    mx = max(r, max(g, b))
    mn = min(r, min(g, b))
    h = 0.0
    s = 0.0
    l = (mn + mx) / 2
    c = mx - mn

    if c != 0.0:
        s = c / (1.0 - abs(2.0 * l - 1))
        if mx == r:
            h = (g - b) / c
        elif mx == g:
            h = (b - r) / c + 2.0
        else:
            h = (r - g) / c + 4.0

    return [h * 60.0, s * 100.0, l * 100.0]


def srgb_to_hwb(r, g, b):
    """SRGB to HWB."""

    h, s, v = srgb_to_hsv(r, g, b)
    w = v * (100.0 - s) / 100.0
    b = 100.0 - v
    return h, w, b


def srgb_to_xyz(r, g, b):
    """SRGB to XYZ."""

    srgb = lin_srgb([r, g, b])
    return d65_to_d50(lin_srgb_to_xyz(srgb))


def srgb_to_lab(r, g, b):
    """SRGB to LAB."""

    x, y, z = srgb_to_xyz(r, g, b)
    return xyz_to_lab(x, y, z)


def srgb_to_lch(r, g, b):
    """SRGB to LCH."""

    return lab_to_lch(*srgb_to_lab(r, g, b))


def srgb_to_display_p3(r, g, b):
    """SRGB to Display P3."""

    xyz = lin_srgb_to_xyz(lin_srgb([r, g, b]))
    return gam_p3(xyz_to_lin_p3(xyz))


def srgb_to_a98_rgb(r, g, b):
    """SRGB to A98 RGB."""

    xyz = lin_srgb_to_xyz(lin_srgb([r, g, b]))
    return gam_a98rgb(xyz_to_lin_a98rgb(xyz))


def srgb_to_prophoto_rgb(r, g, b):
    """SRGB to ProPhoto RGB."""

    xyz = d65_to_d50(lin_srgb_to_xyz(lin_srgb([r, g, b])))
    return gam_prophoto(xyz_to_lin_prophoto(xyz))


def srgb_to_rec2020(r, g, b):
    """SRGB to Rec 2020."""

    xyz = lin_srgb_to_xyz(lin_srgb([r, g, b]))
    return gam_2020(xyz_to_lin_2020(xyz))


############
# Display P3
############
def display_p3_to_hsv(r, g, b):
    """Display P3 to HSV."""

    r, g, b = display_p3_to_srgb(r, g, b)
    return srgb_to_hsv(r, g, b)


def display_p3_to_srgb(r, g, b):
    """Display P3 to SRGB."""

    xyz = lin_p3_to_xyz(lin_p3([r, g, b]))
    return gam_srgb(xyz_to_lin_srgb(xyz))


def display_p3_to_hsl(r, g, b):
    """Display P3 to HSL."""

    return srgb_to_hsl(*display_p3_to_srgb(r, g, b))


def display_p3_to_hwb(r, g, b):
    """Display P3 to HWB."""

    return srgb_to_hwb(*display_p3_to_srgb(r, g, b))


def display_p3_to_xyz(r, g, b):
    """Display p3 to XYZ."""

    prgb = lin_p3([r, g, b])
    return d65_to_d50(lin_p3_to_xyz(prgb))


def display_p3_to_lab(r, g, b):
    """Display P3 to LAB."""

    prgb = lin_p3([r, g, b])
    x, y, z = d65_to_d50(lin_p3_to_xyz(prgb))
    return xyz_to_lab(x, y, z)


def display_p3_to_lch(r, g, b):
    """Display P3 to LCH."""

    return lab_to_lch(*display_p3_to_lab(r, g, b))


def display_p3_to_a98_rgb(r, g, b):
    """Display P3 to A98 RGB."""

    xyz = lin_p3_to_xyz(lin_p3([r, g, b]))
    return gam_a98rgb(xyz_to_lin_a98rgb(xyz))


def display_p3_to_prophoto_rgb(r, g, b):
    """Display P3 to ProPhoto RGB."""

    xyz = d65_to_d50(lin_p3_to_xyz(lin_p3([r, g, b])))
    return gam_prophoto(xyz_to_lin_prophoto(xyz))


def display_p3_to_rec2020(r, g, b):
    """Display P3 to Rec 2020."""

    xyz = lin_p3_to_xyz(lin_p3([r, g, b]))
    return gam_2020(xyz_to_lin_2020(xyz))


############
# A98 RGB
############
def a98_rgb_to_hsv(r, g, b):
    """A98 RGB to HSV."""

    r, g, b = a98_rgb_to_srgb(r, g, b)
    return srgb_to_hsv(r, g, b)


def a98_rgb_to_srgb(r, g, b):
    """A98 RGB to SRGB."""

    xyz = lin_a98rgb_to_xyz(lin_a98rgb([r, g, b]))
    return gam_srgb(xyz_to_lin_srgb(xyz))


def a98_rgb_to_hsl(r, g, b):
    """A98 RGB to HSL."""

    return srgb_to_hsl(*a98_rgb_to_srgb(r, g, b))


def a98_rgb_to_hwb(r, g, b):
    """A98 RGB to HWB."""

    return srgb_to_hwb(*a98_rgb_to_srgb(r, g, b))


def a98_rgb_to_xyz(r, g, b):
    """A98 RGB to XYZ."""

    a98 = lin_a98rgb([r, g, b])
    return d65_to_d50(lin_a98rgb_to_xyz(a98))


def a98_rgb_to_lab(r, g, b):
    """A98 RGB to LAB."""

    a98 = lin_a98rgb([r, g, b])
    x, y, z = d65_to_d50(lin_a98rgb_to_xyz(a98))
    return xyz_to_lab(x, y, z)


def a98_rgb_to_lch(r, g, b):
    """A98 RGB to LCH."""

    return lab_to_lch(*a98_rgb_to_lab(r, g, b))


def a98_rgb_to_display_p3(r, g, b):
    """A98 RGB to SRGB."""

    xyz = lin_a98rgb_to_xyz(lin_a98rgb([r, g, b]))
    return gam_p3(xyz_to_lin_p3(xyz))


def a98_rgb_to_prophoto_rgb(r, g, b):
    """A98 RGB to ProPhoto RGB."""

    xyz = d65_to_d50(lin_a98rgb_to_xyz(lin_a98rgb([r, g, b])))
    return gam_prophoto(xyz_to_lin_prophoto(xyz))


def a98_rgb_to_rec2020(r, g, b):
    """A98 RGB to Rec 2020."""

    xyz = lin_a98rgb_to_xyz(lin_a98rgb([r, g, b]))
    return gam_2020(xyz_to_lin_2020(xyz))


############
# ProPhoto RGB
############
def prophoto_rgb_to_hsv(r, g, b):
    """ProPhoto RGB to HSV."""

    r, g, b = prophoto_rgb_to_srgb(r, g, b)
    return srgb_to_hsv(r, g, b)


def prophoto_rgb_to_srgb(r, g, b):
    """ProPhoto RGB to SRGB."""

    xyz = d50_to_d65(lin_prophoto_to_xyz(lin_prophoto([r, g, b])))
    return gam_srgb(xyz_to_lin_srgb(xyz))


def prophoto_rgb_to_hsl(r, g, b):
    """ProPhoto RGB to HSL."""

    return srgb_to_hsl(*prophoto_rgb_to_srgb(r, g, b))


def prophoto_rgb_to_hwb(r, g, b):
    """ProPhoto RGB to HWB."""

    return srgb_to_hwb(*prophoto_rgb_to_srgb(r, g, b))


def prophoto_rgb_to_xyz(r, g, b):
    """ProPhoto RGB to XYZ."""

    pro = lin_prophoto([r, g, b])
    return lin_prophoto_to_xyz(pro)


def prophoto_rgb_to_lab(r, g, b):
    """ProPhoto RGB to LAB."""

    pro = lin_prophoto([r, g, b])
    x, y, z = lin_prophoto_to_xyz(pro)
    return xyz_to_lab(x, y, z)


def prophoto_rgb_to_lch(r, g, b):
    """ProPhoto RGB to LCH."""

    return lab_to_lch(*prophoto_rgb_to_lab(r, g, b))


def prophoto_rgb_to_display_p3(r, g, b):
    """ProPhoto RGB to SRGB."""

    xyz = d50_to_d65(lin_prophoto_to_xyz(lin_prophoto([r, g, b])))
    return gam_p3(xyz_to_lin_p3(xyz))


def prophoto_rgb_to_a98_rgb(r, g, b):
    """ProPhoto RGB to A98 RGB."""

    xyz = d50_to_d65(lin_prophoto_to_xyz(lin_prophoto([r, g, b])))
    return gam_a98rgb(xyz_to_lin_a98rgb(xyz))


def prophoto_rgb_to_rec2020(r, g, b):
    """ProPhoto RGB to Rec 2020."""

    xyz = d50_to_d65(lin_prophoto_to_xyz(lin_prophoto([r, g, b])))
    return gam_2020(xyz_to_lin_2020(xyz))


############
# Rec 2020
############
def rec2020_to_hsv(r, g, b):
    """Rec 2020 to HSV."""

    r, g, b = rec2020_to_srgb(r, g, b)
    return srgb_to_hsv(r, g, b)


def rec2020_to_srgb(r, g, b):
    """Rec 2020 to SRGB."""

    xyz = lin_2020_to_xyz(lin_2020([r, g, b]))
    return gam_srgb(xyz_to_lin_srgb(xyz))


def rec2020_to_hsl(r, g, b):
    """Rec 2020 to HSL."""

    return srgb_to_hsl(*rec2020_to_srgb(r, g, b))


def rec2020_to_hwb(r, g, b):
    """Rec 2020 to HWB."""

    return srgb_to_hwb(*rec2020_to_srgb(r, g, b))


def rec2020_to_xyz(r, g, b):
    """Rec 2020 to XYZ."""

    rec = lin_2020([r, g, b])
    return d65_to_d50(lin_2020_to_xyz(rec))


def rec2020_to_lab(r, g, b):
    """Rec 2020 to LAB."""

    rec = lin_2020([r, g, b])
    x, y, z = d65_to_d50(lin_2020_to_xyz(rec))
    return xyz_to_lab(x, y, z)


def rec2020_to_lch(r, g, b):
    """Rec 2020 to LCH."""

    return lab_to_lch(*rec2020_to_lab(r, g, b))


def rec2020_to_display_p3(r, g, b):
    """Rec 2020 to SRGB."""

    xyz = lin_2020_to_xyz(lin_2020([r, g, b]))
    return gam_p3(xyz_to_lin_p3(xyz))


def rec2020_to_a98_rgb(r, g, b):
    """Rec 2020 to A98 RGB."""

    xyz = lin_2020_to_xyz(lin_2020([r, g, b]))
    return gam_a98rgb(xyz_to_lin_a98rgb(xyz))


def rec2020_to_prophoto_rgb(r, g, b):
    """Rec 2020 to ProPhoto RGB."""

    xyz = d65_to_d50(lin_2020_to_xyz(lin_2020([r, g, b])))
    return gam_prophoto(xyz_to_lin_prophoto(xyz))


############
# HSL
############
def hsl_to_hsv(h, s, l):
    """
    HSL to HSV.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    s /= 100.0
    l /= 100.0

    v = l + s * min(l, 1.0 - l)

    return [
        h,
        0.0 if (v == 0.0) else 200.0 * (1.0 - l / v),
        100.0 * v
    ]


def hsl_to_srgb(h, s, l):
    """
    HSL to RGB.

    https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB_alternative
    """

    h = h % 360
    s /= 100.0
    l /= 100.0

    def f(n):
        """Calculate the channels."""
        k = (n + h / 30) % 12
        a = s * min(l, 1 - l)
        return l - a * max(-1, min(k - 3, 9 - k, 1))

    return f(0), f(8), f(4)


def hsl_to_hwb(h, s, l):
    """HSL to HWB."""

    r, g, b = hsl_to_srgb(h, s, l)
    return srgb_to_hwb(r, g, b)


def hsl_to_xyz(h, s, l):
    """HSL to XYZ."""

    r, g, b = hsl_to_srgb(h, s, l)
    return srgb_to_xyz(r, g, b)


def hsl_to_lab(h, s, l):
    """HSL to LAB."""

    return srgb_to_lab(*hsl_to_srgb(h, s, l))


def hsl_to_lch(h, s, l):
    """HSL to LCH."""

    return lab_to_lch(*srgb_to_lab(*hsl_to_srgb(h, s, l)))


def hsl_to_display_p3(h, s, l):
    """HSL to Display P3."""

    srgb = hsl_to_srgb(h, s, l)
    return srgb_to_display_p3(*srgb)


def hsl_to_a98_rgb(h, s, l):
    """HSL to A98 RGB."""

    srgb = hsl_to_srgb(h, s, l)
    return srgb_to_a98_rgb(*srgb)


def hsl_to_prophoto_rgb(h, s, l):
    """HSL to ProPhoto RGB."""

    srgb = hsl_to_srgb(h, s, l)
    return srgb_to_prophoto_rgb(*srgb)


def hsl_to_rec2020(h, s, l):
    """HSL to Rec 2020."""

    srgb = hsl_to_srgb(h, s, l)
    return srgb_to_rec2020(*srgb)


############
# HWB
############
def hwb_to_hsv(h, w, b):
    """HWB to HSV."""

    return srgb_to_hsv(*hwb_to_srgb(h, w, b))


def hwb_to_srgb(h, w, b):
    """HWB to RGB."""

    w /= 100.0
    b /= 100.0
    wb = w + b

    if wb > 1.0:
        return [w / wb] * 3

    return [(c * (1.0 - w - b)) + w for c in hsl_to_srgb(h, 100.0, 50.0)]


def hwb_to_hsl(h, w, b):
    """HWB to HSL."""

    r, g, b = hwb_to_srgb(h, w, b)
    return srgb_to_hsl(r, g, b)


def hwb_to_xyz(h, w, b):
    """HWB to XYZ."""

    r, g, b = hwb_to_srgb(h, w, b)
    return srgb_to_xyz(r, g, b)


def hwb_to_lab(h, w, b):
    """HWB to LAB."""

    return srgb_to_lab(*hwb_to_srgb(h, w, b))


def hwb_to_lch(h, w, b):
    """HWB to LCH."""

    return lab_to_lch(*srgb_to_lab(*hwb_to_srgb(h, w, b)))


def hwb_to_display_p3(h, w, b):
    """HWB to Display P3."""

    srgb = hwb_to_srgb(h, w, b)
    return srgb_to_display_p3(*srgb)


def hwb_to_a98_rgb(h, w, b):
    """HWB to A98 RGB."""

    srgb = hwb_to_srgb(h, w, b)
    return srgb_to_a98_rgb(*srgb)


def hwb_to_prophoto_rgb(h, w, b):
    """HWB to ProPhoto RGB."""

    srgb = hwb_to_srgb(h, w, b)
    return srgb_to_prophoto_rgb(*srgb)


def hwb_to_rec2020(h, w, b):
    """HWB to Rec 2020."""

    srgb = hwb_to_srgb(h, w, b)
    return srgb_to_rec2020(*srgb)


############
# LAB
############
def lab_to_hsv(l, a, b):
    """LAB to HSV."""

    return srgb_to_hsv(*lab_to_srgb(l, a, b))


def lab_to_srgb(l, a, b):
    """LAB to RGB."""

    return xyz_to_srgb(*lab_to_xyz(l, a, b))


def lab_to_hsl(l, a, b):
    """LAB to HSL."""

    return srgb_to_hsl(*lab_to_srgb(l, a, b))


def lab_to_hwb(l, a, b):
    """LAB to HWB."""

    return srgb_to_hwb(*lab_to_srgb(l, a, b))


def lab_to_xyz(l, a, b):
    """
    Convert Lab to D50-adapted XYZ.

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    # compute `f`, starting with the luminance-related term
    f1 = (l + 16) / 116
    f0 = a / 500 + f1
    f2 = f1 - b / 200

    # compute `xyz`
    xyz = [
        math.pow(f0, 3) if math.pow(f0, 3) > EPSILON else (116 * f0 - 16) / KAPPA,
        math.pow((l + 16) / 116, 3) if l > KAPPA * EPSILON else l / KAPPA,
        math.pow(f2, 3) if math.pow(f2, 3) > EPSILON else (116 * f2 - 16) / KAPPA
    ]

    # Compute XYZ by scaling `xyz` by reference `white`
    return util.multiply(xyz, D50_REF_WHITE)


def lab_to_lch(l, a, b):
    """LAB to LCH."""

    # This hue correction is taken from https://github.com/LeaVerou/color.js/blob/master/src/spaces/lch.js
    # This appears to be a little smoothing as we get really close to zero.
    # I'm sure it is meant to correct some specific corner case, but not sure what.
    # For now, we will do it as well.
    if abs(a) < util.ACHROMATIC_THRESHOLD and abs(b) < util.ACHROMATIC_THRESHOLD:
        hue = 0
    else:
        hue = math.atan2(b, a) * 180 / math.pi

    return (
        l,
        math.sqrt(math.pow(a, 2) + math.pow(b, 2)),
        hue
    )


def lab_to_display_p3(l, a, b):
    """LAB to Display P3."""

    xyz = d50_to_d65(lab_to_xyz(l, a, b))
    prgb = xyz_to_lin_p3(xyz)
    return gam_p3(prgb)


def lab_to_a98_rgb(l, a, b):
    """LAB to A98 RGB."""

    xyz = d50_to_d65(lab_to_xyz(l, a, b))
    prgb = xyz_to_lin_a98rgb(xyz)
    return gam_a98rgb(prgb)


def lab_to_prophoto_rgb(l, a, b):
    """LAB to ProPhoto RGB."""

    xyz = lab_to_xyz(l, a, b)
    prgb = xyz_to_lin_prophoto(xyz)
    return gam_prophoto(prgb)


def lab_to_rec2020(l, a, b):
    """LAB to Rec 2020."""

    xyz = d50_to_d65(lab_to_xyz(l, a, b))
    prgb = xyz_to_lin_2020(xyz)
    return gam_2020(prgb)


############
# LCH
############
def lch_to_hsv(l, c, h):
    """LCH to HSV."""

    return srgb_to_hsv(*lch_to_srgb(l, c, h))


def lch_to_srgb(l, c, h):
    """LCH to RGB."""

    return lab_to_srgb(*lch_to_lab(l, c, h))


def lch_to_hsl(l, c, h):
    """LCH to HSL."""

    return srgb_to_hsl(*lab_to_srgb(*lch_to_lab(l, c, h)))


def lch_to_hwb(l, c, h):
    """LCH to HWB."""

    return srgb_to_hwb(*lab_to_srgb(*lch_to_lab(l, c, h)))


def lch_to_xyz(l, c, h):
    """LCH to XYZ."""

    l, a, b = lch_to_lab(l, c, h)
    return lab_to_xyz(l, a, b)


def lch_to_lab(l, c, h):
    """LCH to LAB."""

    # If, for whatever reason (mainly direct user input),
    # if chroma is less than zero, clamp to zero.
    if c < 0.0:
        c = 0.0

    return (
        l,
        c * math.cos(h * math.pi / 180.0),
        c * math.sin(h * math.pi / 180.0)
    )


def lch_to_display_p3(l, c, h):
    """LCH to Display P3."""

    return lab_to_display_p3(*lch_to_lab(l, c, h))


def lch_to_a98_rgb(l, c, h):
    """LCH to A98 RGB."""

    return lab_to_a98_rgb(*lch_to_lab(l, c, h))


def lch_to_prophoto_rgb(l, c, h):
    """LCH to ProPhoto RGB."""

    return lab_to_prophoto_rgb(*lch_to_lab(l, c, h))


def lch_to_rec2020(l, c, h):
    """LCH to Rec 2020."""

    return lab_to_rec2020(*lch_to_lab(l, c, h))


############
# XYZ
############
def xyz_to_hsv(x, y, z):
    """XYZ to HSV."""

    return srgb_to_hsv(*xyz_to_srgb(x, y, z))


def xyz_to_srgb(x, y, z):
    """XYZ to SRGB."""

    return gam_srgb(xyz_to_lin_srgb(d50_to_d65([x, y, z])))


def xyz_to_hsl(x, y, z):
    """XYZ to HSL."""

    return srgb_to_hsl(*xyz_to_srgb(x, y, z))


def xyz_to_hwb(x, y, z):
    """XYZ to HWB."""

    return srgb_to_hwb(*xyz_to_srgb(x, y, z))


def xyz_to_lab(x, y, z):
    """Assuming XYZ is relative to D50, convert to CIE Lab from CIE standard."""

    # compute `xyz`, which is XYZ scaled relative to reference white
    xyz = util.divide([x, y, z], D50_REF_WHITE)
    # Compute `f`
    f = [util.cbrt(i) if i > EPSILON else (KAPPA * i + 16.0) / 116.0 for i in xyz]

    return (
        (116.0 * f[1]) - 16.0,
        500.0 * (f[0] - f[1]),
        200.0 * (f[1] - f[2])
    )


def xyz_to_lch(x, y, z):
    """XYZ to LCH."""

    return lab_to_lch(*xyz_to_lab(x, y, z))


def xyz_to_display_p3(x, y, z):
    """XYZ to SRGB."""

    return gam_p3(xyz_to_lin_p3(d50_to_d65([x, y, z])))


def xyz_to_a98_rgb(x, y, z):
    """XYZ to A98 RGB."""

    return gam_a98rgb(xyz_to_lin_a98rgb(d50_to_d65([x, y, z])))


def xyz_to_prophoto_rgb(x, y, z):
    """XYZ to ProPhoto RGB."""

    return gam_prophoto(xyz_to_lin_prophoto([x, y, z]))


def xyz_to_rec2020(x, y, z):
    """XYZ to SRGB."""

    return gam_2020(xyz_to_lin_2020(d50_to_d65([x, y, z])))


############
# White point
############
def d50_to_d65(xyz):
    """Bradford chromatic adaptation from D50 to D65."""

    m = [
        [0.9555766, -0.0230393, 0.0631636],
        [-0.0282895, 1.0099416, 0.0210077],
        [0.0122982, -0.0204830, 1.3299098]
    ]

    return util.dot(m, xyz)


def d65_to_d50(xyz):
    """
    Bradford chromatic adaptation from D65 to D50.

    The matrix below is the result of three operations:
    - convert from XYZ to retinal cone domain
    - scale components from one reference white to another
    - convert back to XYZ
    http://www.brucelindbloom.com/index.html?Eqn_ChromAdapt.html
    """

    m = [
        [1.0478112, 0.0228866, -0.0501270],
        [0.0295424, 0.9904844, -0.0170491],
        [-0.0092345, 0.0150436, 0.7521316]
    ]

    return util.dot(m, xyz)


############
# Linear
############
def lin_srgb_to_xyz(rgb):
    """
    Convert an array of linear-light sRGB values to CIE XYZ using sRGB's own white.

    D65 (no chromatic adaptation)
    """

    m = [
        [0.41239079926595934, 0.357584339383878, 0.1804807884018343],
        [0.21263900587151027, 0.715168678767756, 0.07219231536073371],
        [0.01933081871559182, 0.11919477979462598, 0.9505321522496607]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_srgb(xyz):
    """Convert XYZ to linear-light sRGB."""

    m = [
        [3.2409699419045226, -1.537383177570094, -0.4986107602930034],
        [-0.9692436362808796, 1.8759675015077202, 0.04155505740717559],
        [0.05563007969699366, -0.20397695888897652, 1.0569715142428786]
    ]

    return util.dot(m, xyz)


def lin_p3_to_xyz(rgb):
    """
    Convert an array of linear-light image-p3 values to CIE XYZ using  D65 (no chromatic adaptation).

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [0.4865709486482162, 0.26566769316909306, 0.1982172852343625],
        [0.2289745640697488, 0.6917385218365064, 0.079286914093745],
        [0.0000000000000000, 0.04511338185890264, 1.043944368900976]
    ]

    # 0 was computed as -3.972075516933488e-17
    return util.dot(m, rgb)


def xyz_to_lin_p3(xyz):
    """Convert XYZ to linear-light P3."""

    m = [
        [2.493496911941425, -0.9313836179191239, -0.40271078445071684],
        [-0.8294889695615747, 1.7626640603183463, 0.023624685841943577],
        [0.03584583024378447, -0.07617238926804182, 0.9568845240076872]
    ]

    return util.dot(m, xyz)


def lin_a98rgb_to_xyz(rgb):
    """
    Convert an array of linear-light a98-rgb values to CIE XYZ using D50.D65.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    which has greater numerical precision than section 4.3.5.3 of
    https://www.adobe.com/digitalimag/pdfs/AdobeRGB1998.pdf
    """

    m = [
        [0.5766690429101305, 0.1855582379065463, 0.1882286462349947],
        [0.29734497525053605, 0.6273635662554661, 0.07529145849399788],
        [0.02703136138641234, 0.07068885253582723, 0.9913375368376388]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_a98rgb(xyz):
    """Convert XYZ to linear-light a98-rgb."""

    m = [
        [2.0415879038107465, -0.5650069742788596, -0.34473135077832956],
        [-0.9692436362808795, 1.8759675015077202, 0.04155505740717557],
        [0.013444280632031142, -0.11836239223101838, 1.0151749943912054]
    ]

    return util.dot(m, xyz)


def lin_prophoto_to_xyz(rgb):
    """
    Convert an array of linear-light prophoto-rgb values to CIE XYZ using  D50.D50.

    (so no chromatic adaptation needed afterwards)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [0.7977604896723027, 0.13518583717574031, 0.0313493495815248],
        [0.2880711282292934, 0.7118432178101014, 0.00008565396060525902],
        [0.0, 0.0, 0.8251046025104601]
    ]

    return util.dot(m, rgb)


def xyz_to_lin_prophoto(xyz):
    """Convert XYZ to linear-light prophoto-rgb."""

    m = [
        [1.3457989731028281, -0.25558010007997534, -0.05110628506753401],
        [-0.5446224939028347, 1.5082327413132781, 0.02053603239147973],
        [0.0, 0.0, 1.2119675456389454]
    ]

    return util.dot(m, xyz)


def lin_2020_to_xyz(rgb):
    """
    Convert an array of linear-light rec-2020 values to CIE XYZ using  D65.

    (no chromatic adaptation)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [0.6369580483012914, 0.14461690358620832, 0.1688809751641721],
        [0.2627002120112671, 0.6779980715188708, 0.05930171646986196],
        [0.000000000000000, 0.028072693049087428, 1.060985057710791]
    ]

    # 0 is actually calculated as 4.994106574466076e-17
    return util.dot(m, rgb)


def xyz_to_lin_2020(xyz):
    """Convert XYZ to linear-light rec-2020."""

    m = [
        [1.7166511879712674, -0.35567078377639233, -0.25336628137365974],
        [-0.6666843518324892, 1.6164812366349395, 0.01576854581391113],
        [0.017639857445310783, -0.042770613257808524, 0.9421031212354738]
    ]

    return util.dot(m, xyz)


############
# Gama
############
def lin_2020(rgb):
    """Convert an array of rec-2020 RGB values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    alpha = 1.09929682680944
    beta = 0.018053968510807

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < beta * 4.5:
            result.append(i / 4.5)
        else:
            result.append(math.copysign(math.pow((abs_i + alpha - 1) / alpha, 1 / 0.45), i))
    return result


def gam_2020(rgb):
    """Convert an array of linear-light rec-2020 RGB  in the range 0.0-1.0 to gamma corrected form."""

    alpha = 1.09929682680944
    beta = 0.018053968510807

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i > beta:
            result.append(math.copysign(alpha * math.pow(abs_i, 0.45) - (alpha - 1), i))
        else:
            result.append(4.5 * i)
    return result


def lin_prophoto(rgb):
    """
    Convert an array of prophoto-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    Transfer curve is gamma 1.8 with a small linear portion.
    """

    et2 = 16 / 512

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i <= et2:
            result.append(i / 16)
        else:
            result.append(math.copysign(math.pow(abs_i, 1.8), i))
    return result


def gam_prophoto(rgb):
    """
    Convert an array of linear-light prophoto-rgb  in the range 0.0-1.0 to gamma corrected form.

    Transfer curve is gamma 1.8 with a small linear portion.
    """

    et = 1 / 512

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i >= et:
            result.append(math.copysign(math.pow(abs_i, 1 / 1.8), i))
        else:
            result.append(16 * i)
    return result


def lin_a98rgb(rgb):
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [math.copysign(math.pow(abs(val), 563 / 256), val) for val in rgb]


def gam_a98rgb(rgb):
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [math.copysign(math.pow(abs(val), 256 / 563), val) for val in rgb]


def lin_p3(rgb):
    """Convert an array of image-p3 RGB values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return lin_srgb(rgb)  # same as sRGB


def gam_p3(rgb):
    """Convert an array of linear-light image-p3 RGB  in the range 0.0-1.0 to gamma corrected form."""

    return gam_srgb(rgb)  # same as sRGB


def lin_srgb(rgb):
    """
    Convert an array of sRGB values in the range 0.0 - 1.0 to linear light (un-corrected) form.

    https://en.wikipedia.org/wiki/SRGB
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i < 0.04045:
            result.append(i / 12.92)
        else:
            result.append(math.copysign(math.pow((abs_i + 0.055) / 1.055, 2.4), i))
    return result


def gam_srgb(rgb):
    """
    Convert an array of linear-light sRGB values in the range 0.0-1.0 to gamma corrected form.

    https://en.wikipedia.org/wiki/SRGB
    """

    result = []
    for i in rgb:
        # Mirror linear nature of algorithm on the negative axis
        abs_i = abs(i)
        if abs_i > 0.0031308:
            result.append(math.copysign((1.055 * math.pow(abs_i, 1 / 2.4) - 0.055), i))
        else:
            result.append(12.92 * i)
    return result


############
# Convert
############
def convert(coords, current, wanted):
    """Convert."""

    current = current.lower()
    wanted = wanted.lower()
    if current not in CONVERT_SPACES:
        raise ValueError("'{}' is not a supported color space for conversion".format(current))
    elif wanted not in CONVERT_SPACES:
        raise ValueError("'{}' is not a supported color space for conversion".format(wanted))

    if current == wanted:
        return coords

    return globals()['{}_to_{}'.format(current.replace('-', '_'), wanted.replace('-', '_'))](*coords)


class Convert:
    """Convert class."""

    def _on_convert(self):
        """Run after a convert operation to give an opportunity to do some post convert actions."""

    def convert(self, space, *, fit=False):
        """Convert to color space."""

        space = space.lower()

        if fit:
            method = None if not isinstance(fit, str) else fit
            if not self.in_gamut(space):
                clone = self.clone()
                clone.fit(space, method=method, in_place=True)
                result = clone.convert(space)
                result._on_convert()
                return result

        obj = self.parent.CS_MAP.get(space)
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))
        result = obj(self)
        result._on_convert()
        return result

    def update(self, obj):
        """Update from color."""

        if self is obj:
            self._on_convert()
            return

        if not isinstance(obj, type(self)):
            obj = type(self)(obj)

        for i, value in enumerate(obj.coords()):
            self._coords[i] = value
        self.alpha = obj.alpha
        self._on_convert()
        return self
