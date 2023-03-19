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

```py play
color = Color("orange")
color
color['r']
color['g']
color['b']
color['alpha']
```

Some channels may be also be recognized using an alias. Check the color space's documentation to learn the recognized
channel names and aliases.

```py play
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

```py play
color = Color("orange")
color
color[0]
color[1]
color[2]
color[3]
```

Because a Color object essentially operates similar to a list, negative values are also allowed.

```py play
color = Color("orange")
color
color[-1] = 0.5
color
```

### Access By Iteration

Color objects can also be treated as an iterable object. This allows us to simply loop through the values.

```py play
color = Color("orange")
color
[c for c in color]
```

### Access By Slicing

As previously mentioned, Color objects operate very similar to lists, and as such, can also be read or set via slicing.

```py play
color = Color("orange")
color
color[:-1]
color[:-1] = [0, 0, 1]
color
```

### Access by Type

/// new | New 2.0
///

When dealing with colors, you have two types of channels: color channels and an alpha channel. These values can be
accessed and separated by [slicing](#access-by-slicing) as mentioned earlier, but some convenience functions have
been added to make this easier. `coords()` and `alpha()` will retrieve the color channels and the alpha channel
respectively.

```py play
color = Color("srgb", [1, 0, 1], 0.5)
color
color.alpha()
color.coords()
```

In addition, both of these functions offer a special parameter `nans` that controls whether undefined values are
returned as specified or whether they are resolved to defined values.

```py play
color = Color("hsl", [NaN, 0, 0.75], 0.5)
color
color.coords()
color.coords(nans=False)
```

### Access By Functions

Colors can also be accessed and modified in more advanced ways with special access functions `get()` and `set()`.

`get()` provides access to any channel via the channel name for a given color space, but what sets it apart from other
channel access methods is that it can indirectly access channels in other color spaces as well.

```py play
color = Color("pink")
color
color.get('red')
color.get('oklch.hue')
```

Like `get()`, `set()` is a method that allows for the setting of any color channel via the color channel names. The
value can be set via numerical values or functions with more complex logic.

```py play
color = Color("pink")
color
color.set('blue', 0.5)
color.set('green', lambda g: g * 1.3)
```

Since `set()` returns a reference to the current color object, we can also chain multiple `set()` operations.

```py play
color = Color('black')
color
color.set('red', 1).set('green', 1)
```

Even more interesting is that, like `get()`, you can modify a channel in another color space indirectly.

```py play
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

```py play
color = Color('orange')
color
color.get(['oklch.lightness', 'oklch.hue', 'alpha'])
```

To set multiple channels, pass a single dictionary containing the channel names and values.

```py play
color = Color('orange')
color
color.set(
    {
        'oklch.lightness': lambda l: l - l * 0.25,
        'oklch.hue': 270
    }
)
```

/// warning | Indirect Channel Modifications
Indirect channel modification is very useful, but keep in mind that it may give you access to color spaces that are
incompatible due to gamut size. Additionally, the feature converts the color to the target color space, modifies it,
and then converts it back making it susceptible to any possible [round trip errors](./advanced.md#round-trip-accuracy).
///

/// new | New in 1.5: Getting/Setting Multiple Channels
///

## Checking For Achromatic Colors

/// new | New 2.0
///

It can be useful to check whether a color is achromatic or not. With cylindrical color spaces, you can usually, but not
always, check if the hue is undefined. If you are dealing with a non-cylindrical color space, or a cylindrical space
where the hue has been manually defined despite it being achromatic, you can use `is_achromatic()` to verify if the
color is achromatic, or at least very close to achromatic.

```py play
color1 = Color('orange')
color1
color1.is_achromatic()
color2 = Color('gray').convert('lab')
color2
color2.is_achromatic()
color3 = Color('darkgray').convert('hsl').set('hue', 270)
color3
color3.is_achromatic()
```

## Normalizing Achromatic Colors

When converting, all channels become defined, and only if the color is achromatic will the hue be undefined. When
manually editing a color, or maybe reading a color in from an external source, the values may not be in this
configuration. If desired, `normalize()`  can remove unnecessary undefined channels and set achromatic hues as
undefined.

```py play
color = Color('hsl', [30, NaN, 0.75])
color
color.normalize()
```

If the return of undefined hues (NaN values) are not desired, just set `nans` to `#!py False`.

```py play
color = Color('hsl', [30, NaN, 0.75])
color
color.normalize(nans=False)
```

## Undefined Values

Colors in general can sometimes have undefined channels. This can actually happen in a number of ways.

1. Channels can naturally be undefined under certain situations as defined by the color space. For instance, spaces
   with hues will have powerless hues when the color is achromatic.

    ColorAide will always respect a manually defined hue, even on an achromatic color, but during conversion to a
    cylindrical color space, hue will be set to undefined if the color is achromatic.

    ```py play
    color = Color('white').convert('hsl')
    color[:]
    ```

2. When specifying raw data, and an insufficient amount of channel data is provided, the missing channels will be
   assumed as undefined, the exception is the `alpha` channel which is assumed to be `1` unless explicitly defined or
   explicitly set as undefined.

    ```py play
    Color('srgb', [1])[:]
    Color('srgb', [1, 0, 0], NaN)[:]
    ```

3. Undefined values can also occur when a user specifies a channel with the `none` keyword in CSS syntax. This can also
   be done in raw color data by directly passing `#!py3 float('nan')` -- the provided `NaN` constant is essentially an
   alias for this.

    One may question why such a thing would ever be desired, but this can be quite useful when interpolating as
    undefined channels will not be interpolated. It can be thought of as a way to mask off channels. Checkout the
    [Interpolation](./interpolation.md) section in the documentation to learn more.


    ```py play
    from coloraide import NaN
    color = Color("srgb", [0.3, NaN, 0.4])
    color[:]

    color = Color('rgb(30% none 40%)')
    color[:]
    ```

4. Lastly, a user can use the `mask` method which is a quick way to set one or multiple channels as undefined.
   Additionally, it returns a clone leaving the original untouched by default.

    ```py play
    Color('white')[:]
    Color('white').mask(['red', 'green'])[:]
    ```

    The `alpha` channel can also be masked:

    ```py play
    Color('white').mask('alpha')[-1]
    ```

    You can also do inverse masks, or masks that apply to every channel not specified.

    ```py play
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

```py play
color = Color('color(srgb 1 none 1)')
color['green'] + 0.5
```

Because a `NaN` (or undefined value) may cause surprising results, it can be useful to check if a hue (or any channel)
is undefined before applying certain operations where such a value may be undesirable, especially if the color
potentially came from an unknown source. To make checking for undefined values easy, the convenience function
`is_nan` has been made available. You can simply give `is_nan` the property you wish to check, and it will return
either `#!py3 True` or `#!py3 False`.

```py play
Color('hsl(none 0% 100%)').is_nan('hue')
```

This is equivalent to using the `math` library and comparing the value directly:

```py play
import math
math.isnan(Color('hsl(none 0% 100%)')['hue'])
```

### Resolving Undefined Values

ColorAide generally resolves undefined numbers on string output (when `none` is not allowed), some internal cases when
required, and when a user specifically asks for defined values only.

Normally, an undefined value defaults to `0` when forced to be defined, but there are a few cases where this may not
always be true.

1. Most cylindrical color spaces, when the color is achromatic, the hue becomes meaningless in the calculations. This
   makes sense as achromatic colors have no hues. In these cases, when a hue must be defined, we will generally assume
   `0`, but there are some color spaces that while the a given achromatic color should have no hue, the conversion
   algorithm actually works better when using a specific hue when translating from an achromatic color. Some examples
   are: CAM16 JMh, HCT, or even JzCzhz. In these cases, an undefined hue will be treated with the best hue for round
   trip translation.

    We can see in the example below that using `0` for an undefined hues in CAM16 JMh will not convert `#!py gray` back
    to sRGB properly, but using the one calculated for the color space does.

    ```py play
    jmh = Color('gray').convert('cam16-jmh')
    jmh.coords(nans=False)
    jmh.convert('srgb')
    jmh.set('hue', 0).convert('srgb')
    ```

2. Most of the time, if you set all color channels to undefined, when resolved, the color will be black (or white in
   the case of CMYK). Unfortunately, setting using `0` for undefined channels in some color spaces can create colors
   outside the viewable gamut. One such example is ACEScct which has a lower value that is greater than zero for black.
   In this case, setting undefined channels to zero will cause nonsense colors. In this specific case, we use the value
   for black.

    ```py play
    aces = Color('black').convert('acescct')
    aces
    aces.mask(['alpha'], invert=True, in_place=True)
    aces.coords(nans=False)
    aces.in_gamut()
    aces[:] = [0] * 3
    aces.in_gamut()
    ```
