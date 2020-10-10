# Gamut Mapping

## Overview

Many color spaces have bounds. The bounds represent the limits a color space can represent a color. Some color spaces
are theoretically unbounded, but past a point, the eye can't see them.

When moving from a large color space like Lab to a small color space like sRGB, many Lab colors will not fit without
mapping to the color to one that does fit.

## Checking Gamut

A color can be checked to see if it fits in its own gamut or the gamut of another color space. Some color spaces may
have recommended limits for usability purposes, but may not have actual limits.

Let's assume we may have a color `#!color rgb(30% 105% 0%)` which is not in its own gamut. We can check this via the
`in_gamut` method, and we can see that it is not in gamut.

```pycon3
>>> Color("rgb(30% 105% 0%)").in_gamut()
False
```

We can also check if a color space that is not in sRGB is in sRGB gamut as well. By doing this, we can quickly see that
`#!color lch(100% 50 75)` is not in gamut.

```pycon3
>>> Color("lch(100% 50 75)").in_gamut("srgb")
False
```

## Mapping Colors

An often recommended approach for mapping colors is to compress the chroma while in the Lch color space (overly
simplified). This is the approach that our reference ([`colorjs`](https://colorjs.io/)) chose, so we ported it over here
as well.

In this example, we will take the color `#!color lch(100% 50 75)`, which is out of the sRGB gamut, and fit it. After
fitting, we get a color that can now be rendered in the sRGB color space:

If desired we can force the color in gamut via the `fit` method. By doing this, we get a color we can render in the
sRGB color space: `#!color lch(99.438% 5.2201 99.658)`.


```pycon3
>>> Color("lch(100% 50 75)").fit("srgb").to_string()
'lch(99.438% 5.2201 99.658)'
```

If desired, simple clipping can be used instead of the default gamut fitting. Generally this is not recommended, but
there are times and places for everything. To do so, you can specify the fitting method via the `method` parameter. Here
we take the same color in the previous example (`#!color lch(100% 50 75)`) and perform a simple clipping to get
`#!color lch(95.817% 42.313 96.905)`. Notice the difference when compared to the previous fitting result:
`#!color lch(99.438% 5.2201 99.658)`.

```pycon3
>>> Color("lch(100% 50 75)").fit("srgb", method="clip").to_string()
'lch(95.817% 42.313 96.905)'
```

Gamut fitting will always return a new color unless `in_place` is set `True`.