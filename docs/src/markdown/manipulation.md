# Manipulating Colors

## Reading Coordinates

There are various ways to read the current values of color coordinates.

1. Channel properties can be read directly:

    ```color
    color = Color("orange")
    color.red
    ```

2. Channel values can also be read by using the `get` method and providing the name of desired channel.

    ```color
    color = Color("orange")
    color.get("green")
    ```

3. All non-alpha coordinates can be read simultaneously by using the `coords` function.

    ```color
    color = Color("orange")
    color.coords()
    color.alpha
    ```

If a color coordinate is needed from another color space, it can be accessed by passing in the color space followed by
the name of the desired coordinate. The necessary conversions will happen behind the scenes and the desired value will
be returned.

```color
Color("blue").get("lch.chroma")
```

## Modifying Coordinates

Channel properties can be modified directly by using the named property. Here we modify `#!color red` by adjusting its
`green` property:

```color
color = Color("red")
color.green = 0.5
color.to_string()
```

When doing so, keep in mind, the internal coordinates are being adjusted, and so they must be modified within the range
in which the values are stored, and for sRGB, it is in the range of \[0, 1\].

If desired, the values can be modified with the `set` method. As these methods return a reference to the class, multiple
set operations can be chained together. Chaining the operations together, we can transform `#!color white` to
`#!color rgb(0 127.5 255)`.

```color
Color("white").set("red", 0).set("green", 0.5)
```

Channels in other color spaces can also be modified with the `set` function. Here we alter the color `#!color blue` in
the LCH color space and get `#!color-fit Color("blue").set('lch.hue', 130)`.

```{.color fit}
Color("blue").set('lch.hue', 130)
```

Functions can also be used to modify a channel property. Here we do a relative adjustment of the green channel and
transform the color `#!color pink` to `#!color rgb(255 249.6 203)`.

```color
Color("pink").set('green', lambda g: g * 1.3)
```

## Checking Null Hues

Cylindrical colors that offer a `hue` property can sometimes return `NaN` for a hue. This is usually because the hue
is undefined. For example, the color `#!color hsl(360 0% 100%)`, while assigned a hue, does not actually exhibit any
real hue since saturation is 0. Essentially, hue could be set to anything, and it would still have no affect on the
actual color. So, ColorAide will actually set hue to `NaN` (or "not a number"). `NaN` is treated as a zero on output.

```color
color = Color('hsl(360 0% 100%)')
color
color.coords()
```

Because `NaN` are not numbers, these values will not be included in color interpolation, and these values cannot be
added, multiplied, or take part in any real math operations. All math operations performed on `NaN` simply return `NaN`.

For this reason, it is useful to check if a hue is `NaN`. This can be done with the `is_nan` function. You can simply
give `is_nan` the property you wish to check, and it will return either `#!py3 True` or `#!py3 False`.

```color
Color('hsl(360 0% 100%)').is_nan('hue')
```

This is equivalent to using the `math` library and comparing the value directly:

```color
import math
math.isnan(Color('hsl(360 0% 100%)').hue)
```
