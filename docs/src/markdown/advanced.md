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
when doing interpolation, we detect when a color is achromatic (or very close to achromatic) and set the hues to
undefined. This helps us to identify achromatic cases and helps us to prevent weird color shifts when interpolating
between achromatic colors. Only if a user manually defines a hue do we respect it.

```py play
Color.interpolate(['lch(75 100 180)', 'lch(75 0 0)'], space='lch')
Color.interpolate(['lch(75 100 180)', 'lch(75 0 none)'], space='lch')
```

Because of [floating point issues](#floating-point-math), conversions to cylindrical color spaces do not always satisfy
the requirements to be recognized as achromatic colors.

As an example, HSL colors are achromatic when the sRGB color it is derived from has all color channels equal to each
other. Let's say we convert the color `#!color darkgray` to the XYZ D65 color space and then back again. We can see that
what was once a color with all color channels equal to each other is now a color that has color channels very nearly
equal to each other.

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
it achromatic, and we sacrifice a little accuracy to gain practicality. Or maybe it is better to say that we compensate
for the natural inaccuracies that exist.

```py play
Color('darkgray').convert('hsl')[:-1]
Color('darkgray').convert('xyz-d65').convert('hsl')[:-1]
```

This problem can exist in various scenarios in pretty much all cylindrical color spaces. Some have tighter algorithms
and may give really good results with sRGB, but then when converting from some other color space we'll see maybe not as
tight a translation to and from.

Additionally, some color spaces have very dynamic achromatic responses, as an interesting example, let's consider CAM16
JMh. This color space actually has its lower limit for achromatic colors gradually rise higher and higher as lightness
increases. Not only that, the achromatic line actually passes mainly through hue ~209.5 for most achromatic colors
lighter than black.

```py play
Color('color(srgb 0 0 0)').convert('cam16-jmh', norm=False)[:]
Color('color(srgb 0.5 0.5 0.5)').convert('cam16-jmh', norm=False)[:]
Color('color(srgb 1 1 1)').convert('cam16-jmh', norm=False)[:]
```

This can make it hard to specify a simple chroma check for achromatic colors. Simply lowering the chroma or changing the
hue can make the color no longer achromatic.

```py play
white = Color('color(srgb 1 1 1)')
white.convert('cam16-jmh', norm=False).convert('srgb').to_string(hex=True)
white.convert('cam16-jmh', norm=False).set('h', 0).convert('srgb').to_string(hex=True)
white.convert('cam16-jmh', norm=False).set('m', 0.0).convert('srgb').to_string(hex=True)
```

For these types of color spaces, ColorAide will map the achromatic response with a spline and use it as a reference
to give detect achromatic values for undefined chroma and hue.

```py play
Color('cam16-jmh', [100, NaN, NaN]).convert('srgb').to_string(hex=True)
Color('cam16-jmh', [50, NaN, NaN]).convert('srgb').to_string(hex=True)
Color('cam16-jmh', [20, NaN, NaN]).convert('srgb').to_string(hex=True)
```

Depending on how well we can fit the achromatic response, the better the accuracy, but we do purposely allow some wiggle
room to ensure we can capture achromatic colors within the threshold of the spline's accuracy. This can introduce some
loss of accuracy, but makes working with achromatic colors in difficult spaces like CAM16 JMh more reasonable.

```py play
gray = Color('cam16-jmh', [50, NaN, NaN])
gray.normalize()
Color.interpolate([gray, 'green'], space='cam16-jmh')
```
