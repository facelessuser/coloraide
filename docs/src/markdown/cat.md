# Chromatic Adaptation

## Overview

Chromatic adaptation is the human visual system's ability to adjust to changes in illumination in order to preserve the
appearance of object colors. It is responsible for the stable appearance of object colors despite the wide variation of
light which might be reflected from an object and observed by our eyes. A chromatic adaptation transform (CAT) function
emulates this important aspect of color perception in color appearance models.

In short, colors look different under different lights. Viewing a color in daylight will look different than viewing it
by candle light. Color spaces usually define a reference illuminant that clarifies the assumed lighting for the given
space. For instance, sRGB is a color space defined with an illuminant of D65 (light in the shade - no direct sunlight -
at noon). On the other hand, the ProPhoto RGB space a uses D50 illuminant (direct sunlight at noon). A given color under
one illuminant would look different under the other.

Often, when converting a color to a new illuminant, it is desired to have the new color look the same as the first under
the new illuminant. A CAT can predict what that corresponding color under the new illuminant would have to be in order
to look the same as the original color under the original illuminant.

When translating a color from one illuminant to another, it is often desirable to represent that color under the new
illuminant such that it appears to the eye the same as it did under the original illuminant. CATs are used to predict
what the new color under the new illuminant should be in order to fulfill these requirements.

For a quick example, we can demonstrate the basic principle when translating a color in the XYZ color space from a D50
illuminant to a D65 illuminant. Below, we can see that the colors look pretty much the same, even though they are now
described under different illuminants.

```playground
d50 = Color('color(xyz-d50 0.11627 0.07261 0.23256 / 1)')
d65 = d50.convert('xyz-d65')
d50, d65
```

Under the hood, this is using the Bradford CAT (ColorAide's default CAT). Additionally, when translating from one color
space to another, colors usually pass through an XYZ conversion as a common way point where a given CAT is applied.

So we can actually do this manually and compare the results to what we did above. In order to this, we need to provide
the specified "white point" for the source color and the "white point" for the destination color along with the XYZ
coordinates we wish to transform:

```playground
from coloraide.color.convert import cat
Color('color(xyz-d50 0.11627 0.07261 0.23256 / 1)').convert('xyz-d65').coords()
cat.chromatic_adaptation("D50", "D65", [0.11627, 0.07261, 0.23256], method='bradford')
```

## Changing the Default CAT

Changing the default CAT is easy and follows the same pattern as the rest of the
[available class overrides](./color.md#override-default-settings). Simply derive a new `#!py3 Color()` class from the
original and override the `CHROMATIC_ADAPTATION` property with the [name of the desired CAT](#supported-cats).
Afterwards, all color transforms will use the specified CAT.

```playground
class Custom(Color):
    CHROMATIC_ADAPTATION = 'cat02'

d50 = Custom('color(xyz-d50 0.11627 0.07261 0.23256 / 1)')
d65 = d50.convert('xyz-d65')
d50, d65
```

## Supported CATs

There are various CATs, all varying in complexity and accuracy. We will not go through all of them and instead will
leave that up to the user to research as needed. Suffice it to say though that the Bradford CAT is currently the
industry standard (in most cases), but there are a variety options available, and research continues to try and improve
upon CATs of the past to come up with a better CAT for the future.

Currently, ColorAide mainly supports von Kries type CATs (named after an early 20th century color scientist), or CATs
that are similar to and/or are built upon the original von Kries CAT. We also do not currently support every known von
Kries CAT out there, but a good number are available. In the future, support may be expanded.

CAT           |
------------- |
`bradford`    |
`von-kries`   |
`xyz-scaling` |
`sharp`       |
`cat02`       |
`cat16`       |
`cmccat97`    |
`cmccat2000`  |
