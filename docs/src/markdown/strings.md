# String Output

ColorAide supports serializing colors in the same formats that it accepts as inputs. This includes all CSS formats for
the associated color spaces, and if a color space is not supported in CSS, the `#!css-color color(space ...)` format.
ColorAide exposes various options to allow users to serialize in the form they most prefer.

## Convert to Strings

Colors can be serialized to strings by using the `to_string` method. The color class will convert the current color into
one of the many of CSS formats supported for the given color space.

```py play
Color("srgb", [0.5, 0, 1], 0.3).to_string()
```

There are a number of options that are common among all color spaces, but there are also some color space specific
options. We will only cover the color spaces shipped with ColorAide. It is possible to write a color space plugin that
uses very different options.

## Common Options

All color spaces support the following parameters.

### Alpha

`alpha` is set to `#!py3 None` by default and controls whether the alpha channel is shown in the serialized output.
When in the default state, `alpha` will only be shown if the alpha channel has a value less than 100%, but if set to
`#!py3 True`, alpha will always be shown. Setting to `#!py3 False` will cause alpha to be ignored in the output.

### Rounding

/// new | New in 4.6
///

/// note
Rounding is done with "half up" logic to match CSS recommendations with their color syntax. Internally, as with most
programming languages, all calculations use "half even" logic, or bankers rounding, to minimize floating point error.
"Half up" is only used when serializing or explicitly requesting rounded coordinates through the API.
///

There are various ways to approach rounding of data. ColorAide implements a few approaches in an attempt accommodate
most needs. The following modes can be selected via the `rounding` parameter:

1. `sigfig` is a rounding approach that ensures a specific number of significant figures, the default being 5.
	Significant figures are non-leading zero digits.

    ```py play
    Color("rgb(30.34567543% 0.0234567% 100%)").to_string(rounding='sigfig', percent=True)
    ```

    The number of significant figures is controlled via the `precision` parameter. Generally, values should be between
    [1, 17] with 17 being the largest precision that is supported by double-precision floating point numbers (15 is the
    largest stable precision). For convenience, `#!py 0` can be used as a shortcut for rounding whole integers. Any
    values that exceed this specification are ignored and full precision (`#!py 17`) is used.

    This is similar to how floating point numbers actually work, the difference being that the number of significant
    figures can be controlled. Since this will emphasize very small values, which may be well below the resolution that
    a color space can guarantee accuracy for, this isn't always recommended unless you want to get the exact values
    stored in a color.

    ```py play
    c = Color('srgb', [2e-203] * 3)
    c.to_string(color=True, rounding='sigfig', precision=17)
    c.coords(rounding='sigfig', precision=17)
    ```

2. `decimal` is a rounding approach that ensures rounding to a specific decimal position, the default being 5.


	```py play
    Color("rgb(30.34567543% 0.0234567% 100%)").to_string(rounding='decimal', percent=True)
    ```

    Decimal places can be positive or negative. Positive values will round to fractional positions (after the decimal),
    while negative values will round to integer positions (before the decimal).

    This can be good for being precise about how many decimals of precision a current color space may be accurate to,
    but it doesn't scale very very well as a default for various color spaces which may have reference ranges that
    differ by orders of magnitude. For this reason, it is recommended to use this if you are working in a specific color
    space and which to control the rounding to an exact precision.

    If negative values are used, the color will be rounded to the integer decimal place, `#!py -1` representing the ones
    place, `#!py -2` the tens place, etc.

    ```py play
    Color("rgb(35.34567543% 0.0234567% 100%)").to_string(rounding='decimal', precision=-1, percent=True)
    ```

3.  `digits` is a rounding approach that combines `sigfig` and `decimal` where the lowest precision of the two
    wins. When applied in this way, rounding will try to round to the specified number digits. This is the default mode
    that ColorAide operates in with a default number of digits of 5.

    ```py play
    Color("rgb(30.34567543% 0.0234567% 100%)").to_string(rounding='digits', percent=True)
    ```

    Like `sigfig`, values should be greater than 0 with 17 being the largest precision that is supported by
    double-precision floating point numbers (15 being the largest stable precision). For convenience, `#!py 0` can be
    used as a shortcut for rounding whole integers, and if a negative value is provided, the precision will just default
    to `#!py 17`.

    Because this is a marriage between `sigfig` and `decimal`, it scales better as a default. Color spaces with
    reference ranges of smaller magnitude have more decimals of precision than color spaces with reference ranges of
    larger magnitudes.

### Precision

`precision` is used to configure the precision of the currently selected [`rounding`](#rounding) mode. ColorAide, by
default, uses a value of `#!py 5` regardless of the rounding mode. How the number is handled is purely dependent on
the rounding mode.

`precision` adjusts the significant figures to which the numbers are rounded. Significant figures are non-leading zero
digits. So `#!py 100.003` has 6 significant figures and `#!py 0.000345` has 3 significant figures.

/// tab | `digits`
```py play
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=5, percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=4, percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=3, percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=2, percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=1, percent=True)
```
///


/// tab | `sigfig`
```py play
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=5, rounding='sigfig', percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=4, rounding='sigfig', percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=3, rounding='sigfig', percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=2, rounding='sigfig', percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=1, rounding='sigfig', percent=True)
```
///

/// tab | `decimal`
```py play
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=5, rounding='decimal', percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=4, rounding='decimal', percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=3, rounding='decimal', percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=2, rounding='decimal', percent=True)
Color("rgb(30.34567543% 0.0234567% 100%)").to_string(precision=1, rounding='decimal', percent=True)
```
///

Lastly, there are some times where the channel coordinates need to have different precision. If needed, ColorAide will
allow a list of values for `precision` where each index in the list will correspond to a different color coordinate.

As an example, let's say we are outputting sRGB colors in the CSS `rgb()` format and we want to round the color
components to whole integers. We can do this by just setting `precision` to `#!py 0` which will force integer rounding,
but when we do this, it will round the alpha channel to 0 and 1 which is undesirable.

```py play
Color("rgb(30.3456% 75% 100% / 0.75)").to_string(precision=0)
```

If we provide a list of precision we can control each channel individually.

```py play
Color("rgb(30.3456% 75% 100% / 0.75)").to_string(precision=[0, 0, 0, 3])
```

If a channel is omitted, the current default precision is assumed for that channel.

```py play
Color("rgb(30.3456% 75% 100% / 0.75)").to_string(precision=[0, 0, 0])
```

/// new | New in 4.0: Per Channel Precision Control
///

### Fit

`fit` is set to `#!py3 True` by default and controls whether colors are fit to their gamut or not. Some color spaces are
technically unbounded, so no fitting may occur in those color spaces. Additionally, some color formats, like sRGB hex,
are always fitted (regardless of this setting) as they must fit into the gamut or they cannot be translated.

```py play
Color("rgb(30% 105% 0%)").to_string()
Color("rgb(30% 105% 0%)").to_string(fit=False)
```

Additionally, we can choose a different fitting method by passing `fit` the name of the method we would like.

```py play
Color("rgb(30% 105% 0%)").to_string()
Color("rgb(30% 105% 0%)").to_string(fit='clip')
```

Some gamut mapping plugins may expose more options. To set these options, you can use a dictionary. Specify the method
via the `method` and any other options by their name.

```py play
Color("rgb(30% 105% 0%)").to_string(fit={'method': 'oklch-chroma', 'jnd': 0.002})
```

### Color

`color`, for some color spaces, is the default output, but for others this format can be explicitly requested by setting
`color` to `#!py3 True`. If set to `#!py3 True`, this will take priority over other format options.

```py play
Color("rebeccapurple").to_string(color=True)
```

### None

Colors that have undefined channels are internally represented with `NaN`. On output, these can be displayed as `none`
per the most recent CSS spec. These are very new, so most browsers do not support them. This is disabled by default
until a time when this behavior is common enough. `NaN` values will not survive fitting unless a color channel is
naturally undefined. An example would be a hue when the color has saturation or chroma set to zero.

```py play
Color('hsl(none 0% 30%)').to_string(none=True)
```

The one exception is that legacy `rgb()`, `rgba()`, `hsl()`, and `hsla()` forms ([comma separated](#comma)) do not
support `none` per the CSS spec.

### Percent

Color formats can serialize channels with percents by using `percent`.

```py play
Color("rebeccapurple").to_string(percent=True)
Color("rebeccapurple").convert('lab').to_string(percent=True)
```

By default, only HSL and HWB output channels with percents by default to match browser expectations which do not yet
support colors with non-percent output for their non-hue channels. This is specifically only true for the named color
function formats: `hsl()` and `hwb()`.

```py play
Color("rebeccapurple").convert('hsl').to_string()
Color("rebeccapurple").convert('hsl').to_string(percent=False)
```

If serializing with the CSS legacy format ([comma format](#comma)), percentage will be forced for saturation and
lightness when serializing HSL.

```py play
Color("rebeccapurple").convert('hsl').to_string(comma=True)
Color("rebeccapurple").convert('hsl').to_string(comma=True, percent=False)
```

Percent output is supported for the `color()` function output as well.

```py play
Color("rebeccapurple").convert('srgb').to_string(color=True, percent=True)
```

If it is desired, explicit control over each channel can be achieved by passing in a sequence containing booleans.

```py play
Color('rebeccapurple').convert('lab').to_string(alpha=True, percent=[True, False, False, True])
```

Any omitted list values will be assumed `#!py False`.

```py play
Color('rebeccapurple').convert('lab').to_string(alpha=True, percent=[True])
```

/// new | New 2.12
Boolean sequence support for `percent` added in 2.12.
///

## Format Specific Options

These options may occur in various color spaces depending on the CSS output format.

### Comma

In CSS, there are a few color spaces that allow a comma format: `srgb` and `hsl`. ColorAide allows these to be read in
and to be output in their legacy comma format. These are the only formats that ship with comma support.

If we want commas, we can force the comma syntax by setting `comma` to `#!py3 True`. This can alter some color space
output in other subtle ways. As the comma format is the old legacy approach, when sRGB has commas enabled, it will use
`rgba` instead of `rgb`. If using the non-comma syntax, `rgb` is always used, even when the color has
transparency.

```py play
Color("rgb(30 75 100 / 20%)").to_string(comma=True)
```

## sRGB Specific Options

These options are currently specific to the sRGB color space.

### Hex

sRGB can output colors to a hex format which is unique compared to HSL and others. Simply enable `hex`.

```py play
Color("rebeccapurple").to_string(hex=True)
```

### Upper

You can force hex to output in uppercase.

```py play
Color("red").to_string(hex=True)
Color("red").to_string(hex=True, upper=True)
```

### Compress

When converting to the hex color format, a color can be compressed in certain cases. Enabling `compress` will compress a
hex color if possible.

```py play
Color("#11223388").to_string(hex=True)
Color("#11223388").to_string(hex=True, compress=True)
```

### Names

sRGB can also output color names. If a color evaluates to a hex code which also evaluates to a color name in the
internal CSS color name mapping, then a color name will be returned. If the color does not match a color name, it will
fallback to whatever the other options dictate.

```py play
Color("#663399").to_string(names=True)
```
