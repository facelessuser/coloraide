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

### Precision

`precision` controls the precision of the output values. The name is a little misleading as it will actually adjust the
precision and scale of the values. The default is 5. In some cases, like the sRGB hex output, precision may not really
come into play as hex values are rounded to the nearest whole number.

```py play
Color("rgb(30.3456% 75% 100%)").to_string(precision=5, percent=True)
Color("rgb(30.3456% 75% 100%)").to_string(precision=4, percent=True)
Color("rgb(30.3456% 75% 100%)").to_string(precision=3, percent=True)
Color("rgb(30.3456% 75% 100%)").to_string(precision=2, percent=True)
Color("rgb(30.3456% 75% 100%)").to_string(precision=1, percent=True)
```

Providing a precision of `0` will simply enable simple rounding to the nearest whole number.

```py play
Color("rgb(30.3456% 75% 100%)").to_string(precision=0, percent=True)
```

Providing a precision of `-1` is a special input that will give the highest, useful precision that can be given.
Precision will be given out to double precision. Higher can be used, but will most likely be unhelpful.

```py play
Color("rgb(30.3456% 75% 100%)").to_string(precision=-1, percent=True)
```

One note though, format of the value matters. Here we output in the range of 0 - 255. We can see that a precision of
`1`, in this case, can throw the color out of gamut. So remember to use a sufficient precision for what you are
doing and the values you are working in.

```py play
Color("rgb(30.3456% 75% 100%)").to_string(precision=1)
```

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
