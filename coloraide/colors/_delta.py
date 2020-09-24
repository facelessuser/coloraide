import math

G_CONST = math.pow(25, 7)
RAD2DEG = 180 / math.pi
DEG2RAD = math.pi / 180


def delta_e2000(color, color2, kl=1, kc=1, kh=1):
    """
    Calculate distance doing a direct translation of the algorithm from the CIE delta2000 paper.

    TODO: this is a lot of math, we need to go through and comment this up.

    We denoted prime (L') with trailing 'p' and mean is represented with a trailing 'm'.
    Delta has a preceding 'd'. I'm not sure I was completely consistent.

    http://www2.ece.rochester.edu/~gsharma/ciede2000/ciede2000noteCRNA.pdf
    """

    lab1 = color.convert("lab")
    lab2 = color2.convert("lab")

    l1, a1, b1 = lab1.coords()
    c1 = math.sqrt(math.pow(a1, 2) + math.pow(b1, 2))
    l2, a2, b2 = lab2.coords()
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
