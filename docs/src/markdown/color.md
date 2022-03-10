# The Color Object

The `Color` object is where all the magic of ColorAide happens. In order to manipulate, interpolate, or perform any
action on a color, we must first create one. There are a number of ways to instantiate new colors. Here we will cover
basic creating, cloning, and updating of the `Color` class object and a few other class specific topics.

## Creating Colors

The `Color` object contains all the logic to create and manipulate colors. It can be imported from `coloraide`.

```py3
from coloraide import Color
```

Afterwards, colors can be created using various, valid CSS syntax. Syntax includes legacy formats as defined in CSS
Level 3, but also contains CSS Level 4!

```playground
Color("red")
Color("#00ff00")
Color("rgb(0 0 255 / 1)")
```

!!! warning "Warning: CSS Level 4"
    Though CSS Level 4 is supported, the CSS spec is not finalized and there could be some churn in relation to the
    syntax as browsers begin to implement the spec, there may be changes.

ColorAide, not only supports colors in the CSS spec, but also some other additional color spaces as well. To bridge the
gap with syntax, ColorAide allows all colors, whether in the CSS spec or not, to be recognized using the CSS color
function (`#!css-color color(space coord ... / alpha)`). Even if the color is in the CSS spec and is not currently
specified to use the `#!css-color color()` function, we still allow it.

Essentially, we've adopted the `#!css-color color()` function as the universal way in which to serialize colors. If the
CSS spec does not formally recognize a color in this form, the color identifier will use the two dashes as a prefix
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
or various other reasons. The `space` key and all relevant color channels must be specified when constructing a color
object from a dictionary, `alpha` is the only optional channel and will be assumed as `1` if omitted. Default channel
names must currently be used (no aliases).

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

If desired, all creation methods can be have a color space filter list passed in. The filter list will prevent an input
which specifies a color space found in our list to not be accepted. Use a filter will constrain inputs to supported
color spaces not found in the list.

```playground
try:
    Color("red", filters=["hsl"])
except ValueError:
    print('Not a valid color')
Color("hsl(130 30% 75%)", filters=["hsl"])
```

## Cloning

The `clone` method is an easy way to duplicate the current color object.

Here we clone the `#!color green` object, giving us two.

```playground
c1 = Color("green")
c1
c1.clone()
```

## Updating

A color can be "updated" using another color input. When an update occurs, the current color space is updated from the
data of the second color, but the color space does not change. Using `update` is the equivalent of converting the second
color to the color space of the first and then updating all the coordinates (including alpha). The input parameters
are identical to the `new` method, so we can use a color object, a color string, or even raw data points.

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
color. The input parameters are identical to the `new` method, so we can use a color object, a color string, or even
raw data points.

In this example, the `#!color red` color object literally becomes the specified CIELCH color of
`#!color lch(80% 50 130)`.

```playground
Color("red").mutate("lch(80% 50 130)")
```

## Converting

Colors can be converted to other color spaces as needed. Converting will always return a new color unless the `in_place`
parameter is set to `#!py3 True`, in which case, the current color will be mutated to the new converted color and a
reference to itself is returned.

For instance, if we had a color `#!color yellow`, and we needed to work with it in another color space, such as CIELAB,
we could simply call the `convert` method with the desired color space.

```playground
Color('yellow').convert("lab")
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

Filtering unwanted color spaces is also available via the `filter` parameter, and is typically how creation methods
avoid parsing unwanted color spaces.

```playground
Color.match("red and yellow", filters=["hsl"])
Color.match("hsl(130 30% 75%)", filters=["hsl"])
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

In general, it is always recommended to subclass the [`Color`](#color) object when setting up custom preferences or
adding or removing plugins. This prevents modifying the base class which may affect other libraries relying on the
module. When [`Color`](#color) is subclassed, it is safe to then update global overrides or register and deregister
plugins without the worry of affecting the base class.

### Override Default Settings

ColorAide has a number of preferences that can be altered in the `Color` class. Most of these options can be configured
on demand when calling into a function that uses theme, but it may be useful to setup a new defaults so that the `Color`
object behaves how you prefer.

```playground
class Color2(Color):
    PRECISION = 3

Color('rgb(128.12345 0 128.12345)').to_string()
Color2('rgb(128.12345 0 128.12345)').to_string()
```

Properties             | Defaults            | Description
---------------------- | ------------------- | -----------
`FIT`                  | `#!py "lch-chroma"` | The default gamut mapping method used by the [`Color`](#color) object.
`INTERPOLATE`          | `#!py "oklab"`      | The default color space used for interpolation.
`DELTA_E`              | `#!py "76"`         | The default ∆E algorithm used. This applies to when [`delta_e()`](./distance.md#delta-e) is called without specifying a method or when using color distancing to separate color when using the interpolation method called [`steps`](./interpolation.md#steps).
`PRECISION`            | `#!py 5`            | The default precision for string outputs.
`CHROMATIC_ADAPTATION` | `#!py "bradford"`   | Chromatic adaptation method used when converting between two color spaces with different white points. See [Chromatic Adaptation](./cat.md) for more information.

### Plugins

Currently, only color spaces, delta E methods, and gamut mapping methods are exposed as plugins.

Some potential, useful cases: register a new color spaces not supported directly in ColorAide, test out a new ∆E
algorithm, experiment with a potentially better gamut mapping method, tweak an existing color space to accept and
output color strings in a new format, create a variant of a color space that uses a different white point than is
currently supported, etc.

If you wanted a more lightweight [`Color`](#color) object, you could deregister color spaces you don't need. Though,
keep in mind that some color spaces are essential, like XYZ D65 which is used in many color conversions. Removing some
colors could also break functionality of certain features that are reliant on a specific color space, such as CIELAB
which is used for ∆E^\*^~2000~ color distancing or CIELCH which is used in the the LCH Chroma gamut mapping, but both
could also be deregistered to avoid issues.

While we will not go into creating plugins here, we will go over how to register new plugins and deregister existing
plugins. To learn more about creating plugins, checkout the [plugin documentation](./plugins/index.md).

Registration is performed by the `register` method. It can take a single plugin or a list of plugins. Based on the
plugin's type, The Color object will determine how to properly register the plugin. If the plugin attempts to overwrite
a plugin already registered with the same name (as dictated by the plugin) the operation will fail. If `overwrite` is
set to `#!py3 True`, the overwrite will not fail and the new plugin will be registered with the specified name in place
of the existing plugin.

Here we just overwrite the existing Jzazbz color space plugin with itself again.

```playground
class Custom(Color): ...
from coloraide.spaces import jzazbz
Custom.register(jzazbz.Jzazbz, overwrite=True)
Custom('red').convert('jzazbz')
```

If a deregistration was desired, the `deregister` method can be used. It takes a string that describes the plugin to
deregister: `category:name`. Valid categories are `space`, `delta-e`, and `fit`. If the given plugin is not found,
an error will be thrown, but if this notification is found to be unnecessary, `silent` can be enabled and the there will
be no error thrown.

```playground
class Custom(Color): ...
Custom.deregister('space:jzazbz')
try:
    Custom('red').convert('jzazbz')
except ValueError:
    print('Could not convert to Jzazbz as it is no longer registered')
```

Use of `*` with `deregister` will remove all plugins. Use of `category:*` will remove all plugins of that category.
