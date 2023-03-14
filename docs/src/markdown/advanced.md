# Advanced Topics

Colors are complicated, and sometimes it may not be understood why colors or color transformations yield the results
that they do. Here we'd like to cover more advanced or specific topics that don't fit well in existing topics or are too
verbose to be included elsewhere.

## Round Trip Accuracy

In general, ColorAide is careful to provide good round trip conversions where practical. What this means is that we
try to maintain a high level of accuracy so that when a color is converted to a different color and back that it will be
very close, if not exactly, the same.

In general, we are able to keep decent round tripping by not not clipping values during conversion and maintaining as
high a level of precision as we can, but there are some cases where the high level of round trip accuracy cannot be
maintained, or even at all. There are even reasons where we willfully choose to sacrifice some accuracy for convenience
in order to uphold intuitive expectations for the user.

If you are a color scientist or you work in certain industries, there are definite reasons to uphold accuracy at all
costs, but sometimes, you just want the colors to do the what you expect them to do. ColorAide tries to live in the
space between. We try to provide accurate color round tripping except when it comes at the cost of practicality.

### Limitations of The Color Space

One situation that can affect round tripping is when one color model cannot properly handle a color due to its gamut
being beyond the conversion algorithm's capabilities.

Consider a wide gamut, HDR color space like Jzazbz. Jzazbz is an unbounded color space with plenty of headroom for HDR.
Now, let's compare it to HSLuv, an SDR color space derived from the Luv color space and confined to the sRGB gamut. It
is essentially a more perceptually uniform version of HSL, but the algorithm specifically requires lightness to be
clamped to the SDR range. If we convert an HDR color from Jzazbz to HSLuv, round trip will be broken as the color space
simply does not support the HDR range.

```py play
jz = Color('color(--jzazbz 0.25 0 0)')
jz
hsluv = jz.convert('hsluv')
hsluv
hsluv.convert('jzazbz')
```
If a color space algorithm does not support a specific color, the conversion may be clamped or come back with an
unexpected value.

### Floating Point Math

Floating point math can also be responsible for some differences in round tripping. [Floating point issues][floating-point]
are not specific to this library or even the language of Python, but to all computers in general. For example, computers
cannot store infinite repeating decimals to properly represent all floating point numbers.

What this means is that no matter how much floating point precision you maintain, some error is introduced when doing
floating point operations. Certain rounding conventions are used in order to average out the errors to stay as close as
possible to the intended, real value, but it does not prevent floating point errors. This is simply the nature of
computers and floating point math.

```py play
color = Color('white')
color[:]
color.convert('prophoto-rgb').convert('srgb')[:]
```

### Special Handling: RGB Cylindrical Spaces

Sometimes, round trip accuracy can be compromised further for practical reasons. A common case where we make compromises
is with cylindrical color models.

ColorAide aims to make colors easy to use, but the one case that can frustrate users is interpolating with an achromatic
color using a cylindrical color space.

Achromatic colors do not have a hue, but all conversions end up yielding something for hue, even it it has no practical
meaning. This can cause odd color shifts when interpolating with an achromatic color. In order to get logical results
when doing interpolation, we can set achromatic hues to `NaN` (or `none` in CSS), which means the hue is undefined. This
helps us to identify achromatic cases and helps us to prevent weird color shifts when interpolating between achromatic
colors. Only if a user manually defines a hue do we respect it.

```py play
Color.interpolate(['lch(75 100 180)', 'lch(75 0 0)'], space='lch')
Color.interpolate(['lch(75 100 180)', 'lch(75 0 none)'], space='lch')
```

Because of [floating point issues](#floating-point-math), conversions to cylindrical color spaces do not always satisfy
the requirements to be recognized as achromatic colors.

Consider the following example. HSL colors are achromatic when the sRGB color it is derived from has all color channels
equal to each other. Let's say we convert the color `#!color darkgray` to the XYZ D65 color space and then back again.
We can see that what was once was a color with all color channels equal to each other is now a color that has color
channels very nearly equal to each other.

```py play
c1 = Color('darkgray')
c1[:-1]
c2 = c1.convert('xyz-d65').convert('srgb')
c2[:-1]
```

These two colors are intended to be the same, but one satisfies the requirement to have the HSL hue set to `NaN`, but
the other does not. This is a case where accuracy vs practicality comes into play. We all know the color is essentially
still `#!color darkgray`, and that is what the user intends. To allow this to work seamlessly, we apply a little
leniency to the achromatic rules and state that if the color is very, very close to being achromatic, we will consider
it achromatic, and we sacrifice a little accuracy to gain practicality. Or maybe it is better say that we compensate for
the natural inaccuracies that exist.

```py play
Color('darkgray').convert('hsl')[:-1]
Color('darkgray').convert('xyz-d65').convert('hsl')[:-1]
```

A similar problem can occur with HSL near `#!color white`. If we take white and run it through XYZ, we'll get a value
not that is not only just slightly not achromatic, but values that are slightly out of range (above 1).

```py play
c1 = Color('white')
c1[:-1]
c2 = c1.convert('xyz-d65').convert('srgb')
c2[:-1]
```

Without any correction, we'd get the following:

```py
>>> Color('white').convert('xyz-d65').convert('hsl')[:]
[60.0, 0.5, 0.9999999999999998, 1.0]
```

Again, we all know this is `#!color white`, so we relax the rules a bit and say if a value is very, very close to max
lightness, we will consider saturation to be zero. This provides a little leniency if lightness is slightly over or
under.

```py play
Color('white').convert('hsl')[:-1]
Color('white').convert('xyz-d65').convert('hsl')[:-1]
```

Not all RGB cylindrical models have the exact same rules, but we apply similar logic to all HSL, HSV, and HWB like
models. The approach might be slightly different depending on the model, but the idea is the same.

### Special Handling: LCh Cylindrical Spaces

Lastly, LCh like cylindrical models have a similar issues as the RGB cylindrical models. Since the algorithms are
usually consistent even when extending from SDR to HDR, lightness can usually exceed the upper boundary without the
algorithm breaking down. As a matter of fact, there are a number of LCh models that are based on HDR color spaces. The
real issue is that many of these color spaces do not always have their contrast resolve perfectly to their lower limit
(usually zero) to signify an achromatic color. So, just like with RGB cylindrical models, when contrast gets very, very
close to the lower limit, we consider the hue to be undefined and set it to `NaN`.

```py play
Color('darkgray').convert('lch')[:]
```

Some may have the bottom chroma limit rise slightly as the achromatic colors approach and surpass `#!color white`. We
can see this behavior occur with JzCzhz:

```py play
Color('color(srgb 0 0 0)').convert('jzczhz')[:]
Color('color(srgb 0.5 0.5 0.5)').convert('jzczhz')[:]
Color('color(srgb 1 1 1)').convert('jzczhz')[:]
Color('color(--rec2100-pq 1 1 1)').convert('jzczhz')[:]
```

Generally, as long as the lower chroma limit is quite low, the hue value has little impact on the conversion back and we
can set a lower threshold such that any chroma that falls below that threshold can be considered achromatic. Generally,
conversion will be pretty good, but some round trip accuracy is lost when the lower chroma limit is slightly larger.

For spaces that have a larger chroma limit like JzCzhz has, we may even track the ideal hue to use in the conversion
back from an achromatic color to mitigate round trip errors being introduced. That hue can be acquired from the LCh like
color space object:

```py play
color = Color('gray').convert('jzczhz')
color._space.achromatic_hue()
```

There are some slightly more complicated cases, such as CAM16 JMh and HCT (which is based off of CAM16), but the basic
idea remains relatively the same.

Do keep in mind that there are color space transformations which may vary in precision due to their algorithm. There are
times when we do all we can, and we can still end up not being able to predict an achromatic color as the
transformations can cause values to fall right outside our thresholds. CAM16 JMh and HCT (which is derived from CAM16
JMh) are a bit more difficult to calculate the achromatic threshold to the high degree of precision, and there is only
so far we are willing to drop accuracy for the sake of convenience, so converting between these cylindrical spaces and
other cylindrical spaces may not get us the achromatic hues we desire.

Notice in the example below that we get the achromatic hue in all cases except when we convert from `cam16-jmh` to
`hsl`.

```py play
Color('gray').convert('cam16-jmh')
Color('gray').convert('hsl')
Color('gray').convert('hsl').convert('cam16-jmh')
Color('gray').convert('cam16-jmh').convert('hsl')
```

When it comes to cylindrical color spaces, it is best to choose one instead of bouncing between multiple cylindrical
spaces. If you choose to do so, you may need to manually check for achromatic colors with an even lower threshold.
