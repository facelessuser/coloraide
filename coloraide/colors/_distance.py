import math
from .. import util

G_CONST = math.pow(25, 7)
RAD2DEG = 180 / math.pi
DEG2RAD = math.pi / 180

SUPPORTED = frozenset(["76", "2000", "cmc", "94"])


def distance_euclidean(color1, color2, space="lab", **kwargs):
    """Euclidean distance."""

    lab1 = color1.convert(space)
    lab2 = color2.convert(space)

    coords1 = util.no_nan(lab1.coords())
    coords2 = util.no_nan(lab2.coords())

    total = 0
    for i, coord in enumerate(coords1):
        total += math.pow(coords2[i] - coord, 2)
    return math.sqrt(total)


def delta_e_76(color1, color2, **kwargs):
    """
    Delta E 1976 color distance formula.

    Basically this is Euclidean distance in the Lab space.
    """

    return distance_euclidean(color1, color2, space="lab")


def delta_e_94(color1, color2, kl=1, k1=0.045, k2=0.015):
    """
    Delta E 1994 color distance formula.

    http://www.brucelindbloom.com/Eqn_DeltaE_CIE94.html
    """

    lab1 = color1.convert("lab")
    lab2 = color2.convert("lab")

    l1, a1, b1 = util.no_nan(lab1.coords())
    c1 = math.sqrt(math.pow(a1, 2) + math.pow(b1, 2))
    l2, a2, b2 = util.no_nan(lab2.coords())
    c2 = math.sqrt(math.pow(a2, 2) + math.pow(b2, 2))

    dl = l1 - l2
    dc = c1 - c2

    da = a1 - a2
    db = b1 - b2

    # We never reference `dh` until the very end, and when we do, we square it
    # before using it, so we don't need the square root as described in the
    # algorithm. Instead we can just leave the result as is.
    dh = math.pow(da, 2) + math.pow(db, 2) - math.pow(dc, 2)

    sl = 1
    sc = 1 + k1 * c1
    sh = 1 + k2 * c1

    kc = 1
    kh = 1

    return math.sqrt(
        math.pow(dl / (kl * sl), 2) +
        math.pow(dc / (kc * sc), 2) +
        # Square root just the denominator as `dh` is already squared.
        dh / math.pow(kh * sh, 2)
    )


def delta_e_cmc(color1, color2, l=2, c=1):
    """
    Delta E CMC.

    http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CMC.html
    """

    lab1 = color1.convert("lab")
    lab2 = color2.convert("lab")

    l1, a1, b1 = util.no_nan(lab1.coords())
    c1 = math.sqrt(math.pow(a1, 2) + math.pow(b1, 2))
    l2, a2, b2 = util.no_nan(lab2.coords())
    c2 = math.sqrt(math.pow(a2, 2) + math.pow(b2, 2))

    dl = l1 - l2
    dc = c1 - c2

    da = a1 - a2
    db = b1 - b2

    # We never reference `dh` until the very end, and when we do, we square it
    # before using it, so we don't need the square root as described in the
    # algorithm. Instead we can just leave the result as is.
    dh = math.pow(da, 2) + math.pow(db, 2) - math.pow(dc, 2)

    if l1 < 16:
        sl = 0.511
    else:
        sl = (0.040975 * l1) / (1 + 0.01765 * l1)

    sc = ((0.0638 * c1) / (1 + 0.0131 * c1)) + 0.638

    h = math.atan2(b1, a1) * RAD2DEG

    if h >= 0:
        h1 = h
    else:
        h1 = h + 360

    if 164 <= h1 <= 345:
        t = 0.56 + abs(0.2 * math.cos((h1 + 168) * DEG2RAD))
    else:
        t = 0.36 + abs(0.4 * math.cos((h1 + 35) * DEG2RAD))
    c1_4 = math.pow(c1, 4)
    f = math.sqrt(c1_4 / (c1_4 + 1900))

    sh = sc * ((f * t) + 1 - f)

    return math.sqrt(
        math.pow(dl / (l * sl), 2) +
        math.pow(dc / (c * sc), 2) +
        # Square root just the denominator as `dh` is already squared.
        dh / math.pow(sh, 2)
    )


def delta_e_2000(color1, color2, kl=1, kc=1, kh=1, **kwargs):
    """
    Calculate distance doing a direct translation of the algorithm from the CIE Delta E 2000 paper.

    TODO: this is a lot of math, we need to go through and comment this up.

    We denoted prime (L') with trailing 'p' and mean is represented with a trailing 'm'.
    Delta has a preceding 'd'. I'm not sure I was completely consistent.

    http://www2.ece.rochester.edu/~gsharma/ciede2000/ciede2000noteCRNA.pdf
    """

    lab1 = color1.convert("lab")
    lab2 = color2.convert("lab")

    l1, a1, b1 = util.no_nan(lab1.coords())
    c1 = math.sqrt(math.pow(a1, 2) + math.pow(b1, 2))
    l2, a2, b2 = util.no_nan(lab2.coords())
    c2 = math.sqrt(math.pow(a2, 2) + math.pow(b2, 2))

    cm = (c1 + c2) / 2

    c7 = math.pow(cm, 7)
    g = 0.5 * (1 - math.sqrt(c7 / (c7 + G_CONST)))

    ap1 = (1 + g) * a1
    ap2 = (1 + g) * a2

    cp1 = math.sqrt(math.pow(ap1, 2) + math.pow(b1, 2))
    cp2 = math.sqrt(math.pow(ap2, 2) + math.pow(b2, 2))

    hp1 = 0 if (ap1 == 0 and b1 == 0) else math.atan2(b1, ap1)
    hp2 = 0 if (ap2 == 0 and b2 == 0) else math.atan2(b2, ap2)

    hp1 = (hp1 + 2 * math.pi if hp1 < 0.0 else hp1) * RAD2DEG
    hp2 = (hp2 + 2 * math.pi if hp2 < 0.0 else hp2) * RAD2DEG

    dl = l2 - l1
    dc = cp2 - cp1

    hdiff = hp2 - hp1
    habs = abs(hdiff)
    if cp1 == 0.0 and cp2 == 0.0:
        dh = 0.0
    elif habs <= 180.0:
        dh = hdiff
    elif hdiff > 180.0:
        dh = hdiff - 360
    elif hdiff < -180:
        dh = hdiff + 360

    dh = 2 * math.sqrt(cp2 * cp1) * math.sin(dh * DEG2RAD / 2)

    cpm = (cp1 + cp2) / 2
    lpm = (l1 + l2) / 2

    hsum = hp1 + hp2
    if cp1 == 0 and cp2 == 0:
        hpm = hsum
    elif habs <= 180:
        hpm = hsum / 2
    elif hsum < 360:
        hpm = (hsum + 360) / 2
    else:
        hpm = (hsum - 360) / 2

    t = (
        1 -
        (0.17 * math.cos((hpm - 30) * DEG2RAD)) +
        (0.24 * math.cos(2 * hpm * DEG2RAD)) +
        (0.32 * math.cos(((3 * hpm) + 6) * DEG2RAD)) -
        (0.20 * math.cos(((4 * hpm) - 63) * DEG2RAD))
    )

    dt = 30 * math.exp(-1 * math.pow(((hpm - 275) / 25), 2))

    cpm7 = math.pow(cpm, 7)
    rc = 2 * math.sqrt(cpm7 / (cpm7 + G_CONST))
    l_temp = math.pow(lpm - 50, 2)
    sl = 1 + ((0.015 * l_temp) / math.sqrt(20 + l_temp))
    sc = 1 + 0.045 * cpm
    sh = 1 + 0.015 * cpm * t
    rt = -1 * math.sin(2 * dt * DEG2RAD) * rc

    return math.sqrt(
        math.pow((dl / (kl * sl)), 2) +
        math.pow((dc / (kc * sc)), 2) +
        math.pow((dh / (kh * sh)), 2) +
        rt * (dc / (kc * sc)) * (dh / (kh * sh))
    )


class Distance:
    """Color distancing."""

    def delta_e(self, color, method=None, **kwargs):
        """Delta E distance."""

        if method is None:
            method = self.parent.DELTA_E

        algorithm = method.lower()
        if algorithm not in SUPPORTED:
            raise ValueError("'{}' is not currently a supported distancing algorithm.".format(algorithm))

        return globals()['delta_e_{}'.format(algorithm.replace('-', '_'))](self, color, **kwargs)

    def distance(self, color, space="lab"):
        """Delta."""

        return distance_euclidean(self, color, space=space)
