# The Color Object

The `Color` object is where all the magic of ColorAide happens. In order to manipulate, interpolate, or perform any
action on a color, we must first create one. There are a number of ways to instantiate new colors. Here we will cover
basic creating, cloning, and updating of the `Color` class object and a few other class specific topics.

## Importing

The `Color` object contains all the logic to create and manipulate colors. It can be imported from `coloraide`.

```py3
from coloraide import Color
```

By default, the `Color` object contains only a subset of the available color spaces, related distancing algorithms, etc.
This is done in order to keep the `Color` object lighter. If desired, the `ColorAll` object can be used which includes
_everything_. This is generally not recommended as most users do not need _everything_. In general, it is recommended to
subclass the `Color` object and cherry pick any additional plugins that are required, but if you'd like to have access
to all the color spaces that are available, along with any other optional plugins, you can import and use `ColorAll`.

```py3
from coloraide.everything import ColorAll as Color
```

!!! tip "Custom Color Objects"
    To add more plugins or tweak color defaults, see [Custom Color Classes](#custom-color-classes) for more.

## Creating Colors

Once the `Color` class is imported, colors can be created using various forms of input. Colors can be created from
strings, raw data input, and even simple raw data wrapped in dictionaries.

As far as strings are concerned, ColorAide has the ability to parse valid CSS syntax. Syntax includes legacy formats as
defined in CSS Level 3, but also contains CSS Level 4!

```playground
Color("red")
Color("#00ff00")
Color("rgb(0 0 255 / 1)")
```

!!! warning "Warning: CSS Level 4"
    Though CSS Level 4 is supported, the CSS spec is not finalized and there could be some churn in relation to the
    syntax as browsers begin to implement the spec.

ColorAide not only supports colors in the CSS spec, but also some other additional color spaces as well. To bridge the
gap with syntax, ColorAide allows all colors, whether in the CSS spec or not, to be recognized using the CSS color
function (`#!css-color color(space coord ... / alpha)`). Even if the color is in the CSS spec and is not currently
specified to use the `#!css-color color()` function, we still allow it.

Essentially, we've adopted the `#!css-color color()` function as the universal way in which to serialize color strings.
If the CSS spec does not formally recognize a color in this form, the color identifier will use two dashes as a prefix
(`--color-id`). Check the [documentation of the given color space](./colors/index.md) to discover the appropriate CSS
identifier name as the CSS identifier may not always match the color space name as specified in ColorAide.

```playground
Color('color(--hsl 130 40% 75% / 0.5)')
```

While CSS input is useful, we can also insert raw data points directly. When doing things this way, we must be mindful
of the actual accepted input range. For instance, RGB colors are not specified in ranges from 0 - 255, but from 0 - 1.

```playground
Color("srgb", [0.5, 0, 1], 0.3)
```

Colors can also be exported to and receive input from simple dictionaries. These can be useful when serializing to JSON
or various other reasons. Dictionaries include the `space` key and all relevant color channels as a list under the
`coords` key, and an optional `alpha` key will be assumed as `1` if omitted.

```playground
d = Color('red').to_dict()
print(d)
Color(d)
```

If another color instance is passed as the input, a new color will be created, essentially cloning the passed object.

```playground
c1 = Color('red')
c2 = Color(c1)

c1, c2
```

You can also use the `new` method to generate new colors from already instantiated color objects.

```playground
color1 = Color("red")
color1
color1.new("blue")
```

## Random

If you'd like to generate a random color, simply call `Color.random` with a given color space and one will be generated.

```playground
[Color.random('srgb') for _ in range(10)]
```

Ranges are based on the color space's defined channel range. For color spaces with defined gamuts, the values will be
confined to appropriate ranges. For color space's without defined gamuts, the ranges may be quite arbitrary. For color
spaces with no hard, defined gamut, it is recommend to fit the colors to whatever gamut you'd like, or simply use a
target space with a clear defined gamut.

```playground
Color.random('lab').fit('srgb')
```

Lastly, if you'd like to further constrain the limits, you can provide a list of constraints. A constraint should be
a sequence of two values specifying the minimum and maximum for the channel. If `#!py None` is provided, that constraint
will be ignored. If the list doesn't have enough values, those missing indexes will be ignored. If the list has too many
values, those extra values will be ignored.

```playground
Color.random('srgb', limits=[(0.25, 0.75)] * 3)
```

## Cloning

The `clone` method is an easy way to duplicate the current color object.

Here we clone the `#!color green` color object, giving us two.

```playground
c1 = Color("green")
c1
c1.clone()
```

## Updating

A color can be "updated" using another color input. When an update occurs, the current color space is updated from the
data of the second color, but the color space does not change. Using `update` is the equivalent of
[converting](#converting) the second color to the color space of the first and then updating all the coordinates
(including alpha). The input parameters are identical to the `new` method, so we can use a color object, a color string,
dictionary, or even raw data points.

Here we update the color `#!color red` to the color `#!color blue`:

```playground
Color("red")
Color("red").update(Color("blue"))
```

Here we update the sRGB `#!color red` with the color `#!color lch(80% 50 130)`.

```playground
Color("red").update("lch(80% 50 130)")
```

## Mutating

"Mutating" is similar to [updating](#updating) except that it will update the color **and** the color space from another
color. The input parameters are identical to the `new` method, so we can use a color object, a color string, dictionary,
or even raw data points.

In this example, the `#!color red` color object literally becomes the specified CIELCh color of
`#!color lch(80% 50 130)`.

```playground
Color("red").mutate("lch(80% 50 130)")
```

## Converting

Colors can be converted to other color spaces as needed. Converting will always return a new color unless the `in_place`
parameter is set to `#!py3 True`, in which case, the current color will be mutated to the new converted color and a
reference to itself is returned.

For instance, if we had a color `#!color yellow`, and we needed to work with it in another color space, such as CIELab,
we could simply call the `convert` method with the desired color space.

```playground
Color('yellow').convert("lab")
```

??? note "Notes on Round Tripping Accuracy"
    In general, ColorAide is careful to provide good round trip conversions where practical. What this means is that we
    try to maintain a high level of accuracy so that when a color is converted to a different color and then back, that
    it will be very close, if not exactly, the same. We accomplish this by not not clipping values during conversion and
    maintaining as high of precision as we can, but there are some cases where the round tripping accuracy cannot be
    maintained at the same high level, or when round tripping cannot be maintained at all.

    1. One situation that can cause bad round tripping is when one color model cannot properly handle a color due to its
       gamut being beyond the conversion algorithms limits.

        Consider a wide gamut, HDR color space like Jzazbz. When it is converted to HSLuv, whose algorithm clamps any
        lightness that exceeds the SDR range, the round trip is broken. This is just the nature of the HSLuv algorithm
        as it adheres to an sRGB gamut that does not support HDR lightness.

        ```playground
        jz = Color('color(--jzazbz 0.25 0 0)')
        jz
        hsluv = jz.convert('hsluv')
        hsluv
        hsluv.convert('jzazbz')
        ```

    2. Sometimes, round tripping can be compromised for practical reasons. This does not mean round tripping breaks, but
       the high degree of accuracy can drop some. A common case where this happens is with LCh-like color models: LCh,
       OkLCh, JzCzhz, etc.

        By definition, a color within an LCh-like color model is determined to be achromatic when chroma is `#!py3 0`.
        These color models usually calculate chroma by taking a Lab-like color space's `a` and `b` components (or some
        equivalent) and calculating the chroma with `#!py3 chroma = math.sqrt(a ** 2 + b ** 2)`. This requires both `a`
        and `b` to be exactly `#!py3 0` or chroma will not be `#!py3 0`. Many of these Lab-like color spaces do not
        resolve such that `a` and `b` are perfectly `#!py3 0`. Due to the complexity of the conversion to these Lab-like
        color spaces, coupled with inherent issues with floating point arithmetic, you will sometimes get very close to
        `#!py3 0`, but not exactly `#!py3 0`.

        What is more a problem is not that chroma doesn't resolve to `#!py3 0`, but that you can get nonsensical hues as
        chroma gets very close to zero. Because of this, we simply set hue to undefined when chroma is deemed very close
        for the color model. But this small change can affect the outcome slightly when doing a round trip back to the
        original color, though, not usually enough to impact the value in any significant, meaningful way.

        The definition of very close to `#!py3 0` can be different from color space to color space, so the impact of
        such a change can be more significant for certain color spaces.

        Consider the conversion of the color `#!color gray` to both Oklab and Jzazbz.

        ```playground
        c1 = Color('gray').convert('oklab')
        c2 = Color('gray').convert('jzazbz')
        c1, c2
        list(c1)
        list(c2)
        ```

        Jzazbz simply doesn't resolve as close to zero as Oklab; therefore, it's cylindrical counter part (JzCzhz) will
        be more sensitive during the round trip than Oklab's cylindrical counterpart (OkLCh). It should be noted that
        the difference is still not perceivable to the human eye.

        ```playground
        jz = Color('gray').convert('jzazbz')
        jz
        jz2 = jz.convert('jzczhz').convert('jzazbz')
        jz.delta_e(jz2, method='jz')
        ```

## Color Matching

As previously mentioned, the `#!py3 Color()` object can parse CSS style string inputs. The string matching logic is
exposed via the `match` method. We can simply pass `match` a string, and, if the string is a valid color, a `ColorMatch`
object will be returned. The `ColorMatch` object has a simple structure that contains the matched `color` as a `Color`
object, and the `start` and `end` points it was located at.

```playground
Color.match("red")
```

By default it matches at the start of the buffer and returns a color if it finds one. If desired, we can do a
`fullmatch` which requires the entire buffer to match a color.

```playground
Color.match("red and yellow")
Color.match("red and yellow", fullmatch=True)
```

We can also adjust the start position of the search. In this case, by adjusting the start position to 8 characters
later, we will match `#!color yellow` instead of `#!color red`.

```playground
Color.match("red and yellow", start=8)
```

A method to find all colors in a buffer is not currently provided as looping through all the color spaces and matching
all potential colors on every character is not really efficient. Additionally, some buffers may require additional
context that is not available to the match function. If such behavior is desired, it is recommended to apply some
additional logic to sniff out areas with high likelihood of having a color.

In the following example, we construct a regular expression to find places within the buffer that potentially have a
valid color. As the buffer is an HTML document we also want to incorporate some context to avoid matching HTML entities
or color names that are part of a CSS variable.

Once we've crafted our regular expression, we can search the buffer to find locations in the buffer that are likely to
be colors. Then we can run `Color.match()` on those positions within the buffer to see if we find a valid color!

```playground
import re
from coloraide import Color

RE_COLOR_START = re.compile(r"(?i)(?:\b(?<![-#&$])(?:color\((?!\s*-)|(?:hsla?|lch|lab|hwb|rgba?)\()|\b(?<![-#&$])[\w]{3,}(?![(-])\b|(?<![&])#)")

text = """
<html>
<head>
<style>
body {
    background-color: red;
    color: yellow;
}
</style>
</head>
<body>
<p>This is a test <span style="background-color: #000088; color: lch(75% 50 50)">test</span></p>
</body>
</html>
"""

colors = []
for m in RE_COLOR_START.finditer(text):
    start = m.start()
    mcolor = Color.match(text, start=start)
    if mcolor is not None:
        colors.append(mcolor.color)
[x.to_string() for x in colors]
```

## Custom Color Classes

The `Color` object was created to be extensible and has implemented various functionalities as plugins. Things like
color spaces, distancing algorithms, filters, etc. are all implemented as plugins. In order to keep things light,
ColorAide does not register all the of the plugins by default unless the user as imported the `ColorAll` object.

Additionally, ColorAide as implemented a number of defaults that can be tweaked within the `Color` class to alter how
things are handled.

Creating a custom class allows for a user to change some of the default settings and add or remove plugins to gain
access to more color spaces, distancing algorithms, filters, etc.

In general, it is always recommended to subclass the `Color` object when setting up custom preferences or adding or
removing plugins. This prevents modifying the base class which may affect other libraries relying on the module. When
`Color` is subclassed, it is safe to then update global overrides or register and deregister plugins without the worry
of affecting the base class.

### Override Default Settings

ColorAide has a number of preferences that can be altered in the `Color` class. Most of these options can be configured
on demand when calling into a related function that uses them, but it may be useful to set them up one time on a new
`Color` object.

```playground
class Color2(Color):
    PRECISION = 3

Color('rgb(128.12345 0 128.12345)').to_string()
Color2('rgb(128.12345 0 128.12345)').to_string()
```

Properties             | Defaults            | Description
---------------------- | ------------------- | -----------
`FIT`                  | `#!py "lch-chroma"` | The default gamut mapping method used by the `Color` object.
`INTERPOLATE`          | `#!py "oklab"`      | The default color space used for interpolation.
`DELTA_E`              | `#!py "76"`         | The default ∆E algorithm used. This applies to when [`delta_e()`](./distance.md#delta-e) is called without specifying a method or when using color distancing to separate color when using the interpolation method called [`steps`](./interpolation.md#steps).
`PRECISION`            | `#!py 5`            | The default precision for string outputs.
`CHROMATIC_ADAPTATION` | `#!py "bradford"`   | Chromatic adaptation method used when converting between two color spaces with different white points. See [Chromatic Adaptation](./cat.md) for more information.
`HARMONY`              | `#!py "oklch"`      | Default color space to use for calculating color harmonies. This should be a cylindrical color space.
`CONTRAST`             | `#!py "wcag21"`     | Default contrast algorithm.

### Plugins

Currently, color spaces, delta E methods, chromatic adaptation, filters, contrast, and gamut mapping methods are exposed
as plugins. As previously mentioned, `Color` does not register all plugins, and `ColorAll` is often more than a user
needs by default. Registering exactly what you need is normally the recommend way.

While we won't go into a lot of details about creating plugins here, we will go over how to register new plugins and
deregister existing plugins. To learn more about creating plugins, checkout the [plugin documentation](./plugins/index.md).

Registration is performed by the `register` method. It can take a single plugin or a list of plugins. Based on the
plugin's type, The Color object will determine how to properly register the plugin. If the plugin attempts to overwrite
a plugin already registered with the same name (as dictated by the plugin) the operation will fail. If `overwrite` is
set to `#!py3 True`, the overwrite will not fail and the new plugin will be registered with the specified name in place
of the existing plugin.

As previously mentioned, the `Color` object does not include all plugins. This example shows how to register one of the
many additional color spaces provided by ColorAide.

```playground
from coloraide import Color
from coloraide.spaces.xyy import xyY

try:
    Color('red').convert('xyy')
except:
    print('Nope')

class Custom(Color): ...

Custom.register(xyY())

Custom('red').convert('xyy')
```

Used in conjunction with [default settings override](#override-default-settings), we can not only change a default ∆E,
but we can alter a ∆E method's configuration by registering it with different defaults:

```playground
Color('red').delta_e('blue', method='cmc')
from coloraide.distance.delta_e_cmc import DECMC
class Custom(Color):
    DELTA_E = "cmc"
Custom.register(DECMC(l=1, c=1), overwrite=True)
Custom('red').delta_e('blue')
```

If a deregistration was desired, the `deregister` method can be used. It takes a string that describes the plugin to
deregister: `category:name`.

Valid categories are `space`, `delta-e`, `cat`, `filter`, and `fit`.

If the given plugin is not found, an error will be thrown, but if this notification is found to be unnecessary, `silent`
can be enabled and the there will be no error thrown.

```playground
class Custom(Color): ...
Custom.deregister('space:lab-d65')
try:
    Custom('red').convert('lab-d65')
except ValueError:
    print('Could not convert to Lab D65 as it is no longer registered')
```

Use of `*` with `deregister` will remove all plugins. Use of `category:*` will remove all plugins of that category.
