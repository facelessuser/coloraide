# Manipulating Colors

## Reading Coordinates

There are various ways to read the current values of color coordinates.

1. Channel properties can be read directly:

    ```playground
    color = Color("orange")
    color.red
    ```

2. Channel values can also be read by using the `get` method and providing the name of desired channel.

    ```playground
    color = Color("orange")
    color.get("green")
    ```

3. All coordinates can be read simultaneously by using the `coords` function. The alpha channel is excluded from
   `coords` and must be retrieved separately.

    ```playground
    color = Color("orange")
    color.coords()
    color.alpha
    ```

If a color coordinate is needed from another color space, it can be accessed by passing in the color space followed by
the name of the desired coordinate. The necessary conversions will happen behind the scenes and the desired value will
be returned.

```playground
Color("blue").get("lch.chroma")
```

## Modifying Coordinates

Channel properties can be modified directly by using the named property. Here we modify `#!color red` by adjusting its
`green` property and get an orange hued color.

```playground
color = Color("red")
color.green = 0.5
color.to_string()
```

When doing so, keep in mind, the internal coordinates are being adjusted, and so they must be modified within the range
in which the values are stored, and for sRGB, it is in the range of \[0, 1\].

Much like reading with the `get` method, values can be modified with the `set` method. As these methods return a
reference to the current class, multiple set operations can be chained together. Chaining multiple `set` operations
together, we can transform `#!color white` to `#!color rgb(0 127.5 255)`.

```playground
Color("white").set("red", 0).set("green", 0.5)
```

Functions can also be used to modify a channel property. This allows us to do more complex set operations. Here we do a
relative adjustment of the green channel and transform the color `#!color pink` to `#!color rgb(255 249.6 203)`.

```playground
Color("pink").set('green', lambda g: g * 1.3)
```

## Modifying Coordinates in Other Spaces

Channels in other color spaces can also be modified with the `set` function. Here we alter the color `#!color blue` by
editing the `hue` channel in the CIELCH color space and get `#!color Color("blue").set('lch.hue', 130)`. Keep in mind
though that the colors are being converted to the specified space under the hood, set, and then converted back, so if
you have multiple operations to apply in a given color space, it may be more efficient to convert to that space, apply
the set operations directly, and then convert back.

```playground
Color("blue").set('lch.hue', 130)
```

When setting a color in another color space, the final value is subject to any rounding errors that may occur in the
round trip to and from the specified color space. Also, depending on the transform functions of the spaces involved and
whether the original color is on the edge of its own gamut, this can lead to a color going slightly out of gamut, and if
one of the spaces involved in the conversion doesn't handle out of gamut colors with sensible values, you may get
something unexpected back.

```playground
Color('hsl(0 0% 50%)').set('hwb.blackness', 0).set('hwb.whiteness', 100)
Color('hsl(0 0% 50%)').set('oklab.lightness', 1)
Color('hsl(0 0% 50%)').set('oklab.lightness', 1).convert('srgb').coords()
```

The above example cleanly converts between HSL and HWB as the conversion between these two is much more precise, but the
Oklab example is not quite as precise and returns a color with a saturation that is way out of bounds. This is partly
because the Oklab max whiteness isn't exactly `1`, but more like `~0.999`, But keep in mind, it looks worse than it
really is. When converting the HSL value to sRGB, we see it is barely off. None of this is a bug, it is just the nature
of the algorithms we are using to convert, the precision of the floats, and the slight rounding errors that occur when
using [floating-point arithmetic][floating-point], etc.

In the end, while the HSL color with high saturation seems a bit unexpected, it is actually pretty close to the intended
value once you realize that the nearly 100% lightness dominates the result and makes the saturation and hue values
insignificant. For this reason, it makes a lot of sense that the sRGB coordinates are still so close. Also, HSL just
doesn't represent out of gamut colors as well as sRGB does. HSL was designed mainly to show colors from a square, RGB
coordinate system. Anything outside of the RGB range will not be as meaningful, but the values will convert back to sane
values in another space in most cases.

## Masking Channels

Colors in general can use `NaN` to represent undefined color channels. This currently only happens by default for `hue`
channels when the color is achromatic and has no defined hue.

When interpolating, undefined channels will not be interpolated. While we won't dive into all the interpolation
specifics here, we will demonstrate how to mask channels. To learn more about interpolation and how masking can help,
you can read more about it in [Interpolation](./interpolation.md).

Suffice it to say, a user may want to mask channels on their own for various reasons, using the `mask` function can
allow for a user to quickly and easily mask one or more channels:

```playground
Color('white').coords()
Color('white').mask(['red', 'green']).coords()
```

The `alpha` channel can also be masked:

```playground
Color('white').mask('alpha').alpha
```

Additionally, you can do inverse masks, or masks that apply to every channel not specified.

```playground
c = Color('white').mask('blue', invert=True)
c.coords()
c.alpha
```

## Checking for Null/NaN

As previously mentioned, a user can set a channel to `NaN` via the `mask` function, or potentially by passing `NaN`
directly to  the channel. In addition, cylindrical colors that offer a `hue` property can sometimes return `NaN` for a
hue. This occurs only when the hue is undefined, and only when ColorAide is converting from one color space to another,
or when interpreting a color string input.

As an example, the color `#!color hsl(360 0% 100%)`, while assigned a hue, does not actually exhibit any real hue since
saturation is 0. Essentially, hue could be set to anything, and it would still have no affect on the actual color. So,
ColorAide will actually set hue to `NaN` (or "not a number"). When outputting to a string, `NaN` is treated as a zero on
output.

```playground
color = Color('hsl(360 0% 100%)')
color
color.coords()
```

The only time `hue` is not automatically evaluated is when raw data inputs are used. This can be when a user
instantiates a color with raw data points or manually sets the channel with an explicit value. While the rendered color
still looks the same as the previous example, the channel values are preserved.

```playground
color = Color('hsl', [360, 0, 100])
color
color.coords()
color.hue = 270
color
```

Because `NaN` values are not numbers, and these values cannot be added, multiplied, or take part in any real math
operations. All math operations performed with a `NaN` simply return `NaN`.

```playground
float('nan') * 3
float('nan') + 3
```

Because a `NaN` may cause unexpected results, it can be useful to check if a hue (or any channel) is `NaN` before
applying certain operations. To make checking for `NaN`s easy, the convenience function `is_nan` has been made
available. You can simply give `is_nan` the property you wish to check, and it will return either `#!py3 True` or
`#!py3 False`.

```playground
Color('hsl(360 0% 100%)').is_nan('hue')
```

This is equivalent to using the `math` library and comparing the value directly:

```playground
import math
math.isnan(Color('hsl(360 0% 100%)').hue)
```
