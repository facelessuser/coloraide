# Gamut Mapping

## Overview

Many color spaces have limits the colors they can accurately represent. This is the color gamut. The bounds represent
the limits in which a color space can represent a color. Some color spaces are theoretically unbounded, but past a
point, the eye can't see them.

When moving from a large color space like Lab to a small color space like sRGB, many Lab colors will not fit without
mapping the color to one that does fit. This "fitting" of the color from one gamut into another is called gamut mapping.

## Checking Gamut

A color can be checked to see if it fits in its own gamut or the gamut of another color space. Some color spaces may
have suggested limits for usability purposes, but may not have actual limits.

Let's assume we may have a color `#!color rgb(30% 105% 0%)` which is not in its own gamut as the blue channel exceeds
the sRGB limit of `100%`. We can check this via the `in_gamut` method, and we can see that it is not in gamut.

```pycon3
>>> Color("rgb(30% 105% 0%)").in_gamut()
False
```

We can also test if a color from one color space fits in a completely different color space. In the example below, we
can see that the LCH color of `#!color lch(100% 50 75)` is outside the narrow gamut of sRGB.

```pycon3
>>> Color("lch(100% 50 75)").in_gamut("srgb")
False
```

## Mapping Colors

The recommended approach for fitting/mapping a color is to compress the chroma while in the Lch color space (overly
simplified). This is the approach that our reference ([`colorjs`](https://colorjs.io/)) chose, so we ported it over here
as well.

In this example, we will take the color `#!color lch(100% 50 75)`. LCH's gamut is technically unbounded, but if we try
to fit it in the sRGB gamut, as noted earlier, it is outside the narrow gamut of sRGB. So, using the `fit` method, and
specifying `srgb` as the target color space, the color will changed to `#!color lch(99.437% 5.219 99.729)` which now
fits into the sRGB color gamut.

```pycon3
>>> Color("lch(100% 50 75)").fit("srgb").to_string()
'lch(99.437% 5.219 99.729)'
```

If desired, simple clipping can be used instead of the default gamut fitting. Generally this is not recommended, but
there are times and places for everything. To do so, the fitting method can be specified via the `method` parameter.
Here, we take the same color in the previous example (`#!color lch(100 50 75)`) and perform a simple clipping to get
`#!color lch(95.815% 42.312 96.915)`. Notice the difference when compared to the previous fitting result:
`#!color lch(99.437% 5.219 99.729)`.

```pycon3
>>> Color("lch(100% 50 75)").fit("srgb", method="clip").to_string()
'lch(95.815% 42.312 96.915)'
```

Gamut fitting will always return a new color unless `in_place` is set `True`.
