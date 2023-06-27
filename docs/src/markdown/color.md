# The Color Object

The `Color` object is where all the magic of ColorAide happens and provides access to all the color manipulation
methods available. The `Color` object is used to represent a given color within a particular color space. In order
to perform most operations, you will need to create a color instance to begin.

There are a number of ways to instantiate new colors. Here we will cover the basics of creating colors, cloning colors,
converting colors, and a few other `Color` class specific topics.

## Importing

The `Color` object contains all the logic to create and manipulate colors. It can be imported from `coloraide`.

```py
from coloraide import Color
```

By default, the `Color` object registers only a subset of the available color spaces and features that are shipped with
ColorAide. This keeps the object a bit lighter and provides the more commonly used color spaces and features. Color
spaces, additional color distancing algorithms, gamut mapping algorithms, etc. are implemented via plugins. The normal
way to get access to these additional spaces and features is to subclass the `Color` object and resister the desired
spaces and features that are needed, but if you just want to explore all that ColorAide offers, you can import the
`ColorAll` object from `everything`.

```py
from coloraide.everything import ColorAll as Color
```

/// tip | Custom Color Objects
To add more plugins or tweak color defaults, see [Custom Color Classes](#custom-color-classes) for more.
///

## Creating Colors

Once the `Color` class is imported, colors can be created using various forms of input, including: numerical inputs,
dictionaries, CSS color strings, and even other `Color` instances.

### Numerical Inputs

The quickest way to create a color is by simply specifying the color space, color coordinates, and the optional alpha
channel. Numerical inputs require very little processing, but it should be noted that inputs must be specified according
to the way the color points are stored. Some people may be aware of the old CSS convention of specifying sRGB colors
with a range of 0 - 255, but ColorAide stores these as values between 0 - 1. If transparency is omitted, transparency is
assumed to be fully opaque, or a value of 1.

```py play
Color("srgb", [0.5, 0, 1], 0.3)
Color("srgb", [0.5, 0, 1])
```

### Dictionary Inputs

It may be desired to store and retrieve colors from some serialized format such as JSON. To make this easier, ColorAide
allows exporting and importing colors via dictionaries as well.

Dictionaries must define the `space` key and the `coords` key containing values for all of the color channels. The
`alpha` channel is kept separate and can be omitted, and if so, will be assumed as 1.

```py play
d = Color('red').to_dict()
print(d)
Color(d)
```

### String Inputs

By default, ColorAide accepts input strings as outlined in the CSS color specification. Accepted syntax includes legacy
CSS color formats as defined in CSS Level 3, but also allows for CSS Level 4 Color syntax!

```py play
Color("red")
Color("#00ff00")
Color("rgb(0 0 255 / 1)")
```

ColorAide supports all the color spaces as defined in the CSS Level 4 Color spec, but is not restricted to only
supported CSS colors. In order to support color strings for all colors, ColorAide allows for non-CSS color spaces to be
represented via the Level 4 CSS `#!css-color color()` function. Essentially, we've adopted the `#!css-color color()`
function as the universal way in which to serialize color strings.

It should also be noted that `#!css-color color()` can be used to describe any color regardless of whether it is
supported in the CSS spec in this way or not. For any color that is not explicitly supported in CSS via the
`#!css-color color()` function, ColorAide will allow using this form if the color space uses a `--` prefix for the color
space identifier. Check the [documentation of the given color space](./colors/index.md) to discover the appropriate CSS
identifier name.

```py play
Color('color(--hsl 130 40% 75% / 0.5)')
```

### Color Instance Inputs

If another color instance is passed as the input, a new color object will be created using the color data from the
input. This essentially clones the passed object.

```py play
c1 = Color('red')
c2 = Color(c1)

c1, c2
```

You can also use the `new` method to generate new colors from already instantiated color objects.

```py play
color1 = Color("red")
color1
color1.new("blue")
```

/// tip
If the `Color` class has be subclassed, this is an easy way to convert between the different subclasses, assuming
the registered color spaces are compatible between the two different `Color` classes.
///

## Random

If you'd like to generate a random color, simply call `Color.random` with a given color space and one will be generated.

```py play
[Color.random('srgb') for _ in range(10)]
```

Ranges are based on the color space's defined channel range. For color spaces with defined gamuts, the values will be
confined to appropriate ranges. For color space's without defined gamuts, the ranges may be quite arbitrary in some
cases. For color spaces with no hard, defined gamut, or gamuts that that far exceed practical usage it is recommend to
fit the colors to whatever gamut you'd like, or simply use a target space with a clear defined gamut.

```py play
Color.random('lab').fit('srgb')
```

Lastly, if you'd like to further constrain the limits, you can provide a list of constraints. A constraint should be
a sequence of two values specifying the minimum and maximum for the channel. If `#!py None` is provided, that constraint
will be ignored. If the list doesn't have enough values, those missing indexes will be ignored. If the list has too many
values, those extra values will be ignored.

```py play
Color.random('srgb', limits=[(0.25, 0.75)] * 3)
```

## Cloning

The `clone` method is an easy way to duplicate the current color object.

Here we clone the `#!color green` color object, giving us two.

```py play
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

```py play
Color("red")
Color("red").update(Color("blue"))
```

Here we update the sRGB `#!color red` with the color `#!color lch(80% 50 130)`.

```py play
Color("red").update("lch(80% 50 130)")
```

## Mutating

"Mutating" is similar to [updating](#updating) except that it will update the color **and** the color space from another
color. The input parameters are identical to the `new` method, so we can use a color object, a color string, dictionary,
or even raw data points.

In this example, the `#!color red` color object literally becomes the specified CIELCh color of
`#!color lch(80% 50 130)`.

```py play
Color("red").mutate("lch(80% 50 130)")
```

## Converting

Colors can be converted to other color spaces as needed. Converting will always return a new color unless the `in_place`
parameter is set to `#!py3 True`, in which case, the current color will be mutated to the new converted color and a
reference to itself is returned.

For instance, if we had a color `#!color yellow`, and we needed to work with it in another color space, we could simply
call the `convert` method with the desired color space.

```py play
Color('yellow').convert("lab")
```

/// note | Notes on [Round Trip Accuracy](./advanced.md#round-trip-accuracy)
///

## Color Matching

As previously mentioned, the `#!py3 Color()` object can parse CSS style string inputs. The string matching logic is
exposed via the `match` method. We can simply pass `match` a string, and, if the string is a valid color, a `ColorMatch`
object will be returned. The `ColorMatch` object has a simple structure that contains the matched `color` as a `Color`
object, and the `start` and `end` points it was located at.

```py play
Color.match("red")
```

By default it matches at the start of the buffer and returns a color if it finds one. If desired, we can do a
`fullmatch` which requires the entire buffer to match a color.

```py play
Color.match("red and yellow")
Color.match("red and yellow", fullmatch=True)
```

We can also adjust the start position of the search. In this case, by adjusting the start position to 8 characters
later, we will match `#!color yellow` instead of `#!color red`.

```py play
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
be colors. Then we can run `Color.match()` on those positions within the buffer to see if we find a valid color. This
ends up being much more efficient!

```py play
import re
from coloraide import Color

RE_COLOR_START = re.compile(
    r"""(?ix)
    (?:
        # CSS functions
        \b(?<![-#&$])(?:color\((?!\s*-)|(?:hsla?|(?:ok)?(?:lch|lab)|hwb|rgba?)\()|
        # Color words
        \b(?<![-#&$])[\w]{3,}(?![(-])\b|
        # Hex codes
        (?<![&])\#
    )
    """
)

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

for m in RE_COLOR_START.finditer(text):
    start = m.start()
    mcolor = Color.match(text, start=start)
    if mcolor is not None:
        mcolor.color.to_string()
```

## Custom Color Classes

The `Color` object was created to be extensible and has implemented various functionalities as plugins. Things like
color spaces, distancing algorithms, filters, etc. are all implemented as plugins. In order to keep things light,
ColorAide does not register all the of the plugins by default unless the user as imported the `ColorAll` object.

Additionally, ColorAide has implemented a number of defaults that can be tweaked within the `Color` class to alter how
things are handled.

Creating a custom class allows for a user to change some of the default settings and add or remove plugins to gain
access to more color spaces, distancing algorithms, filters, and other functionality.

In general, it is always recommended to subclass the `Color` object when setting up custom preferences or adding or
removing plugins. This prevents modifying the base class which may affect other libraries relying on the module. When
`Color` is subclassed, it is safe to then update global overrides or register and deregister plugins without the worry
of affecting the base class.

### Override Default Settings

ColorAide has a number of preferences that can be altered in the `Color` class. Most of these options can be configured
on demand when calling into a related function that uses them, but it may be useful to set them up one time on a new
`Color` object.

```py play
class Color2(Color):
    PRECISION = 3

Color('rgb(128.12345 0 128.12345)').to_string()
Color2('rgb(128.12345 0 128.12345)').to_string()
```

Properties             | Defaults               | Description
---------------------- | ---------------------- | -----------
`FIT`                  | `#!py "lch-chroma"`    | The default gamut mapping method used by the `Color` object.
`INTERPOLATE`          | `#!py "oklab"`         | The default color space used for interpolation.
`DELTA_E`              | `#!py "76"`            | The default ∆E algorithm used. This applies to when [`delta_e()`](./distance.md#delta-e) is called without specifying a method or when using color distancing to separate color when using the interpolation method called [`steps`](./interpolation.md#steps).
`PRECISION`            | `#!py 5`               | The default precision for string outputs.
`CHROMATIC_ADAPTATION` | `#!py "bradford"`      | Chromatic adaptation method used when converting between two color spaces with different white points. See [Chromatic Adaptation](./cat.md) for more information.
`HARMONY`              | `#!py "oklch"`         | Default color space to use for calculating color harmonies. This should be a cylindrical color space.
`CONTRAST`             | `#!py "wcag21"`        | Default contrast algorithm.
`AVERAGE`              | `#!py "average"`       | Default color space for averaging.
`CCT`                  | `#!py "robertson-1968` | Default CCT method.

### Plugins

Currently, color spaces, delta E methods, chromatic adaptation, filters, contrast, interpolation, and gamut mapping
methods are exposed as plugins. As previously mentioned, `Color` does not register all plugins, and `ColorAll` is often
more than a user needs by default. Registering exactly what you need is normally the recommend approach when more
functionality is required.

While we won't go into a lot of details about creating plugins here, we will go over how to register new plugins and
deregister existing plugins. To learn more about creating plugins, checkout the [plugin documentation](./plugins/index.md).

Registration is performed by the `register` method. It can take a single plugin or a list of plugins. Based on the
plugin's type, The Color object will determine how to properly register the plugin. If the plugin attempts to overwrite
a plugin already registered with the same name (as dictated by the plugin) the operation will fail. If `overwrite` is
set to `#!py3 True`, the overwrite will not fail and the new plugin will be registered with the specified name in place
of the existing plugin.

```py play
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

```py play
Color('red').delta_e('blue', method='cmc')
from coloraide.distance.delta_e_cmc import DECMC
class Custom(Color):
    DELTA_E = "cmc"
Custom.register(DECMC(l=1, c=1), overwrite=True)
Custom('red').delta_e('blue')
```

If a deregistration is desired, the `deregister` method can be used. It takes a string that describes the plugin to
deregister: `category:name`.

Valid categories are `space`, `delta-e`, `cat`, `contrast`, `filter`, `interpolate`, `fit`, and `cct`.

If the given plugin is not found, an error will be thrown, but if this notification is found to be unnecessary, `silent`
can be enabled and the there will be no error thrown.

```py play
class Custom(Color): ...
Custom.deregister('space:lab-d65')
try:
    Custom('red').convert('lab-d65')
except ValueError:
    print('Could not convert to Lab D65 as it is no longer registered')
```

Use of `*` with `deregister` will remove all plugins. Use of `category:*` will remove all plugins of that category.
