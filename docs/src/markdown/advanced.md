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

### Special Handling: Cylindrical Spaces

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

This problem can exist in various scenarios. in pretty much all cylindrical color spaces. Some have tighter algorithms
and may give really good results with sRGB, but then when converting from some other color space we'll see maybe not as
tight a translation to and from.

There are various ways to identify when a color is achromatic. In LCh, you may consider a color achromatic if chroma is
zero (or near zero). You can consider it achromatic when lightness is at minimum or maximum lightness. Similar logic
applies to other color spaces, but with varying accuracy across the many color spaces, you can often identify an
achromatic color in one color space, but miss it in another because you don't have the precision quite nailed down in
that color space.

As an interesting example, let's consider JzCzhz. This color space actually has its lower limit for achromatic colors
gradually rise higher and higher as lightness increases. This can be hard to set a simple chroma check that preserves
high accuracy, and this phenomenon is even more exaggerated in color spaces like CAM16 JMh and HCT.

```py play
Color('color(srgb 0 0 0)').convert('jzczhz')[:]
Color('color(srgb 0.5 0.5 0.5)').convert('jzczhz')[:]
Color('color(srgb 1 1 1)').convert('jzczhz')[:]
Color('color(--rec2100-pq 1 1 1)').convert('jzczhz')[:]
```

Because chroma keeps creeping higher, we find that the hue can actually start to affect translations even though
achromatic colors have no hue. This is just due to how the math works. In most color spaces chroma gets so small that
that it dwarfs the impact that hue has in the equation.

ColorAide, in order to handle achromatic colors across all color spaces in a sane way, tackles the problem by converting
any given color space to some common space for achromatic evaluation. We've chosen XYZ D65 as it is already a
requirement to have that color space registered for anything. We can then take the cross product of a particular color
in the XYZ space, crossing its value with XYZ value for `#!color white`. If the result is a vector with all zeros (or
in reality close enough to zero under some threshold) we know we have an achromatic color. We try to strike a nice
compromise with the threshold to preserve as much accuracy as we can, but provide decent achromatic results.

In the end, we pay a little cost in accuracy, but provide more reasonable achromatic detection with a reasonable amount
of error around achromatic colors.

```py play

hsl = Color('gray').convert('hsl')
hsl
jmh = hsl.convert('cam16-jmh')
jmh
lch = jmh.convert('lch')
lch
```

Keep in mind that certain color spaces may introduce more errors than others, and if you truncate precision, or even
translate through a lot of spaces, you may introduce enough error that a given color cannot be detected as achromatic.
