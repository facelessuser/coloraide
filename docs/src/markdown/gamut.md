# Gamut Mapping

## Overview

Many color spaces have limits to the colors they can accurately represent. This is the color gamut. The bounds represent
the limits to which a color space can represent a color. Some color spaces are theoretically unbounded, but past a
point, the eye can't see them.

When moving from a large color space like CIELAB to a small color space like sRGB, many CIELAB colors will not fit
without mapping the color to one that does fit. This "fitting" of the color from one gamut into another is called gamut
mapping.

## Checking Gamut

When dealing with colors, it can be important to know whether a color is within its own gamut. The `in_gamut` function
allows for comparing the current color's specified values against the color space's gamut.

Let's assume we have a color `#!color rgb(30% 105% 0%)`. The color is out of gamut due to the green channel exceeding
the channel's limit of `#!py3 100%`. When we execute `in_gamut`, we can see that the color is not in its own gamut.

```playground
Color("rgb(30% 105% 0%)").in_gamut()
```

On the other hand, some colors do not have a limit, only suggested limits for usability. CIELAB does not really have
bounds as it is formulated in such a way that it can represent any color, even if they are not visible. When we check a
CIELAB color, we will find that it is always in gamut.

```playground
Color("lab(200% -20 40 / 1)").in_gamut()
```

While checking CIELAB's own gamut isn't very useful, we can test it against a different color space's gamut. By simply
passing in the name of a different color space, the current color will be converted to the provided space and then
will run `in_gamut` on the new color. You could do this manually, but using `in_gamut` in this manner can be very
convenient. In the example below, we can see that the CIELAB color of `#!color lab(200% -20 40 / 1)` is outside the
narrow gamut of sRGB.

```playground
Color("lab(200% -20 40 / 1)").in_gamut('srgb')
```

Generally, ColorAide does not round off values in order to guarantee the best possible values for round tripping, but
due to [limitations of floating-point arithmetic][floating-point], there can be edge cases where colors don't round trip
perfectly. By default, `in_gamut` allows for a tolerance of `#!py3 0.000075` to account for such cases where a color
is "close enough". If desired, this "tolerance" can be adjusted.

Let's consider CIELAB. The sRGB round trip through CIELAB for `#!color white` does not perfectly convert back to the
original color. We can see that when using a tolerance of zero, the color is considered out of gamut. Depending on what
you are doing, this may not be an issue up until you are ready to finalize the color, so sometimes it may be desirable
to have some tolerance, and other times not.

```playground
Color('color(srgb 1 1 1)').convert('lab').convert('srgb').coords()
Color('color(srgb 1 1 1)').convert('lab').convert('srgb').in_gamut()
Color('color(srgb 1 1 1)').convert('lab').convert('srgb').in_gamut(tolerance=0)
```

On the topic of tolerance, there are some spaces that inherently are based off gamuts of other spaces. For instance, the
cylindrical spaces HSL, HSV, and HWB are just different color models for the sRGB space, so their gamut is the same as
sRGB. So it stands to reason that simply using the sRGB gamut check for them should be sufficient, and if we are using
strict tolerance, this would make sense:

```playground
Color('rgb(255 255 255)').in_gamut('srgb', tolerance=0)
Color('hsl(0 0% 100%)').in_gamut('srgb', tolerance=0)
Color('color(--hsv 0 0% 100%)').in_gamut('srgb', tolerance=0)
Color('rgb(255.05 255 255)').in_gamut('srgb', tolerance=0)
Color('hsl(0 0% 100.05%)').in_gamut('srgb', tolerance=0)
Color('color(--hsv 0 0% 100.05%)').in_gamut('srgb', tolerance=0)
```

HWB is a little funny as values over 100% for whiteness and blackness are normalized, but the results are technically
correct as the value will convert to an sRGB value perfectly in gamut.

```playground
Color('hwb(0 100% 0%)').in_gamut('srgb', tolerance=0)
Color('hwb(0 100.05% 0%)').in_gamut('srgb', tolerance=0)
Color('hwb(0 100.05% 0%)').convert('srgb').coords()
```

But when using a tolerance check in a Cartesian model while in a cylindrical model, we can end up with some surprising
results. In this example, we have an sRGB color that is extremely close to being in gamut, but when we convert it to HSL
we can see wildly large saturation. There isn't anything technically wrong with this value as saturation and hue are
essentially meaningless when lightness is `#!py3 100%`, but this may be undesirable to a user.

```playground
hsl = Color('color(srgb 0.9999999999994 1.0000000000002 0.9999999999997)').convert('hsl')
hsl
hsl.in_gamut('srgb')
```

For this reason, if passing in `hsl`, `hsv`, or `hwb` as gamut inputs, the tolerance is also compared not only against
the Cartesian coordinates, but also the cylindrical coordinates. In this way, we are still checking that the colors are
in the sRGB gamut, but the tolerance is now relative to the constraints of the cylindrical color model.

There is no HSL, HSV, and HWB gamuts as these are just alternative models for RGB based colors. One could easily map the
Display P3 color space, which has a different gamut, to one of these models.

We can see below that now the gamut check will fail. If the color is an HSL color, we do not have to specify `hsl`, as
it will be the default for that color space, but we specify it below just for illustration.

```playground
hsl = Color('color(srgb 0.9999999999994 1.0000000000002 0.9999999999997)').convert('hsl')
hsl
hsl.in_gamut('hsl')
```

We can also see that the tolerance is now relative to the color model:

```playground
hsl = Color('hsl(140 100.000002% 0%)')
hsl.convert('srgb').coords()
hsl.in_gamut('hsl')
```

But don't worry, the tolerance constraint above isn't _solely_ based on the HSL coordinates. If the color deviates past
the threshold for sRGB **or** HSL, the gamut will yield `#!py3 False`. It is simply an extra check added that ensures
the tolerance is compared against both the Cartesian coordinates and the cylindrical coordinates to ensure that we are
working with sane values.

If the Cartesian check is the only desired check, and the strange cylindrical values that are returned are not a
problem, `srgb` can always be specified. `#!py3 tolerance=0` can always be used to constrain the check to values exactly
in the gamut.

## Mapping Colors

Gamut mapping is the process of taking a color that is out of gamut and adjusting it such that it fits within the gamut.
There are various different ways to gamut map a color into a smaller gamut. Currently, ColorAide provides three methods:

Method         | Description
-------------- | -----------
`clip`         | Simple, naive clipping.
`oklch-chroma` | Two stage mapping that uses a combination of chroma compression and clipping. Chroma compression is done in the Oklch color space and is what is currently specified in the [CSS Level 4 specification](https://drafts.csswg.org/css-color/#binsearch). This is the default method used.
`lch-chroma`   | This is like `oklch-chroma` but is done with CIELCH. This is what ColorAide originally used before `oklch-chroma`. Hue preservation is not as good, but has been left in for those who prefer this legacy method.

In this example, we will take the color `#!color lch(100% 50 75)`. CIELCH's gamut is technically unbounded, but when we
convert the color to sRGB, we find that the color is out of gamut. So, using the `fit` method, we can actually transform
the color to one that fits in the sRGB space and gives a color that represents the intent of the larger color as best we
can. As the color's lightness is so high, when fitting, we essentially end up with `#!color white`.

```playground
rgb = Color("lch(100% 50 75)").convert('srgb')
rgb.in_gamut()
rgb.coords()
rgb.fit()
```

If desired, simple clipping can be used instead of the default gamut mapping. Clipping is a naive way to fit a color as
it simply truncates any color channels whose values are too big. While gamut mapping via chroma compression can give
better results, gamut clipping is much faster and is actually what browsers currently do. If your desire is to match how
browsers handle out of gamut color or if you have a specific reason to favor this approach, clipping may be the way to
go.

Clipping can simply be done using the `clip` method. Notice the difference when compared to the previous fitting
results. We now end up with a very yellow-ish color.

```playground
Color("lch(100% 50 75)").clip("srgb")
Color("lch(100% 50 75)").fit("srgb")
```

Color objects could potentially install other gamut fitting methods via plugins. If more are available, you can specify
which one to use via the `method` parameter. `clip` is a reserved method and is always available. `clip` is provided
this way to ensure any functions, like `to_string`, that allow for specifying the gamut mapping method dynamically can
always use `clip`.

```playground
Color("lch(100% 50 75)").fit("srgb", method='clip')
```

If we wanted to change the default "fitting" to `clip`, we can also just use a
[class override](./color.md#override-default-settings). Doing this will cause the class to default to `clip` any time a
color needs to be mapped. Though, you can still use chroma compression by specifying `oklch-chroma` for the `method`.

```playground
class Custom(Color):
    FIT = 'clip'

Custom("lch(100% 50 75)").convert('srgb').fit()
Custom("lch(100% 50 75)").convert('srgb').fit(method='oklch-chroma')
```

It is important to note that when using fit, there is no tolerance, so even if `in_gamut` allowed enough tolerance to
consider a color within the gamut, calling `fit` will fit any color that is not exactly in gamut.

```playground
lab = Color('lab(100% 0 0)')
srgb = lab.convert('srgb')
srgb.in_gamut()
srgb.coords()
srgb.fit().coords()
```

And much like [gamut checking](#gamut-checking), we can fit a color in a different color space.

```playground
Color("lch(100% 50 75)").fit('srgb')
```

When fitting in another color space, results may vary depending on what color space you are in and what color space you
are using to fit the color. We went into great depths when discussing [gamut checking](#gamut-checking) about how
transform functions from one color space to another are not always exact. We also gave quite a number of examples
showing cases in which some color spaces were more sensitive to slight deviations from their gamut than others. This is
mainly mentioned as fitting in one color space and round tripping back may not give exact results:

```playground
Color("lch(100% 50 75)").convert('srgb').fit().coords()
Color("lch(100% 50 75)").fit('srgb').convert('srgb').coords()
```

Depending on what you are doing, and what spaces you are working in, it may make sense to fully convert to a space and
work directly in that space opposed to the indirect fitting of a color in a different color space.
