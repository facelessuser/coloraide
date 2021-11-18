# The Color Object

## Creating Colors

The `Color` object can be imported from `coloraide`.

```py3
from coloraide import Color
```

Afterwards, colors can be created using various, valid CSS syntax:

```playground
Color("red")
Color("#00ff00")
Color("rgb(0 0 255 / 1)")
```

In general, each color space can be recognized using valid CSS syntax as specified in the CSS level 4 spec.
Additionally, all colors are recognized using the CSS color function (`#!css-color color(space coord ... / alpha)`),
even if the color is not defined in the CSS color spec or supported in the spec in this way. While the
`#!css-color color()` function in CSS does not explicitly support color spaces with angular channels (hues), it has been
adapted to support cylindrical colors, and is generally used as a generic input and default output for string
representation of colors. Colors not found in the CSS spec are usually done as custom names with the `--` prefix. Check
the [documentation of the given color space](./colors/index.md) to discover the appropriate CSS identifier name as the
CSS identifier may not always match the color space name as specified in ColorAide.

```playground
Color('color(--hsl 130 40% 75% / 0.5)')
```

While CSS input is useful, we can also insert raw data points directly. When doing things this way, we must be mindful
of the actual accepted input range. For instance, RGB colors are not specified in ranges from 0 - 255, but from 0 - 1.

```playground
Color("srgb", [0.5, 0, 1], 0.3)
```

Since colors can be exported to a simple dictionary, which can be useful if serializing to JSON, the Color object will
also accept this dictionary as an input. `space` and all relevant color channels must be specified, `alpha` is optional
and will be assumed `1` if omitted. Default channel names must currently be used (no aliases).

```playground
d = Color('red').to_dict()
print(d)
Color(d)
```

!!! note "Normalizing Undefined Channels"

    Normally, when ColorAide processes a color via CSS input or returns a color via compositing, interpolation, gamut
    fitting, etc., it will normalize undefined hues. Certain color spaces will consider a hue undefined in certain
    cases, such as when a HSL color has a saturation of zero. Raw inputs via the dict method or the color space and list
    method will not be normalized in such cases. Raw inputs are accepted as is. This is because they are treated as
    manual inputs, or purposeful inputs from the user, so their values are respected and left unchanged.

    If at any time, it is desired to force channel normalization after a manual input, just run `normalize`:

    ```playground
    Color("hsl(130 0% 50%)")
    Color("hsl", [130, 0, 0.5])
    Color("hsl", [130, 0, 0.5]).normalize()
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

If desired, all creation method can be configured to also filter out color spaces that we are not interested in by using
the `filter` parameter and specifying only the color spaces we do care about. Valid colors will then be constrained only
to those spaces in the list.

```playground
try:
    Color("red", filters=["hsl"])
except ValueError:
    print('Not a valid color')
Color("hsl(130 30% 75%)", filters=["hsl"])
```

## Cloning

The `clone` method is an easy way to duplicate the current color object.

Here we clone the `#!color green` object so we have two.

```playground
c1 = Color("green")
c1
c1.clone()
```

## Updating

A color can be "updated" using another color object. When an update occurs, the current color space is updated with the
data from the second color, but the color space does not change. It is basically the equivalent of converting the second
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

"Mutating" is similar to [updating](#updating) except that it will update the color and the color space from another
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

As previously mentioned, the `#!py3 Color()` object can take in CSS style string inputs. The string matching logic is
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

We can also adjust the start position of the search. In this case, by adjusting the start position to 8
characters later, we will match `#!color yellow` instead of `#!color red`.

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
all potential colors on every character is not really efficient. Additionally, some buffers way require additional
context that is not available to the to the match function. If such behavior is desired, what is recommended would
be to apply this with some logic to find potential places in the buffer to test, and only test those places.

In this example, we construct a regex to find places within the buffer that potentially has a valid color, but we also
try and filter out cases that are unfavorable by providing additional context. As we are interested in matching full
colors in HTML or CSS, we don't want to match hex in HTML entities or color names that are part of color variables
(`#!css var(--color-red)`).

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

In general, it is always recommended to subclass the [`Color`](#color) object when setting up a custom preferences or
adding and removing plugins. This prevents modifying the base class which may affect other libraries relying on the
module. When [`Color`](#color) is subclassed, it is safe to then update global overrides or register and deregister
plugins without worry of affecting the base class.

### Override Default Settings

ColorAide has a couple of default settings, such as the default precision for string outputs, default gamut mapping
mode, etc. All of these options can be set on demand when calling certain functions, but when not explicitly set, the
base class defaults are used. If needed, the defaults can be changed for an entire application or library. To do so,
simply subclass the `Color` object and override the class defaults. The new derived class can be used throughout an
application or library and will use the specified defaults.

```playground
class Color2(Color):
    PRECISION = 3

Color('rgb(128.12345 0 128.12345)').to_string()
Color2('rgb(128.12345 0 128.12345)').to_string()
```

Properties             | Description
---------------------- | -----------
`FIT`                  | The default gamut mapping method used by the [`Color`](#color) object.
`DELTA_E`              | The default ∆E algorithm used for gamut distancing called both internally for things like interpolation [`steps`](./interpolation.md#steps) or when [`delta_e()`](./distance.md#delta-e) is called without a an explicit method.
`PRECISION`            | The default precision for string outputs.
`CHROMATIC_ADAPTATION` | The default chromatic adaptation method (default is `bradford`). See [Chromatic Adaptation](./cat.md) for more information.

### Plugins

Currently, only color spaces, delta E methods, and gamut mapping methods are exposed as plugins.

If you wanted a more lightweight [`Color`](#color) object, you could deregister color spaces you don't need. Keep in
mind that some color spaces are essential, like XYZ D65 which is used in many color conversions. Removing some colors
could also break functionality of certain features that are reliant on a specific color space, such as CIELAB which is
used for delta E 2000 color distancing or CIELCH which is used in the the LCH Chroma gamut mapping.

While we will not go into creating plugins here, we will go over how to register new plugins and deregister existing
plugins. To learn more about creating plugins, checkout the [plugin documentation](./plugins/index.md).

Registration is performed by the `register` method. It can take a single plugin or a list of plugins. Based on the
plugin's type, The Color object will determine how to properly register the plugin. If the plugin attempts to overwrite
a plugin already registered with plugin's name (as dictated by the plugin) the operation will fail. If `overwrite` set
to `#!py3 True`, the overwrite will not fail and the new plugin will be registered with the specified name in place of
the existing plugin.

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
This is in case a user wishes to build up a color classes plugins from scratch. This may be useful if there is a desire
to explicitly define allowed plugins and exclude any unknown new ones that may become available.
