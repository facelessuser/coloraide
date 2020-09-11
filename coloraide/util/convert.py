"""Convert utilities."""
from colorsys import rgb_to_hls, hls_to_rgb, rgb_to_hsv, hsv_to_rgb  # noqa: F401
import math

KAPPA = 24389 / 27  # `29^3 / 3^3`
EPSILON = 216 / 24389  # `6^3 / 29^3`
D50_REF_WHITE = [0.96422, 1.00000, 0.82521]  # D50 reference white

CONVERT_SPACES = ("srgb", "hsl", "hwb", "lch", "lab", "hsv", "display-p3", "a98-rgb")


def mat_mul_vec(mat, vec):
    """Multiply the matrix by the vector."""

    return [sum([x * y for x, y in zip(row, vec)]) for row in mat]


def cbrt(x):
    """Cube root."""

    if 0 <= x:
        return x ** (1.0 / 3.0)
    return -(-x) ** (1.0 / 3.0)


############
# HSV
############
def hsv_to_srgb(h, s, v):
    """HSV to RGB."""

    return hsv_to_rgb(h / 360.0, s / 100.0, v / 100.0)


def hsv_to_hsl(h, s, v):
    """HSV to HSL."""

    return srgb_to_hsl(*hsv_to_srgb(h, s, v))


def hsv_to_hwb(h, s, v):
    """HSV to HWB."""

    return srgb_to_hwb(*hsv_to_srgb(h, s, v))


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


############
# SRGB
############
def srgb_to_hsv(r, g, b):
    """SRGB to HSV."""

    h, s, v = rgb_to_hsv(r, g, b)
    return h * 360.0, s * 100.0, v * 100.0


def srgb_to_hsl(r, g, b):
    """SRGB to HSL."""

    h, l, s = rgb_to_hls(r, g, b)
    return h * 360.0, s * 100.0, l * 100.0


def srgb_to_hwb(r, g, b):
    """SRGB to HWB."""

    h, s, v = srgb_to_hsv(r, g, b)
    w = v * (100.0 - s) / 100.0
    b = 100.0 - v
    return h, w, b


def srgb_to_lab(r, g, b):
    """SRGB to LAB."""

    srgb = lin_srgb([r, g, b])
    x, y, z = d65_to_d50(lin_srgb_to_xyz(srgb))
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


############
# Display P3
############
def display_p3_to_hsv(r, g, b):
    """Display P3 to HSV."""

    r, g, b = display_p3_to_srgb(r, g, b)
    return rgb_to_hsv(r, g, b)


def display_p3_to_srgb(r, g, b):
    """Display P3 to SRGB."""

    xyz = lin_p3_to_xyz(lin_p3([r, g, b]))
    return gam_srgb(xyz_to_lin_srgb(xyz))


def display_p3_to_hsl(r, g, b):
    """Display P3 to HSL."""

    return srgb_to_hsl(*display_p3_to_srgb(r, g, b))


def display_p3_to_hwb(r, g, b):
    """Display P3 to HWB."""

    return srgb_to_hwb(display_p3_to_srgb(r, g, b))


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


############
# A98 RGB
############
def a98_rgb_to_hsv(r, g, b):
    """A98 RGB to HSV."""

    r, g, b = a98_rgb_to_srgb(r, g, b)
    return rgb_to_hsv(r, g, b)


def a98_rgb_to_srgb(r, g, b):
    """A98 RGB to SRGB."""

    xyz = lin_a98rgb_to_xyz(lin_a98rgb([r, g, b]))
    return gam_srgb(xyz_to_lin_srgb(xyz))


def a98_rgb_to_hsl(r, g, b):
    """A98 RGB to HSL."""

    return srgb_to_hsl(*a98_rgb_to_srgb(r, g, b))


def a98_rgb_to_hwb(r, g, b):
    """A98 RGB to HWB."""

    return srgb_to_hwb(a98_rgb_to_srgb(r, g, b))


def a98_rgb_to_lab(r, g, b):
    """A98 RGB to LAB."""

    prgb = lin_a98rgb([r, g, b])
    x, y, z = d65_to_d50(lin_a98rgb_to_xyz(prgb))
    return xyz_to_lab(x, y, z)


def a98_rgb_to_lch(r, g, b):
    """A98 RGB to LCH."""

    return lab_to_lch(*a98_rgb_to_lab(r, g, b))


def a98_rgb_to_display_p3(r, g, b):
    """A98 RGB to SRGB."""

    xyz = lin_a98rgb_to_xyz(lin_a98rgb([r, g, b]))
    return gam_p3(xyz_to_lin_p3(xyz))


############
# HSL
############
def hsl_to_hsv(h, s, l):
    """HSL to HSV."""

    return srgb_to_hsv(*hsl_to_srgb(h, s, l))


def hsl_to_srgb(h, s, l):
    """HSL to RGB."""

    return hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)


def hsl_to_hwb(h, s, l):
    """HSL to HWB."""

    r, g, b = hsl_to_srgb(h, s, l)
    return srgb_to_hwb(r, g, b)


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


############
# HWB
############
def hwb_to_hsv(h, w, b):
    """HWB to HSV."""

    return srgb_to_hsv(*hwb_to_srgb(h, w, b))


def hwb_to_srgb(h, w, b):
    """HWB to RGB."""

    return [v * (1.0 - (w / 100.0) - (b / 100.0)) + w for v in hsl_to_srgb(h, 100.0, 50.0)]


def hwb_to_hsl(h, w, b):
    """HWB to HSL."""

    r, g, b = hwb_to_srgb(h, w, b)
    return srgb_to_hsl(r, g, b)


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


############
# LAB
############
def lab_to_hsv(l, a, b):
    """LAB to HSV."""

    return srgb_to_hsv(*lab_to_srgb(l, a, b))


def lab_to_srgb(l, a, b):
    """LAB to RGB."""

    xyz = d50_to_d65(lab_to_xyz(l, a, b))
    srgb = xyz_to_lin_srgb(xyz)
    return gam_srgb(srgb)


def lab_to_hsl(l, a, b):
    """LAB to HSL."""

    return srgb_to_hsl(*lab_to_srgb(l, a, b))


def lab_to_hwb(l, a, b):
    """LAB to HWB."""

    return srgb_to_hwb(*lab_to_srgb(l, a, b))


def lab_to_lch(l, a, b):
    """LAB to LCH."""

    return (
        l,
        math.sqrt(math.pow(a, 2) + math.pow(b, 2)),
        math.atan2(b, a) * 180 / math.pi
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


def lch_to_lab(l, c, h):
    """LCH to LAB."""

    return (
        l,
        c * math.cos(h * math.pi / 180.0),
        c * math.sin(h * math.pi / 180.0)
    )


def lch_to_display_p3(l, c, h):
    """LCH to Display P3."""

    return lab_to_display_p3(*lch_to_lab(l, c, h))


def lch_to_a98_rgb(l, c, h):
    """LCH to Display P3."""

    return lab_to_a98_rgb(*lch_to_lab(l, c, h))


############
# Other
############
def xyz_to_lab(x, y, z):
    """Assuming XYZ is relative to D50, convert to CIE Lab from CIE standard."""

    # compute `xyz`, which is XYZ scaled relative to reference white
    xyz = [i / j for i, j in zip([x, y, z], D50_REF_WHITE)]
    # Compute `f`
    f = [cbrt(i) if i > EPSILON else (KAPPA * i + 16.0) / 116.0 for i in xyz]

    return (
        (116.0 * f[1]) - 16.0,
        500.0 * (f[0] - f[1]),
        200.0 * (f[1] - f[2])
    )


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
    return [i * j for i, j in zip(xyz, D50_REF_WHITE)]


def d50_to_d65(xyz):
    """Bradford chromatic adaptation from D50 to D65."""

    m = [
        [0.9555766, -0.0230393, 0.0631636],
        [-0.0282895, 1.0099416, 0.0210077],
        [0.0122982, -0.0204830, 1.3299098]
    ]

    return mat_mul_vec(m, xyz)


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

    return mat_mul_vec(m, xyz)


def lin_srgb_to_xyz(rgb):
    """
    Convert an array of linear-light sRGB values to CIE XYZ using sRGB's own white.

    D65 (no chromatic adaptation)
    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    m = [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041]
    ]

    return mat_mul_vec(m, rgb)


def xyz_to_lin_srgb(xyz):
    """Convert XYZ to linear-light sRGB."""

    m = [
        [3.2404542, -1.5371385, -0.4985314],
        [-0.9692660, 1.8760108, 0.0415560],
        [0.0556434, -0.2040259, 1.0572252]
    ]

    return mat_mul_vec(m, xyz)


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
    return mat_mul_vec(m, rgb)


def xyz_to_lin_p3(xyz):
    """Convert XYZ to linear-light P3."""

    m = [
        [2.493496911941425, -0.9313836179191239, -0.40271078445071684],
        [-0.8294889695615747, 1.7626640603183463, 0.023624685841943577],
        [0.03584583024378447, -0.07617238926804182, 0.9568845240076872]
    ]

    return mat_mul_vec(m, xyz)


def lin_a98rgb(rgb):
    """Convert an array of a98-rgb values in the range 0.0 - 1.0 to linear light (un-corrected) form."""

    return [math.pow(val, 563 / 256) for val in rgb]


def gam_a98rgb(rgb):
    """Convert an array of linear-light a98-rgb  in the range 0.0-1.0 to gamma corrected form."""

    return [math.pow(val, 256 / 563) for val in rgb]


def lin_a98rgb_to_xyz(rgb):
    """Convert an array of linear-light a98-rgb values to CIE XYZ using D50.D65.

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

    return mat_mul_vec(m, rgb)


def xyz_to_lin_a98rgb(xyz):
    """Convert XYZ to linear-light a98-rgb."""

    m = [
        [2.0415879038107465, -0.5650069742788596, -0.34473135077832956],
        [-0.9692436362808795, 1.8759675015077202, 0.04155505740717557],
        [0.013444280632031142, -0.11836239223101838, 1.0151749943912054]
    ]

    return mat_mul_vec(m, xyz)


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

    return [(i / 12.92) if i < 0.04045 else math.pow((i + 0.055) / 1.055, 2.4) for i in rgb]


def gam_srgb(rgb):
    """
    Convert an array of linear-light sRGB values in the range 0.0-1.0 to gamma corrected form.

    https://en.wikipedia.org/wiki/SRGB
    """

    return [(1.055 * math.pow(i, 1 / 2.4) - 0.055) if i > 0.0031308 else (12.92 * i) for i in rgb]


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
