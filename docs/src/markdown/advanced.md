# Advanced Topics

Colors are complicated, and sometimes it may not be understood why colors or color transformations yield the results
that they do. Here we'd like to cover more advanced or specific topics that don't fit well in existing topics or are too
verbose to be included elsewhere.

## Round Trip Accuracy

In general, ColorAide is careful to provide good round trip conversions where practical. What this means is that we
try to maintain a high level of accuracy so that when a color is converted to a different color and then back, that
it will be very close, if not exactly, the same. We accomplish this by not not clipping values during conversion and
maintaining as high of precision as we can, but there are some cases where the round tripping accuracy cannot be
maintained at the same high level or at all, there are even reasons where we willfully choose to sacrifice accuracy for
convenience.

### Limitations of The Color Space

One situation that can cause bad round tripping is when one color model cannot properly handle a color due to its gamut
being beyond the conversion algorithms limits or other limitations in the color space.

Consider a wide gamut, HDR color space like Jzazbz. When it is converted to HSLuv, whose algorithm clamps any lightness
that exceeds the SDR range, the round trip is broken. This is just the nature of the HSLuv algorithm as it adheres to an
sRGB gamut that does not support HDR lightness.

```playground
jz = Color('color(--jzazbz 0.25 0 0)')
jz
hsluv = jz.convert('hsluv')
hsluv
hsluv.convert('jzazbz')
```

### Floating Point Math

Floating point math can also be responsible for some differences in round tripping. [Floating point issues][floating-point]
are not specific to this library or even the language of Python, but to all computers in general. For example, computers
cannot store infinite repeating decimals to properly represent all floating point numbers.


```playground
color = Color('white')
color[:]
color.convert('prophoto-rgb').convert('srgb')[:]
```

### Special Handling of Cylindrical Spaces

Sometimes, round trip accuracy can be compromised further for practical reasons. This does not mean round tripping
breaks, but the high degree of accuracy can drop some. A common case where this happens is with some cylindrical color
models.

ColorAide aims to make colors easy to use, and one way it does this is treating hues as powerless under reasonable
situations. One common issue people run into is with interpolating achromatic colors in cylindrical spaces. Achromatic
colors do not have a hue, so to get logical results, we set achromatic hues to `NaN`, which means the hue is undefined.
This prevents weird color shifts when interpolating between achromatic colors. Only if a user manually specifies a hue
do we respect it.

```playground
Color.interpolate(['lch(75 100 180)', 'lch(75 0 0)'], space='lch')
Color.interpolate(['lch(75 100 180)', 'lch(75 0 none)'], space='lch')
```

So that colors work the way people intend, ColorAide does its best during color conversion to identify when a color is
achromatic and a hue powerless. In these cases, the hue will be set to `NaN`, or `none` in CSS.

```playground
Color('white').convert('lch')
Color.interpolate(['cyan', 'white'], space='lch')
```

When determining if a cylindrical color's hue is powerless, it must often be based on attributes of the color space. As
an example, HSL is achromatic when lightness is 0 (black) or 1 (white) or when there is no color saturation. Where
things get tricky is that not all color spaces have perfect transformation algorithms. They may not handle out of gamut
colors well, the recommended algorithm may not provide the high level of precision to get a perfect 0 for saturation or
chroma, or floating point math simply cannot get the perfect conversion. Combine this with translating to and from many
different color spaces that all have such quirks, you can end up with colors that are meant to be achromatic, that
simply cannot be detected as such.

As an example, let's look at the conversion between Lab-ish and LCh-ish color spaces. In general, to convert a Lab-ish
color space to LCh-ish, you use the following formulas to transform a Lab color's `a` and `b` components to chroma and
hue:

```py
import math
chroma = math.sqrt(a ** 2 + b ** 2)
hue = math.degrees(math.atan2(b, a))
```

And to get back:

```py
import math
a = chroma * math.cos(math.radians(hue))
b = chroma * math.sin(math.radians(hue))
```

For a good number of Lab-ish color spaces, this will result in zero for chroma or extremely close to zero as `a` and `b`
will be zero or very near zero for achromatic colors. On the conversion back the extremely low chroma makes whatever the
hue is essentially meaningless.

```playground
import math
from coloraide import util
c = Color('gray').convert('lab')
c.to_string()
math.sqrt(c[1] ** 2 + c[2] ** 2)
util.constrain_hue(math.degrees(math.atan2(c[2], c[1])))
c = Color('gray').convert('oklab')
c.to_string()
math.sqrt(c[1] ** 2 + c[2] ** 2)
util.constrain_hue(math.degrees(math.atan2(c[2], c[1])))
```

But there are some color spaces whose transformation are not nearly so tight. Let's consider JzCzhz which is derived
from Jzazbz.

```playground
import math
c = Color('gray').convert('jzazbz')
c.to_string()
math.sqrt(c[1] ** 2 + c[2] ** 2)
```

We can see just from the conversion of `#!color gray` from sRGB to Jzazbz that `a` and `b` are already far enough from
zero that round to 5 decimal places is not not enough to get zeros. Then when we convert them to chroma, we get chroma
that is much larger than are previous examples. Still close enough to zero that we do not have to worry much about it,
but not nearly as close to zero as we would normally prefer.

We can see that with JzCzhz that the hue can have more influence on the conversion back even though the color
technically has no hue.

```playground
import math
from coloraide import util
color = Color('gray').convert('jzazbz')
color.to_string()
a1, b1 = color[1:3]
c = math.sqrt(a1 ** 2 + b1 ** 2)
h = util.constrain_hue(math.degrees(math.atan2(b1, a1)))
a2 = c * math.cos(math.radians(0))
b2 = c * math.sin(math.radians(0))
a2, a1
b1, b2
a3 = c * math.cos(math.radians(h))
b3 = c * math.sin(math.radians(h))
a3, a1
b3, b1
```

Unless you are a color scientist, no one wants to think about this when specifying white, or gray, they just want to set
chroma to zero and not think about hue.

```playground
Color.interpolate(['color(--jzczhz 0.16 0.2 180)', 'color(--jzczhz 0.227 0 none)'], space='jzczhz')
```

ColorAide figures this all out so the user doesn't have to. Since chroma's distance from zero can fluctuate a little
depending on the lightness, we use a threshold, as small as we can, to generally detect an achromatic color, then we 
will use a hue that is close enough to the ideal hue to give as good a conversion back as we can.

```playground
color = Color('gray').convert('jzazbz')
a1, b1 = color[1:3]
a2, b2 = color.convert('jzczhz').convert('jzazbz')[1:3]
a1, a2
b1, b2
```

If desired, the hue used can be acquired directly from ColorAide. This can be useful for plotting or other reasons.

```playground
color = Color('gray').convert('jzczhz')
color._space.achromatic_hue()
```

Obviously, with such approximation, round tripping will not be as precise, but the convenience of not having to think
about the proper hue or how close to zero the chroma needs to be in order to consider the color achromatic
is priceless.

Do keep in mind though, as there are color space transformation with wildly varying accuracy, even when we do all we
can, we can end up sometimes not able to predict an achromatic color as the transformations can cause values to fall
right outside our thresholds.

If in doubt, work directly in the color space of interest.
