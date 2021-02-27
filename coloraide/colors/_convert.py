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
def hsv_to_hsl(hsv):
    """
    HSV to HSL.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    h, s, v = hsv
    s /= 100.0
    v /= 100.0
    l = v * (1.0 - s / 2.0)

    return [
        h,
        0.0 if (l == 0.0 or l == 0.0) else ((v - l) / min(l, 1.0 - l)) * 100,
        l * 100
    ]


############
# SRGB
############
def srgb_to_hsv(rgb):
    """SRGB to HSV."""

    return hsl_to_hsv(srgb_to_hsl(rgb))


def srgb_to_hsl(rgb):
    """SRGB to HSL."""

    r, g, b = rgb
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

    return h * 60.0, s * 100.0, l * 100.0


def srgb_to_hwb(rgb):
    """SRGB to HWB."""

    h, s, v = srgb_to_hsv(rgb)
    w = v * (100.0 - s) / 100.0
    b = 100.0 - v
    return h, w, b


def srgb_to_xyz(rgb):
    """SRGB to XYZ."""

    return d65_to_d50(lin_srgb_to_xyz(lin_srgb(rgb)))


############
# Display P3
############
def display_p3_to_xyz(rgb):
    """Display p3 to XYZ."""

    return d65_to_d50(lin_p3_to_xyz(lin_p3(rgb)))


############
# A98 RGB
############
def a98_rgb_to_xyz(rgb):
    """A98 RGB to XYZ."""

    return d65_to_d50(lin_a98rgb_to_xyz(lin_a98rgb(rgb)))


############
# ProPhoto RGB
############
def prophoto_rgb_to_xyz(rgb):
    """ProPhoto RGB to XYZ."""

    return lin_prophoto_to_xyz(lin_prophoto(rgb))


############
# Rec 2020
############
def rec2020_to_xyz(rgb):
    """Rec 2020 to XYZ."""

    return d65_to_d50(lin_2020_to_xyz(lin_2020(rgb)))


############
# HSL
############
def hsl_to_hsv(hsl):
    """
    HSL to HSV.

    https://en.wikipedia.org/wiki/HSL_and_HSV#Interconversion
    """

    h, s, l = hsl
    s /= 100.0
    l /= 100.0

    v = l + s * min(l, 1.0 - l)

    return [
        h,
        0.0 if (v == 0.0) else 200.0 * (1.0 - l / v),
        100.0 * v
    ]


def hsl_to_srgb(hsl):
    """
    HSL to RGB.

    https://en.wikipedia.org/wiki/HSL_and_HSV#HSL_to_RGB_alternative
    """

    h, s, l = hsl
    h = h % 360
    s /= 100.0
    l /= 100.0

    def f(n):
        """Calculate the channels."""
        k = (n + h / 30) % 12
        a = s * min(l, 1 - l)
        return l - a * max(-1, min(k - 3, 9 - k, 1))

    return f(0), f(8), f(4)


############
# HWB
############
def hwb_to_srgb(hwb):
    """HWB to RGB."""

    h, w, b = hwb
    w /= 100.0
    b /= 100.0
    wb = w + b

    if wb > 1.0:
        return [w / wb] * 3

    return [(c * (1.0 - w - b)) + w for c in hsl_to_srgb([h, 100.0, 50.0])]


############
# LAB
############
def lab_to_xyz(lab):
    """
    Convert Lab to D50-adapted XYZ.

    http://www.brucelindbloom.com/index.html?Eqn_RGB_XYZ_Matrix.html
    """

    l, a, b = lab

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


def lab_to_lch(lab):
    """LAB to LCH."""

    l, a, b = lab

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


############
# LCH
############
def lch_to_lab(lch):
    """LCH to LAB."""

    l, c, h = lch

    # If, for whatever reason (mainly direct user input),
    # if chroma is less than zero, clamp to zero.
    if c < 0.0:
        c = 0.0

    return (
        l,
        c * math.cos(h * math.pi / 180.0),
        c * math.sin(h * math.pi / 180.0)
    )


############
# XYZ
############
def xyz_to_srgb(xyz):
    """XYZ to SRGB."""

    return gam_srgb(xyz_to_lin_srgb(d50_to_d65(xyz)))


def xyz_to_display_p3(xyz):
    """XYZ to SRGB."""

    return gam_p3(xyz_to_lin_p3(d50_to_d65(xyz)))


def xyz_to_a98_rgb(xyz):
    """XYZ to A98 RGB."""

    return gam_a98rgb(xyz_to_lin_a98rgb(d50_to_d65(xyz)))


def xyz_to_prophoto_rgb(xyz):
    """XYZ to ProPhoto RGB."""

    return gam_prophoto(xyz_to_lin_prophoto(xyz))


def xyz_to_rec2020(xyz):
    """XYZ to SRGB."""

    return gam_2020(xyz_to_lin_2020(d50_to_d65(xyz)))


def xyz_to_lab(xyz):
    """Assuming XYZ is relative to D50, convert to CIE Lab from CIE standard."""

    # compute `xyz`, which is XYZ scaled relative to reference white
    xyz = util.divide(xyz, D50_REF_WHITE)
    # Compute `f`
    f = [util.cbrt(i) if i > EPSILON else (KAPPA * i + 16.0) / 116.0 for i in xyz]

    return (
        (116.0 * f[1]) - 16.0,
        500.0 * (f[0] - f[1]),
        200.0 * (f[1] - f[2])
    )


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

        convert_to = '_to_{}'.format(space)
        convert_from = '_from_{}'.format(self.space())

        obj = self.parent.CS_MAP.get(space)
        if obj is None:
            raise ValueError("'{}' is not a valid color space".format(space))

        # See if there is a direct conversion route
        func = None
        coords = self._coords
        if hasattr(self, convert_to):
            func = getattr(self, convert_to)
            coords = func(coords)
        elif hasattr(obj, convert_from):
            func = getattr(obj, convert_from)
            coords = func(coords)

        # See if there is an XYZ route
        if func is None and self.space() != space:
            func = getattr(self, '_to_xyz')
            coords = func(coords)

            if space != 'xyz':
                func = getattr(obj, '_from_xyz')
                coords = func(coords)

        coords = list(coords) + [self.alpha]
        result = obj(coords)
        result.parent = self.parent
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
