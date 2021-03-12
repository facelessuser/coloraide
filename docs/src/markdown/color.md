# The Color Object

## Creating Colors

The `Color` object can be imported from `coloraide`.

```py3
from coloraide import Color
```

Afterwards, colors can be created using various, valid CSS syntax:

```color
Color("red"),
Color("#00ff00"),
Color("rgb(0 0 255 / 1)")
```

As shown above, we can use all sorts of valid CSS syntax, and we get the same color `#!color red`.

We can also insert raw data points directly, but notice, when doing this, we are required to enter the data as it is
used internally, and in the case for sRGB, the channels are in the range of \[0, 1\]. Additionally, alpha is always
handled as a separate parameter.

```color
Color("srgb", [0.5, 0, 1], 0.3)
```

We can also pass in other color objects, which is really only useful if we've subclassed the `Color` object and want
to cast the object between the classes.

The same color creation can be preformed from a color's `new` class method as well. `new` accepts the same inputs
as the class object itself.

```color
color1 = Color("red")
color1
color1.new("blue")
```

## Cloning

The `clone` method is an easy way to duplicate the current color object.

Here we clone the `#!color green` object so we have two.

```color
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

```color
Color("red")
Color("red").update(Color("blue"))
```

Here we update the sRGB `#!color red` with the color `#!color lch(80% 50 130)`.

```color
Color("red").update("lch(80% 50 130)")
```

## Mutating

"Mutating" is similar to [updating](#updating) except that it will update the color and the color space from another
color. The input parameters are identical to the `new` method, so we can use a color object, a color string, or even
raw data points.

Here the `#!color red` color object literally becomes an LCH color object with the new color
`#!color lch(80% 50 130)`.

```color
Color("red").mutate("lch(80% 50 130)")
```

## Converting

Colors can be converted to other color spaces as needed. Converting will always return a new color unless `in_place` is
set `#!py3 True`, in which case the current color will be mutated to the new converted color.

For instance, if we had a color `#!color yellow`, and we needed to work with it in another color space, such as LAB, we
could simply call the `convert` method with the desired color space.

```color
Color('yellow').convert("Lab")
```

## Color Matching

Color objects can take in raw data points or a CSS style string input. The string matching logic is exposed via the
`match` method. By default, we can just give it a string, and it will return a `ColorMatch` object. The `ColorMatch`
object will have the matched color as a `Color` object, and the `start` and `end` points it was located at.

```color
Color.match("red")
```

By default it matches at the start of the buffer and returns a color if it finds one. If desired, we can do a
`fullmatch` which requires the entire buffer to match the color.

```color
Color.match("red and yellow")
Color.match("red and yellow", fullmatch=True)
```

We can also adjust the start position of the search. In this case, by adjusting the start position to 8
characters later, we will match `#!color yellow` instead of `#!color red`.

```color
Color.match("red and yellow", start=8)
```

If desired, we can also filter out the CSS syntax of certain color spaces. In the following example, we will only target
HSL colors.

```color
Color.match("red and yellow", filters=["hsl"])
Color.match("hsl(130 30% 75%)", filters=["hsl"])
```

A method to find all colors in a buffer is not provided as looping through all the color spaces and matching all
potential colors on every character is not really efficient.  What is recommended would be to apply this with some logic
to find potential places in the buffer to test, and only test those places.

In this example, we construct a regex to find places within the buffer that potentially have a valid color, but we also
try and filter out cases that are unfavorable, particularly in HTML or CSS. We don't want to match hex in HTML entities
or color names that are part of color variables (`#!css var(--color-red)`).

```color
import re
from coloraide import Color

RE_COLOR_START = re.compile(r"(?i)(?:\b(?<![-#&$])(?:color|hsla?|lch|lab|hwb|rgba?)\(|\b(?<![-#&$])[\w]{3,}(?![(-])\b|(?<![&])#)")

text = """Red and yellow are colors. So are #000088 and lch(75% 50 50)."""

colors = []
for m in RE_COLOR_START.finditer(text):
    start = m.start()
    mcolor = Color.match(text, start=start)
    if mcolor is not None:
        colors.append(mcolor.color)
[x.to_string() for x in colors]
```

## Override Default Settings

ColorAide has a couple of default settings, such as the default precision for string outputs, default gamut mapping
mode, etc. All of these options can be set on-demand when calling certain functions. When not explicitly set, some
default is used. If needed, the defaults can be changed for an entire application or library. To do so, simply subclass
the `Color` object and override the defaults. Then the new derived class can be used throughout an application or
library.

```color
class Color2(Color):
    PRECISION = 3

Color('purple').convert('lch').to_string()
Color2('purple').convert('lch').to_string()
```

Properties  | Description
----------- | -----------
`FIT`       | The default gamut mapping method used by the [`Color`](#color) object.
`DELTA_E`   | The default delta E algorithm used for gamut distancing calls internally.
`PRECISION` | The default precision for string outputs.
