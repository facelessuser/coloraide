# Gamut Mapping

## Overview

Many color spaces have limits to the colors they can accurately represent. This is the color gamut. The bounds represent
the limits to which a color space can represent a color. Some color spaces are theoretically unbounded, but past a
point, the eye can't see them.

When moving from a large color space like CIELCH to a small color space like sRGB, many CIELAB colors will not fit
without mapping the color to one that does fit. This "fitting" of the color from one gamut into another is called gamut
mapping.

## Checking Gamut

A color can be checked to see if it fits in its own gamut or the gamut of another color space. Some color spaces may
have suggested limits for usability purposes, but may not have actual limits.

Let's assume we have a color `#!color-no-fit rgb(30% 105% 0%)` which is not in its own gamut as the green channel
exceeds the sRGB limit of `100%`. We can check this via the `in_gamut` method, and we can see that it is not in gamut.

```color
Color("rgb(30% 105% 0%)").in_gamut()
```

We can also test if a color from one color space fits in a completely different color space. In the example below, we
can see that the LCH color of `#!color-no-fit lch(100% 50 75)` is outside the narrow gamut of sRGB.

```color
Color("lch(100% 50 75)").in_gamut("srgb")
```

## Mapping Colors

The recommended approach for fitting/mapping a color is to compress the chroma while in the CIELCH color space (overly
simplified). This is the approach that our reference ([`colorjs`](https://colorjs.io/)) chose, so we ported it over here
as well.

In this example, we will take the color `#!color-no-fit lch(100% 50 75)`. CIELCH's gamut is technically unbounded, but
if we try to fit it in the sRGB gamut, as noted earlier, it is outside the narrow gamut of sRGB. So, using the `fit`
method, and specifying `srgb` as the target color space, we can fit it in the sRGB gamut.

```color
Color("lch(100% 50 75)").fit("srgb")
```

If desired, simple clipping can be used instead of the default gamut fitting. While gamut mapping via chroma compression
can give better results, gamut clipping is much faster and is actually what browsers do. So if your desire is to match
browsers, or speed is more important, clipping may be the way to go.

In this example, we can change the fitting `method` parameter to `clip`. Notice the difference when compared to the
previous fitting result:

```color
Color("lch(100% 50 75)").fit("srgb", method="clip")
Color("lch(100% 50 75)").fit("srgb")
```

If we wanted to change the default "fitting" to `clip`, we can also just use a
[class override](./color.md#override-default-settings). Doing this will default to `clip` any time a color needs
to be mapped. Though you can still use chroma compression by specifying `lch-chroma` for the `method`.

```color
class Custom(Color):
    FIT = 'clip'

Custom("lch(100% 50 75)").fit("srgb")
```

Gamut fitting will always return a new color unless `in_place` is set `#!py3 True`.

--8<--
playground.txt

refs.txt
--8<--
