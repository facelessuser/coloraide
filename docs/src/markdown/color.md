# The Color Object

## Creating Colors

The `Color` object can be imported from `coloraide`.

```py3
from coloraide import Color
```

Afterwards, colors can be created using various, valid CSS syntax:

```pycon3
>>> Color("red")
color(srgb 1 0 0 / 1)
>>> Color("#ff0000")
color(srgb 1 0 0 / 1)
>>> Color("rgb(255 0 0 / 1)")
color(srgb 1 0 0 / 1)
```

As shown above, we can use all sorts of valid CSS syntax, and we get the same color `#!color red`.

We can also insert raw data points directly, but notice, when doing this, we are required to enter the data as it is
used internally, and in the case for sRGB, the channels are in the range of \[0, 1\]. Additionally, alpha is always
handled as a separate parameter.

```pycon3
>>> Color("srgb", [0.5, 0, 1], 0.3)
color(srgb 0.5 0 1 / 0.3)
```

So in the example above, the raw data is parsed, and we get a transparent color in the sRGB space:
`#!color color(srgb 0.5 0 1 / 0.3)`.

We can also pass in other color objects, which is really only useful if we've subclassed the `Color` object and want
to cast the object between the classes.

The same color creation can be preformed from a color's `new` class method as well. New accepts the same inputs
as the class object itself.

```pycon3
>>> color1 = Color("red")
>>> color2 = color1.new("blue")
>>> color1, color2
(color(srgb 1 0 0 / 1), color(srgb 0 0 1 / 1))
```

## Cloning

The `clone` method is an easy way to duplicate the current color object.

Here we clone the `#!color green` object so we have two.

```pycon3
>>> c1 = Color("green")
>>> c2 = c1.clone()
>>> c1, c2
(color(srgb 0 0.50196 0 / 1), color(srgb 0 0.50196 0 / 1))
```

## Updating

A color can be "updated" using another color object. When an update occurs, the current color space is updated with the
data from the second color, but the color space does not change. It is basically the equivalent of converting the second
color to the color space of the first and then updating all the coordinates (including alpha). The input parameters
are identical to the `new` method, so we can use a color object, a color string, or even raw data points.

Here we update the color `#!color red` to the color `#!color blue`:

```pycon3
>>> color1 = Color("red")
>>> color2 = Color("blue")
>>> color1.update(color2)
color(srgb 0 0 1 / 1)
>>> color1, color2
(color(srgb 0 0 1 / 1), color(srgb 0 0 1 / 1))
```

Here we update the sRGB `#!color red` with the color `#!color lch(100% 50 130)`. Notice that the result is still in the
sRGB color space, but the color is bigger than the sRGB color space making the color out of gamut:
`#!color color(srgb 0.82374 1.0663 0.69484 / 1)`.

```pycon3
>>> Color("red").update("lch(100% 50 130)")
color(srgb 0.82374 1.0663 0.69484 / 1)
```

## Mutating

"Mutating" is similar to [updating](#updating) except that it will update the color and the color space from another
color. The input parameters are identical to the `new` method, so we can use a color object, a color string, or even
raw data points.

Here the `#!color red` color object literally becomes an LCH color object with the new color `#!color lch(50% 50 130)`.

```pycon3
>>> Color("red").mutate("lch(50% 50 130)")
color(lch 50 50 130 / 1)
```

## Converting

Colors can be converted to other color spaces as needed. Converting will always return a new color unless `in_place` is
set `True`.

For instance, if we had a color `#!color yellow`, and we needed to work with it in another color space, we
could simply call the `convert` method. In the example below, we convert the color `#!color yellow`, which is in the
sRGB color space, to the Lab color space which gives us `#!color color(lab 97.607 -15.753 93.388 / 1)`.

```pycon3
>>> Color('yellow').convert("Lab")
color(lab 97.607 -15.753 93.388 / 1)
```

## Color Matching

Color objects can take in raw data points with a color space name or CSS style inputs. This CSS style input logic is
exposed via the `match` method. By default, we can just give it a string, and it will return a `ColorMatch` object. The
`ColorMatch` object will have the matched color as a `Color` object, and the start and end points it was located at.

```pycon3
>>> Color.match("red")
ColorMatch(color=color(srgb 1 0 0 / 1), start=0, end=3)
```

By default it matches at the start of the buffer and returns a color if it finds one. If desired, we can do a
`fullmatch` which requires the entire buffer to match the color.

```pycon3
>>> Color.match("red and yellow")
ColorMatch(color=color(srgb 1 0 0 / 1), start=0, end=3)
>>> Color.match("red and yellow", fullmatch=True)
```

We can also adjust the start position of the search. In this case, by adjusting the start position to 8
characters later, we will match `#!color yellow` instead of `#!color red`.

```pycon3
>>> Color.match("red and yellow", start=8)
ColorMatch(color=color(srgb 1 1 0 / 1), start=8, end=14)
```

If desired, we can also filter out the CSS syntax of certain color spaces. In the following example, we will only target
HSL colors.

```pycon3
>>> Color.match("red and yellow", filters=["hsl"])
>>> Color.match("hsl(130 30% 75%)", filters=["hsl"])
ColorMatch(color=color(hsl 130 30 75 / 1), start=0, end=16)
```

A method to find all colors in a buffer is not provided as looping through all the color spaces and matching all
potential colors on every character is not really efficient.  What is recommended would be to apply this with some logic
to find potential places in the buffer to test, and only test those places.

In this example, we construct a regex to find places within the buffer that potentially have a valid color, but we also
try and filter out cases that are unfavorable, particularly in HTML or CSS. We don't want to match hex in HTML entities
or color names that are part of color variables (`#!css var(--color-red)`).

=== "Code"

    ```py3
    import re
    from coloraide.css import Color

    RE_COLOR_START = re.compile(r"(?i)(?:\b(?<![-#&])(?:color|hsla?|lch|lab|hwb|rgba?)\(|\b(?<![-#&])[\w]{3,}(?!\()\b|(?<![&])#)")

    text = """Red and yellow are colors. So are #ff0033 and lch(90% 50 50)."""

    for m in RE_COLOR_START.finditer(text):
        start = m.start()
        mcolor = Color.match(text, start=start)
        if mcolor is not None:
            print('Found {} @ index {}'.format(mcolor.color.to_string(), start))
    ```

=== "Output"

    ```
    Found rgb(255 0 0) @ index 0
    Found rgb(255 255 0) @ index 8
    Found rgb(255 0 51) @ index 34
    Found lch(90% 50 50) @ index 46
    ```
