# Advanced Topics

Colors are complicated, and sometimes it may not be understood why colors or color transformations yield the results
that they do. Here we'd like to cover more advanced or specific topics that don't fit well in existing topics or are too
verbose to be included elsewhere.

## CSS Compatibility

CSS is a convenient color syntax that people are familiar with, so it makes a great text representation of colors.
ColorAide supports the input and output of CSS syntax, but that doesn't mean it is attempting to be a CSS color library.
CSS goals and ColorAide goals are at times different, and some of the decisions they make are at odds with how we feel
colors should be treated in general. While we may not have all of CSS's behaviors enabled by default, we do provide a
way to simulate _most_ CSS logic.

### What is Not Supported?

It should be noted that ColorAide does not provide compatibility for CSS parse-time clamping. CSS clamps RGB channels
when using `rgb()` syntax, it clamps lightness of Lab and LCh color spaces (Oklab and OkLCh included), it clamps
hues, chroma, and saturation in many cylindrical color spaces. ColorAide does not do any of this.

- ColorAide only clamps channels if the conversion algorithm requires it or when performing gamut mapping/clipping.
- Hues are left as specified except when converted to another color space, gamut mapping/clipping, or when normalizing
  a color.

Currently, the only thing ColorAide clamps is the `alpha` channel as there is no practical use for transparency or
opaqueness beyond the range of [0, 1]. ColorAide clamps alpha on every set.

### What is Supported?

There are four features that allow ColorAide to mimic CSS behavior. All four features can be used on demand via special
parameters when using the appropriate, related functions, but if desired, they can be forced to be enabled for a `Color`
class. The for features are as follows:

1.  Gamut mapping with `oklch-chroma` is the current CSS recommended approach. It provides a color space with better
    hue preservation, but the space does become a bit more distorted at very wide gamuts and can cause sane gamut
    mapping to break down. Gamut mapping colors that fall within the Rec. 2020 and Display P3 range should work
    reasonably well.

2.  The `css-linear` interpolator follows CSS interpolation logic which differs from ColorAide's default interpolation
    logic. CSS specifically treats interpolation between achromatic hues and non-achromatic hues as if there is a hue
    arc. This means that when using `longer` hue fix-ups when interpolating between a color with a undefined hue and a
    color with a defined hue, you will interpolate a full 360 degrees. We do not agree with this approach and feel in
    both `shorter` and `longer` hue fix-ups that there should be no arc to interpolate along.

3.  Auto powerless handling in CSS will force hues to be interpolated as powerless if under certain circumstances. This
    is usually happens when color space chroma/saturation components are zero. While this behavior does make general
    sense, and ensures that a user is always treating achromatic colors as achromatic, it cripples the user's control of
    how a color is interpolated.

    ColorAide, by default, respects what the user has explicitly specified. If a user has a component set as undefined,
    it is treated as defined, it is explicitly set to a numerical value, it is treated defined. This makes interpolation
    very transparent. Only through natural conversions do hues become achromatic. If a user has explicitly defined a
    hue, they need to use `normalize()` to force ColorAide to update powerless hues.

    With all of this said, there are times when a user wants to force powerless hues, even when not explicitly defined.
    In these cases ColorAide can enforce this behavior.

4.  CSS also implements the idea of carrying forward undefined values during interpolation. Essentially, if a user
    specifies an undefined components, but interpolation is performed in a different color space, after conversion, if
    the two color spaces have compatible components, the undefined values will be carried forward to the like
    components. This means that an undefined hue in HSL would be carried forward to LCh. A red component in sRGB would
    be carried over to Display P3.

    The concept is interesting, but it can sometimes be a bit surprising in some cases. Currently, ColorAide does not
    enable this by default.

If a CSS compatible color object is required, one can be derived from the base `Color` class. All four features can be
forced as enabled by default as shown below.

```py
from coloraide import Color as Base

class Color(base):
    FIT = 'oklch-chroma'
    INTERPOLATOR = 'css-linear'
    POWERLESS = True
    CARRYFORWARD = True
```

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
jz = Color('color(jzazbz 0.25 0 0)')
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
to detect achromatic values for undefined chroma and hue.

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
