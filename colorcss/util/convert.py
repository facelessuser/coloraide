"""Convert utilities."""
from colorsys import rgb_to_hls, hls_to_rgb, rgb_to_hsv, hsv_to_rgb  # noqa: F401
import math

KAPPA = 24389 / 27  # `29^3 / 3^3`
EPSILON = 216 / 24389  # `6^3 / 29^3`
D50_REF_WHITE = [0.96422, 1.00000, 0.82521]  # D50 reference white


def mat_mul_vec(mat, vec):
    """Multiply the matrix by the vector."""

    return [sum([x * y for x, y in zip(row, vec)]) for row in mat]


def cbrt(x):
    """Cube root."""

    if 0 <= x:
        return x ** (1.0 / 3.0)
    return -(-x) ** (1.0 / 3.0)


def rgb_to_hsl(r, g, b):
    """RGB to HSL."""

    h, l, s = rgb_to_hls(r, g, b)
    return h, s, l


def hsl_to_rgb(h, s, l):
    """HSL to RGB."""

    return hls_to_rgb(h, l, s)


def hwb_to_rgb(h, w, b):
    """HWB to RGB."""

    return [v * (1 - w - b) + w for v in hsl_to_rgb(h, 1.0, .5)]


def rgb_to_hwb(r, g, b):
    """RGB to HWB."""

    h, s, v = rgb_to_hsv(r, g, b)
    w = (1.0 - s) * v
    b = 1.0 - v
    return h, w, b


def hsl_to_hwb(h, s, l):
    """HSL to HWB."""

    r, g, b = hsl_to_rgb(h, s, l)
    return rgb_to_hwb(r, g, b)


def hwb_to_hsl(h, w, b):
    """HWB to HSL."""

    r, g, b = hwb_to_rgb(h, w, b)
    return rgb_to_hwb(r, g, b)


def hsl_to_lab(h, s, l):
    """HSL to LAB."""

    return rgb_to_lab(*hsl_to_rgb(h, s, l))


def lab_to_hsl(l, a, b):
    """LAB to HSL."""

    return rgb_to_hsl(*lab_to_rgb(l, a, b))


def hwb_to_lab(h, w, b):
    """HWB to LAB."""

    return rgb_to_lab(*hwb_to_rgb(h, w, b))


def lab_to_hwb(l, a, b):
    """LAB to HWB."""

    return rgb_to_hwb(*lab_to_rgb(l, a, b))


def lab_to_rgb(l, a, b):
    """LAB to RGB."""

    xyz = d50_to_d65(lab_to_xyz(l, a, b))
    srgb = xyz_to_lin_srgb(xyz)
    return gam_srgb(srgb)


def rgb_to_lab(r, g, b):
    """RGB to LAB."""

    srgb = lin_srgb([r, g, b])
    x, y, z = d65_to_d50(lin_srgb_to_xyz(srgb))
    return xyz_to_lab(x, y, z)


def lab_to_lch(l, a, b):
    """LAB to LCH."""

    return (
        l,
        math.sqrt(math.pow(a, 2) + math.pow(b, 2)),
        math.atan2(b, a) * 180 / math.pi
    )


def lch_to_lab(l, c, h):
    """LCH to LAB."""

    return (
        l,
        c * math.cos(h * math.pi / 180.0),
        c * math.sin(h * math.pi / 180.0)
    )


def rgb_to_lch(r, g, b):
    """RGB to LCH."""

    return lab_to_lch(*rgb_to_lab(r, g, b))


def lch_to_rgb(l, c, h):
    """LCH to RGB."""

    return lab_to_rgb(*lch_to_lab(l, c, h))


def hsl_to_lch(h, s, l):
    """HSL to LCH."""

    return lab_to_lch(*rgb_to_lab(*hsl_to_rgb(h, s, l)))


def lch_to_hsl(l, c, h):
    """LCH to HSL."""

    return rgb_to_hsl(*lab_to_rgb(*lch_to_lab(l, c, h)))


def hwb_to_lch(h, w, b):
    """HWB to LCH."""

    return lab_to_lch(*rgb_to_lab(*hwb_to_rgb(h, w, b)))


def lch_to_hwb(l, c, h):
    """LCH to HWB."""

    return rgb_to_hwb(*lab_to_rgb(*lch_to_lab(l, c, h)))


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
