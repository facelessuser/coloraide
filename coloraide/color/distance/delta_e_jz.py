"""
Delta E z.

https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272
"""
import math
from ... import util


def distance(color, sample, **kwargs):
    """Delta E z color distance formula."""

    jz1, az1, bz1 = util.no_nan(color.convert('jzazbz').coords())
    jz2, az2, bz2 = util.no_nan(sample.convert('jzazbz').coords())

    cz1 = math.sqrt(az1 ** 2 + bz1 ** 2)
    cz2 = math.sqrt(az2 ** 2 + bz2 ** 2)

    hz1 = math.atan2(bz1, az1)
    hz2 = math.atan2(bz2, az2)

    djz = jz1 - jz2
    dcz = cz1 - cz2
    dhz = 2 * math.sqrt(cz1 * cz2) * math.sin((hz1 - hz2) / 2)

    return math.sqrt(djz ** 2 + dcz ** 2 + dhz ** 2)
