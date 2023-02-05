# Manipulating Colors

Once a `#!py3 Color` object is created, you have access to all the color channels. Color channels can be read
individually or extracted all at once. Getting and setting color channels is flexible and easy, allowing for intuitive
access.

## Accessing Coordinates

There are various ways to get and set the current values of color coordinates. Colors can be accessed by channel name
or numerical index directly. We can also manipulate colors within different color spaces.

### Access By Channel Name

One of the more intuitive ways to access color values is by channel name. Each color space defines the name of each of
the available channels. `alpha` is the one channel name that is always constant no matter the color space.

```playground
color = Color("orange")
color
color['r']
color['g']
color['b']
color['alpha']
```

Some channels may be also be recognized using an alias. Check the color space's documentation to learn the recognized
channel names and aliases.

```playground
color = Color("orange")
color
color['red'] = 0
color['green'] = 0
color['blue'] = 1
color
```

### Access By Index

Color channels can also be read or set by index. Channels are always in logical order. This means, for instance, an
RGB color space will have its channel in the order of `r`, `g`, `b`, and `alpha`. The`alpha` channel always being the
last channel in any color space. Check out the color space's documentation to learn more about available channels and
the order in which they are stored.

```playground
color = Color("orange")
color
color[0]
color[1]
color[2]
color[3]
```

Because a Color object essentially operates similar to a list, negative values are also allowed.

```playground
color = Color("orange")
color
color[-1] = 0.5
color
```

### Access By Iteration

Color objects can also be treated as an iterable object. This allows us to simply loop through the values.

```playground
color = Color("orange")
color
[c for c in color]
```

### Access By Slicing

As previously mentioned, Color objects operate very similar to lists, and as such, can also be read or set via slicing.

```playground
color = Color("orange")
color
color[:-1]
color[:-1] = [0, 0, 1]
color
```

### Access By Functions

Colors can also be accessed and modified in more advanced ways with special access functions `get()` and `set()`.

`get()` provides access to any channel via the channel name for a given color space, but what sets it apart from other
channel access methods is that it can indirectly access channels in other color spaces as well.

```python
color = Color("pink")
color
color.get('red')
color.get('oklch.hue')
```

Like `get()`, `set()` is a method that allows for the setting of any color channel via the color channel names. The
value can be set via numerical values or functions with more complex logic.

```playground
color = Color("pink")
color
color.set('blue', 0.5)
color.set('green', lambda g: g * 1.3)
```

Since `set()` returns a reference to the current color object, we can also chain multiple `set()` operations.

```playground
color = Color('black')
color
color.set('red', 1).set('green', 1)
```

Even more interesting is that, like `get()`, you can modify a channel in another color space indirectly.

```playground
color = Color("orange")
color
color.set('oklab.lightness', 0.50)
```

When getting/setting a color channel in a different color space than the current color space, the underlying color must
be converted to the target color space in order to access the channel. When doing this to get/set multiple channels,
this can be a bit inefficient. In order to make such operations more efficient, both `get()` and `set()` allow for bulk
operations. When performing bulk channel operations, the channels operations are performed in the order they are
specified; therefore, it is important to group together channels of the same color space to ensure they are accessed
with a single conversion.

To get multiple channels, simply provide a list of channels.

```playground
color = Color('orange')
color
color.get(['oklch.lightness', 'oklch.hue', 'alpha'])
```

To set multiple channels, pass a single dictionary containing the channel names and values.

```playground
color = Color('orange')
color
color.set(
    {
        'oklch.lightness': lambda l: l - l * 0.25,
        'oklch.hue': 270
    }
)
```

!!! warning "Indirect Channel Modifications"
    Indirect channel modification is very useful, but keep in mind that it may give you access to color spaces that are
    incompatible due to gamut size, and their algorithm may end up not preserving some aspects of a color. Additionally,
    the feature converts the color to the target color space, modifies it, and then converts it back making it
    susceptible to any possible [round trip errors](./advanced.md#round-trip-accuracy).

!!! new "New in 1.5: Getting/Setting Multiple Channels"

## Undefined Values

Colors in general can sometimes have undefined channels. This can actually happen in a number of ways.

1. Channels can naturally be undefined under certain situations as defined by the color space. For instance, spaces
   with hues will have powerless hues when the color is achromatic. As an example, this can occur if saturation or
   chroma is zero.

    If an achromatic color manually has its hue defined, then the hue is considered defined, though that value will
    still be powerless during conversions. But lets considered an achromatic color in a rectangular color space being
    converted to a cylindrical color space with hue. During the conversion process, there is nothing to suggest to the
    algorithm what the hue should be. For instance, if saturation is zero, one could argue the hue should be `0`, but
    that is actually a red hue, and achromatic colors have no hue. In the end, no hue is actually satisfactory, so an
    undefined hue is applied.

    ```playground
    color = Color('white').convert('hsl')
    color[:]
    ```

2. When specifying raw data, and an insufficient amount of channel data is provided, the missing channels will be
   assumed as undefined, the exception is the `alpha` channel which is assumed to be `1` unless explicitly defined or
   explicitly set as undefined.

    ```playground
    Color('srgb', [1])[:]
    Color('srgb', [1, 0, 0], NaN)[:]
    ```

3. Undefined values can also occur when a user specifies a channel with the `none` keyword in CSS syntax. This can also
   be done in raw color data by directly passing `#!py3 float('nan')` -- the provided `NaN` constant is essentially an
   alias for this.

    One may question why such a thing would ever be desired, but this can be quite useful when interpolating as
    undefined channels will not be interpolated. It can be thought of as a way to mask off channels. Checkout the
    [Interpolation](./interpolation.md) section in the documentation to learn more.


    ```playground
    from coloraide import NaN
    color = Color("srgb", [0.3, NaN, 0.4])
    color[:]

    color = Color('rgb(30% none 40%)')
    color[:]
    ```

4. Lastly, a user can use the `mask` method which is a quick way to set one or multiple channels as undefined.
   Additionally, it returns a clone leaving the original untouched by default.

    ```playground
    Color('white')[:]
    Color('white').mask(['red', 'green'])[:]
    ```

    The `alpha` channel can also be masked:

    ```playground
    Color('white').mask('alpha')[-1]
    ```

    You can also do inverse masks, or masks that apply to every channel not specified.

    ```playground
    c = Color('white').mask('blue', invert=True)
    c[:]
    ```

### Checking for Undefined Values

As previously mentioned, a color channel can be undefined for a number of reasons. And in cases such as interpolation,
undefined values can even be useful. On the other hand, sometimes an undefined value may need to be handled special.

Undefined values are represented as the float value `NaN`. And since `NaN` values are not numbers -- hence the name "not
a number" -- they don't quite work the same as normal numbers. They don't contribute to math operations like add,
multiply, and divide. Any math operation performed with a `NaN` will simply yield `NaN`. `NaN` values are essentially
infectious.

At first glance, the behavior of `NaN` values can seem confusing, but it is actually pretty intuitive. If we define a
color with an undefined channel, and try to add to that value, what should we get? In reality, if the value is
undefined, how could we possibly add to it? The only sane answer is to return `NaN` again.

```playground
color = Color('color(srgb 1 none 1)')
color['green'] + 0.5
```

Because a `NaN` may cause surprising results, it can be useful to check if a hue (or any channel) is `NaN` before
applying certain operations where `NaN` may be undesirable, especially if the color potentially came from an unknown
source. To make checking for `NaN`s easy, the convenience function `is_nan` has been made available. You can simply give
`is_nan` the property you wish to check, and it will return either return `#!py3 True` or `#!py3 False`.

```playground
Color('hsl(none 0% 100%)').is_nan('hue')
```

This is equivalent to using the `math` library and comparing the value directly:

```playground
import math
math.isnan(Color('hsl(none 0% 100%)')['hue'])
```
