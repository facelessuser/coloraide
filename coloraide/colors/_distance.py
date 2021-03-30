import math
from .. import util

G_CONST = 25 ** 7
SUPPORTED = frozenset(["76", "2000", "cmc", "94"])


def distance_euclidean(color1, color2, space="lab", **kwargs):
    """
    Euclidean distance.

    https://en.wikipedia.org/wiki/Euclidean_distance
    """

    lab1 = color1.convert(space)
    lab2 = color2.convert(space)

    coords1 = util.no_nan(lab1.coords())
    coords2 = util.no_nan(lab2.coords())

    return math.sqrt(sum((x - y) ** 2.0 for x, y in zip(coords2, coords1)))


def delta_e_76(color1, color2, **kwargs):
    """
    Delta E 1976 color distance formula.

    http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CIE76.html

    Basically this is Euclidean distance in the Lab space.
    """

    # Equation (1)
    return distance_euclidean(color1, color2, space="lab")


def delta_e_94(color1, color2, kl=1, k1=0.045, k2=0.015):
    """
    Delta E 1994 color distance formula.

    http://www.brucelindbloom.com/Eqn_DeltaE_CIE94.html
    """

    lab1 = color1.convert("lab")
    lab2 = color2.convert("lab")

    l1, a1, b1 = util.no_nan(lab1.coords())
    l2, a2, b2 = util.no_nan(lab2.coords())

    # Equation (5)
    c1 = math.sqrt(a1 ** 2 + b1 ** 2)

    # Equation (6)
    c2 = math.sqrt(a2 ** 2 + b2 ** 2)

    # Equation  (2)
    dl = l1 - l2

    # Equation  (3)
    dc = c1 - c2

    # Equation (7)
    da = a1 - a2

    # Equation  (8)
    db = b1 - b2

    # Equation (4)
    # We never reference `dh` until the very end, and when we do, we square it
    # before using it, so we don't need the square root as described in the
    # algorithm. Instead we can just leave the result as is.
    dh = da ** 2 + db ** 2 - dc ** 2

    # Equation (9)
    sl = 1

    # Equation (10)
    sc = 1 + k1 * c1

    # Equation (11)
    sh = 1 + k2 * c1

    # Equation (12)
    # Provided by `kl`

    # Equation (13)
    kc = 1

    # Equation (14)
    kh = 1

    # Equation (15) and Equation (16)
    # Provided by `k1` and `k2`

    # Equation (1)
    return math.sqrt(
        (dl / (kl * sl)) ** 2 +
        (dc / (kc * sc)) ** 2 +
        # Square root just the denominator as `dh` is already squared.
        dh / ((kh * sh) ** 2)
    )


def delta_e_cmc(color1, color2, l=2, c=1):
    """
    Delta E CMC.

    http://www.brucelindbloom.com/index.html?Eqn_DeltaE_CMC.html
    """

    lab1 = color1.convert("lab")
    lab2 = color2.convert("lab")

    l1, a1, b1 = util.no_nan(lab1.coords())
    l2, a2, b2 = util.no_nan(lab2.coords())

    # Equation (3)
    c1 = math.sqrt(a1 ** 2 + b1 ** 2)

    # Equation (4)
    c2 = math.sqrt(a2 ** 2 + b2 ** 2)

    # Equation (2)
    dc = c1 - c2

    # Equation (6)
    dl = l1 - l2

    # Equation (7)
    da = a1 - a2

    # Equation (8)
    db = b1 - b2

    # Equation (5)
    # We never reference `dh` until the very end, and when we do, we square it
    # before using it, so we don't need the square root as described in the
    # algorithm. Instead we can just leave the result as is.
    dh = da ** 2 + db ** 2 - dc ** 2

    # Equation (9)
    if l1 < 16:
        sl = 0.511
    else:
        sl = (0.040975 * l1) / (1 + 0.01765 * l1)

    # Equation (10)
    sc = ((0.0638 * c1) / (1 + 0.0131 * c1)) + 0.638

    # Equation (14)
    h = math.degrees(math.atan2(b1, a1))

    # Equation (15)
    if h >= 0:
        h1 = h
    else:
        h1 = h + 360

    # Equation (12)
    if 164 <= h1 <= 345:
        t = 0.56 + abs(0.2 * math.cos(math.radians(h1 + 168)))
    else:
        t = 0.36 + abs(0.4 * math.cos(math.radians(h1 + 35)))

    # Equation (13)
    c1_4 = c1 ** 4
    f = math.sqrt(c1_4 / (c1_4 + 1900))

    # Equation (11)
    sh = sc * (f * t + 1 - f)

    # Equation (1)
    return math.sqrt(
        (dl / (l * sl)) ** 2 +
        (dc / (c * sc)) ** 2 +
        # Square root just the denominator as `dh` is already squared.
        dh / (sh ** 2)
    )


def delta_e_2000(color1, color2, kl=1, kc=1, kh=1, **kwargs):
    """
    Calculate distance doing a direct translation of the algorithm from the CIE Delta E 2000 paper.

    We denoted prime (L') with trailing 'p' and mean is represented with a trailing 'm'.
    Delta has a preceding 'd'. I'm not sure I was completely consistent.

    http://www2.ece.rochester.edu/~gsharma/ciede2000/ciede2000noteCRNA.pdf
    """

    lab1 = color1.convert("lab")
    lab2 = color2.convert("lab")

    l1, a1, b1 = util.no_nan(lab1.coords())
    l2, a2, b2 = util.no_nan(lab2.coords())

    # Equation (2)
    c1 = math.sqrt(a1 ** 2 + b1 ** 2)
    c2 = math.sqrt(a2 ** 2 + b2 ** 2)

    # Equation (3)
    cm = (c1 + c2) / 2

    # Equation (4)
    c7 = cm ** 7
    g = 0.5 * (1 - math.sqrt(c7 / (c7 + G_CONST)))

    # Equation (5)
    ap1 = (1 + g) * a1
    ap2 = (1 + g) * a2

    # Equation (6)
    cp1 = math.sqrt(ap1 ** 2 + b1 ** 2)
    cp2 = math.sqrt(ap2 ** 2 + b2 ** 2)

    # Equation (7)
    hp1 = 0 if (ap1 == 0 and b1 == 0) else math.atan2(b1, ap1)
    hp2 = 0 if (ap2 == 0 and b2 == 0) else math.atan2(b2, ap2)
    hp1 = math.degrees(hp1 + 2 * math.pi if hp1 < 0.0 else hp1)
    hp2 = math.degrees(hp2 + 2 * math.pi if hp2 < 0.0 else hp2)

    # Equation (8)
    dl = l2 - l1

    # Equation (9)
    dc = cp2 - cp1

    # Equation (10)
    hdiff = hp2 - hp1
    if cp1 * cp2 == 0.0:
        dh = 0.0
    elif abs(hdiff) <= 180.0:
        dh = hdiff
    else:
        # If not `hdiff > 180.0` and not `abs(hdiff) <= 180.0`
        # then it must be `hdiff < -180`
        offset = -360 if hdiff > 180.0 else 360
        dh = hdiff + offset

    # Equation (11)
    dh = 2 * math.sqrt(cp2 * cp1) * math.sin(math.radians(dh / 2))

    # Equation (12)
    lpm = (l1 + l2) / 2

    # Equation (13)
    cpm = (cp1 + cp2) / 2

    # Equation (14)
    hsum = hp1 + hp2
    if cp1 * cp2 == 0:
        hpm = hsum
    elif abs(hp1 - hp2) > 180:
        # if not `hsum < 360`
        # then it must be `hsum >= 360`
        offset = 360 if hsum < 360 else -360
        hpm = (hsum + offset) / 2
    else:  # `abs(hp1 - hp2) <= 180`
        hpm = hsum / 2

    # Equation (15)
    t = (
        1 -
        (0.17 * math.cos(math.radians(hpm - 30))) +
        (0.24 * math.cos(math.radians(2 * hpm))) +
        (0.32 * math.cos(math.radians((3 * hpm) + 6))) -
        (0.20 * math.cos(math.radians((4 * hpm) - 63)))
    )

    # Equation (16)
    dt = 30 * math.exp(-1 * ((hpm - 275) / 25) ** 2)

    # Equation (17)
    cpm7 = cpm ** 7
    rc = 2 * math.sqrt(cpm7 / (cpm7 + G_CONST))

    # Equation (18)
    l_temp = (lpm - 50) ** 2
    sl = 1 + ((0.015 * l_temp) / math.sqrt(20 + l_temp))

    # Equation (19)
    sc = 1 + 0.045 * cpm

    # Equation (20)
    sh = 1 + 0.015 * cpm * t

    # Equation (21)
    rt = -1 * math.sin(math.radians(2 * dt)) * rc

    # Equation (22)
    return math.sqrt(
        (dl / (kl * sl)) ** 2 +
        (dc / (kc * sc)) ** 2 +
        (dh / (kh * sh)) ** 2 +
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
