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

In general, each color space can be recognized using valid CSS syntax as specified in the CSS level 4 spec.
Additionally, all colors are recognized using the CSS color function (`#!css-color color(space coord ... / alpha)`),
even if the color is not defined in the CSS color spec or supported in the spec in this way. While the
`#!css-color color()` function in CSS does not explicitly support color spaces with angular channels (hues), it has been
adapted to support cylindrical colors, and is generally used as a generic input and default output for string
representation of colors.

```color
Color('color(hsl 130 40% 75% / 0.5)')
```

While CSS input is useful, we can also insert raw data points directly. When doing things this way, we must be mindful
of the actual accepted input range. For instance, RGB colors are not specified in ranges from 0 - 255, but from 0 - 1.

```color
Color("srgb", [0.5, 0, 1], 0.3)
```

It is important to note that raw inputs are always accepted exactly as they are specified. Take, for instance, an HSL
color with zero saturation. When providing a color via a string, the color is parsed and normalized as appropriate. If
we pass in an HSL color with zero saturation, the parsed string will treat the hue as undefined, while the raw input
values remain unaltered. Raw inputs are essentially treated as if the user is directly setting those channels.

```color
Color("hsl(130 0% 50%)")
Color("hsl", [130, 0, 50])
```

If another color instance is passed as the input, a new color will be created, essentially cloning the passed object.

```color
c1 = Color('red')
c2 = Color(c1)

c1, c2
```

You can also use the `new` method to generate new colors from already instantiated colors.

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

Here the `#!color red` color object literally becomes the specified CIELCH color of `#!color lch(80% 50 130)`.

```color
Color("red").mutate("lch(80% 50 130)")
```

## Converting

Colors can be converted to other color spaces as needed. Converting will always return a new color unless `in_place` is
set `#!py3 True`, in which case the current color will be mutated to the new converted color and then `covert` will
return a reference to the current color object.

For instance, if we had a color `#!color yellow`, and we needed to work with it in another color space, such as CIELAB,
we could simply call the `convert` method with the desired color space.

```color
Color('yellow').convert("lab")
```

## Color Matching

As previously mentioned, `#!py3 Color()` objects can take in CSS style string inputs. The string matching logic is
exposed via the `match` method. We can simply give it a string, and it will return a `ColorMatch` object. The 
`ColorMatch` object will have the matched color as a `Color` object, and the `start` and `end` points it was located at.

```color
Color.match("red")
```

By default it matches at the start of the buffer and returns a color if it finds one. If desired, we can do a
`fullmatch` which requires the entire buffer to match a color.

```color
Color.match("red and yellow")
Color.match("red and yellow", fullmatch=True)
```

We can also adjust the start position of the search. In this case, by adjusting the start position to 8
characters later, we will match `#!color yellow` instead of `#!color red`.

```color
Color.match("red and yellow", start=8)
```

If we'd like to only match certain color spaces, we can provide a filter list that will constrain the match only to the
specified color spaces.

```color
Color.match("red and yellow", filters=["hsl"])
Color.match("hsl(130 30% 75%)", filters=["hsl"])
```

A method to find all colors in a buffer is not currently provided as looping through all the color spaces and matching
all potential colors on every character is not really efficient. If such behavior is desired, what is recommended would
be to apply this with some logic to find potential places in the buffer to test, and only test those places.

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
mode, etc. All of these options can be set on-demand when calling certain functions. When not explicitly set, thenbase
class' default is used. If needed, the defaults can be changed for an entire application or library. To do so, simply
subclass the `Color` object and override the class defaults. Then the new derived class can be used throughout an
application or library.

```color
class Color2(Color):
    PRECISION = 3

Color('rgb(128.12345 0 128.12345)').to_string()
Color2('rgb(128.12345 0 128.12345)').to_string()
```

Properties  | Description
----------- | -----------
`FIT`       | The default gamut mapping method used by the [`Color`](#color) object.
`DELTA_E`   | The default delta E algorithm used for gamut distancing calls internally.
`PRECISION` | The default precision for string outputs.
