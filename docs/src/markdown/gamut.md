# Gamut Mapping

## Overview

Many color spaces are designed in such a way that they can only represent colors accurately within a specific range.
This range in which a color can accurately be represented is known as the color gamut. Some color spaces are
theoretically unbounded, but past a point, the eye can't see them anyways.

CIELAB is a color space that has no real defined. When translating a color from such a large color space as CIELAB to a
small color space like sRGB, there are many colors that simply cannot be represented within the space. In order to
visually represent a color outside of the gamut, a suitable color within the gamut must be selected to be shown in its
place. This selecting of a suitable replacement is called gamut mapping.

## Checking Gamut

When dealing with colors, it can be important to know whether a color is within its own gamut. The `in_gamut` function
allows for comparing the current color's specified values against the color space's gamut.

Let's assume we have a color `#!color rgb(30% 105% 0%)`. The color is out of gamut due to the green channel exceeding
the channel's limit of `#!py3 100%`. When we execute `in_gamut`, we can see that the color is not in its own gamut.

```playground
Color("rgb(30% 105% 0%)").in_gamut()
```

On the other hand, some color spaces do not have a limit. CIELAB is one such color space. Sometimes limits will be
placed on the color space channels for practicality, but theoretically, there are no bounds. When we check a CIELAB
color, we will find that it is always considered in gamut.

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

### Tolerance

Generally, ColorAide does not round off values in order to guarantee the best possible values for round tripping, but
due to [limitations of floating-point arithmetic][floating-point] and precision of conversion algorithms, there can be
edge cases where colors don't round trip perfectly. By default, `in_gamut` allows for a tolerance of `#!py3 0.000075` to
account for such cases where a color is "close enough". If desired, this "tolerance" can be adjusted.

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

But when we are not using a strict threshold, and we check one of these models **only** using the sRGB gamut, there are
some cases where these cylindrical colors can exhibit coordinates wildly outside of the model's range but still very
close to the sRGB gamut.

In this example, we have an sRGB color that is extremely close to being in gamut, but when we convert it to HSL,
we can see wildly large saturation.

```playground
hsl = Color('color(srgb 0.9999999999994 1.0000000000002 0.9999999999997)').convert('hsl')
hsl.to_string(fit=False)
hsl.in_gamut('srgb')
```

There is actually no inherent color gamut for the HSL, HSV, and HWB model as any RGB color space could be represented
in one of these cylindrical models. One could easily map the Display P3 color space to one of these cylindrical modes
creating an HSL Display P3 color, but the models do have constraints to ensure sane color coordinates that make sense.

For this reason, gamut checks in the HSL, HSV, or HWB models apply tolerance checks on the color's coordinates in the
sRGB color space **and** the respective cylindrical model ensuring we have coordinates that are inside the color's
actual gamut and that they are sanely within the cylindrical model's constraints as well.

So, when using HSL as the gamut check, we can see that it ensures the color is not only within the sRGB gamut, but that
its coordinates are also sanely within the model's constraints.

```playground
hsl = Color('color(srgb 0.9999999999994 1.0000000000002 0.9999999999997)').convert('hsl')
hsl
hsl.in_gamut('hsl')
```

Essentially, this forces a tighter constraint to ensure the colors represented in one of these cylindrical space aren't
wildly out of the model's range even if they are technically close to being in gamut.

If the Cartesian check is the only desired check, and the strange cylindrical values that are returned are not a
problem, `srgb` can always be specified. `#!py3 tolerance=0` can always be used to constrain the check to values exactly
in the gamut.

Additionally, there may be other color spaces that play a little loose with the gamut during their conversion. For
instance, Okhsv, an HSV model built off of Oklab, has a conversion back to sRGB that is simply not as precise as HSL or
HSV to sRGB. There is nothing actually wrong with our implementation of the conversion algorithm, as it matches the
behavior of the official implementation, the algorithm just isn't concerned with exactly translating the colors
perfectly within the sRGB gamut. Simply clipping the color can clean it up nicely, and if desired, we can always tweak
the tolerance.

```playground
okhsv = Color('color(--okhsv 20 100% 75% / 1)')
okhsv.in_gamut()
okhsv.convert('srgb')
okhsv.in_gamut(tolerance=0.0005)
```

## Mapping Colors

Gamut mapping is the process of taking a color that is out of gamut and adjusting it such that it fits within the gamut.
While there are various different ways to gamut map a color into a smaller gamut, ColorAide currently provides only
three:

Method         | Description
-------------- | -----------
`clip`         | Simple, naive clipping.
`lch-chroma`   | Uses a combination of chroma reduction and MINDE in the CIELCH color space to bring a color into gamut. This is the default method used.
`oklch-chroma` | Like `lch-chroma`, but uses the Oklch color space instead. Currently experimental and closer to the current proposed [CSS Color Level 4 specification](https://drafts.csswg.org/css-color/#binsearch).

!!! note "CSS Level 4 Gamut Mapping"
    The current [CSS Level 4 specification](https://drafts.csswg.org/css-color/#binsearch) describes the suggested gamut
    mapping algorithm as a combination of chroma reduction and MINDE. While our approach is actually very similar, it
    does differ a little. The CSS algorithm:

    1. Currently uses Oklch which we've found to be problematic in some circumstances.
    2. Is quicker to settle on a mapped color, but comes at the cost of sometimes reducing chroma too aggressively.

    We've currently replaced Oklch with CIELCH which avoids some of the issues found with Oklch. We also have adjusted
    the algorithm to be less aggressive in regards to chroma reduction at the cost of some performance.

    The CSS Level 4 algorithm is very new and likely to go through some revisions to address some of the issues. When
    the algorithm becomes more stable, we may align more closely or at the very least provide the official CSS approach
    as an option.

In order to demonstrate gamut mapping, in this example, we will take the color `#!color lch(100% 50 75)`. CIELCH's gamut
is technically unbounded, but when we convert the color to sRGB, we find that the color is out of gamut. So, using the
`fit` method, we can actually transform the color to one that fits in the sRGB space and gives a color that represents
the intent of the larger color as best we can. As the color's lightness is so high, when fitting, we essentially end up
with `#!color white`.

```playground
rgb = Color("lch(100% 50 75)").convert('srgb')
rgb.in_gamut()
rgb.coords()
rgb.fit()
```

If desired, simple clipping can be used instead of the default gamut mapping. Clipping is a naive way to fit a color as
it simply truncates any color channels whose values are too big. While gamut mapping via chroma reduction and MINDE can
give better results, gamut clipping is much faster and is actually what browsers currently do. If your desire is to
match how browsers handle out of gamut color or if you have a specific reason to favor this approach, clipping may be
the way to go.

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
color needs to be mapped. Though, you can still use the chroma reduction/MINDE approach by specifying `lch-chroma` for
the `method`.

```playground
class Custom(Color):
    FIT = 'clip'

Custom("lch(100% 50 75)").convert('srgb').fit()
Custom("lch(100% 50 75)").convert('srgb').fit(method='lch-chroma')
```

It is important to note that when using fit, there is no tolerance, so even if `in_gamut` allowed enough tolerance to
consider a color within the gamut, calling `fit` will adjust it such that it fits without tolerance.

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
