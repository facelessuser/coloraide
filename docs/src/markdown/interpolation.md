# Color Interpolation

## Interpolating

The `interpolate` method allows a user to create an interpolation function. This can be used to create a list of
gradient colors, or whatever is needed. This function drives most of the features handled by interpolation.

Interpolation functions accept an input between 0 - 1, if values are provided out of this range, the color will be
extrapolated and the results may be surprising.

Here we create a an interpolation between `#!color rebeccapurple` and `#!color-fit lch(85% 100 85)` (previews are fit to
the sRGB gamut). We then step through values of `0.1`, `0.2`, and `0.3` which creates: \[
`#!color-swatch rgb(102 51 153)`,
`#!color-swatch rgb(142.01 45.343 154.31)`,
`#!color-swatch rgb(178.56 36.401 149.51)`,
`#!color-swatch rgb(211.09 28.471 139.17)`,
`#!color-swatch rgb(238.59 32.984 124.24)`,
`#!color-swatch rgb(255 53.098 105.75)`,
`#!color-swatch rgb(249.19 108.42 101.41)`,
`#!color-swatch rgb(255 130.24 87.784)`,
`#!color-swatch rgb(255 154.43 74.138)`,
`#!color-swatch rgb(255 179.93 62.157)`
\].

```pycon3
>>> i = Color("rebeccapurple").interpolate("lch(85% 100 85)", space='lch')
>>> for x in range(10):
...     i(x/10).to_string()
...
'rgb(102 51 153)'
'rgb(142.01 45.343 154.31)'
'rgb(178.56 36.401 149.51)'
'rgb(211.09 28.471 139.17)'
'rgb(238.59 32.984 124.24)'
'rgb(255 53.098 105.75)'
'rgb(249.19 108.42 101.41)'
'rgb(255 130.24 87.784)'
'rgb(255 154.43 74.138)'
'rgb(255 179.93 62.157)'
```

If desired, we can target specific channels for mixing which will keep all the other channels constant on the base
color. In this example, we have a base color of `#!color lch(52% 58.1 22.7)` which we mix with
`#!color lch(56% 49.1 257.1)`. We also specify that we want to only mix the `hue` channel. The final color is
`#!color lch(52% 58.1 351.59)`. Notice that when comparing to the base color that only the `hue` has changed.

```pycon3
>>> i = Color("lch(52% 58.1 22.7)").interpolate("lch(56% 49.1 257.1)", space="lch", adjust=["hue"])
>>> i(0.2477).to_string()
'lch(52% 58.1 351.59)'
```

Additionally, hues are special, and we can control the way the interpolation is evaluated. The `hue` parameter
accepts such values as `longer` or `shorter`, `shorter` being the default (see API for all options). In this example,
we run the same command, but specify that the interpolation should use the longer angle between the two hues. This time,
when we mix `#!color lch(52% 58.1 22.7)` and `#!color lch(56% 49.1 257.1)`, we get a different color
(`#!color lch(52% 58.1 80.761)`) as we interpolated between the larger angle instead of the shorter angle.

```pycon3
>>> i = Color("lch(52% 58.1 22.7)").interpolate("lch(56% 49.1 257.1)", space="lch", adjust=["hue"], hue="longer")
>>> i(0.2477).to_string()
'lch(52% 58.1 80.761)'
```

!!! tip
    It is important to note that you must specify the channels of the space the interpolation is occurring in.
    Specifying `hue` while interpolating in the sRGB color space would target no channels and would be ignored.

You can also do non-linear interpolation by providing a function. Here we use a function that returns `p ** 3` creating
the colors (colors are fit to the sRGB gamut): \[
`#!color-swatch-fit lch(50% 50 0)`,
`#!color-swatch-fit lch(50.04% 49.997 0.0196)`,
`#!color-swatch-fit lch(50.32% 49.976 0.15685)`,
`#!color-swatch-fit lch(51.08% 49.921 0.52995)`,
`#!color-swatch-fit lch(52.56% 49.819 1.2588)`,
`#!color-swatch-fit lch(55% 49.669 2.4666)`,
`#!color-swatch-fit lch(58.64% 49.487 4.2807)`,
`#!color-swatch-fit lch(63.72% 49.316 6.831)`,
`#!color-swatch-fit lch(70.48% 49.241 10.242)`,
`#!color-swatch-fit lch(79.16% 49.401 14.617)`
\].

```pycon3
>>> i = Color("lch(50% 50 0)").interpolate("lch(90% 50 20)", progress=lambda p: p ** 3)
>>> for x in range(10):
...     i(x/10).to_string()
...
'lch(50% 50 0)'
'lch(50.04% 49.997 0.0196)'
'lch(50.32% 49.976 0.15685)'
'lch(51.08% 49.921 0.52995)'
'lch(52.56% 49.819 1.2588)'
'lch(55% 49.669 2.4666)'
'lch(58.64% 49.487 4.2807)'
'lch(63.72% 49.316 6.831)'
'lch(70.48% 49.241 10.242)'
'lch(79.16% 49.401 14.617)'
```

## Color Mixing

Colors can be mixed together to create new colors. Mixing is built on top of the [`interpolate`](#interpolating)
function and will return a color between the current and specified color. If colors are requested to be interpolated
within a color space smaller than the original, the colors will be gamut mapped into the desired color space.

!!! tip
    Mix, just like interpolation, also accepts the `accept` and `hue` parameters.

As an example, if we had the color `#!color red` and the color
`#!color blue`, and we wanted to mix them, we can just call the `mix` method, and we'll get the color
`#!color rgb(127.5 0 127.5)`.

```pycon3
>>> red = Color("red")
>>> blue = Color("blue")
>>> red.mix(blue).to_string()
'rgb(127.5 0 127.5)'
```

The `mix` method will mix the two colors in the color space of the color calling the method. If needed a different color
space can be specified with the `space` parameter. Notice that this creates a different color:
`#!color rgb(180.38 44.003 76.616)`. The results of mixing in a different color space may be more desirable as color
mixing may be more natural.

```pycon3
>>> red = Color("red")
>>> blue = Color("blue")
>>> red.mix(blue, space="lab").to_string()
'rgb(180.38 44.003 76.616)'
```

By default, colors are mixed at 50%, but the percentage can be controlled. Here we mix the color `#!color blue` into
the color `#!color red` at 20%. This gives us the color of `#!color rgb(204 0 51)`.

```pycon3
>>> red = Color("red")
>>> blue = Color("blue")
>>> red.mix(blue, 0.2).to_string()
'rgb(204 0 51)'
```

Mix can also accept a string and will create the color for you which is great if you don't need to work with the
second color afterwards.

```pycon3
>>> Color("red").mix("blue", 0.2).to_string()
'rgb(204 0 51)'
```

Mixing will always return a new color unless `in_place` is set `True`.

## Steps

The `steps` method creates a list of discrete colors. Like mixing, it is also built on the [`interplate`](#interpolating).
steps. The steps to take between the two colors can be configured with the three options, `steps` (minimum number of
steps), `max_steps`, and `max_delta` (max allowable delta E distance between steps). The default delta E method is
delta E 76, which is a simple euclidean distancing in the Lab color space.

In this example we we specify the color `#!color Color("display-p3", [0, 1, 0])` and interpolate steps between
`#!color red`. The result gives us an array of colors: \[
`#!color-swatch rgb(0% 98.694% 11.114%)`,
`#!color-swatch rgb(25.043% 95.745% 0%)`,
`#!color-swatch rgb(38.1% 92.729% 0%)`,
`#!color-swatch rgb(47.023% 89.644% 0%)`,
`#!color-swatch rgb(54.067% 86.49% 0%)`,
`#!color-swatch rgb(59.956% 83.266% 0%)`,
`#!color-swatch rgb(65.025% 79.973% 0%)`,
`#!color-swatch rgb(69.455% 76.61% 0%)`,
`#!color-swatch rgb(73.353% 73.18% 0%)`,
`#!color-swatch rgb(76.786% 69.684% 0%)`,
`#!color-swatch rgb(79.796% 66.125% 0%)`,
`#!color-swatch rgb(82.412% 62.507% 0%)`,
`#!color-swatch rgb(84.651% 58.835% 0%)`,
`#!color-swatch rgb(86.526% 55.112% 0%)`,
`#!color-swatch rgb(88.045% 51.345% 0%)`,
`#!color-swatch rgb(89.213% 47.54% 0%)`,
`#!color-swatch rgb(90.034% 43.704% 0%)`,
`#!color-swatch rgb(90.512% 39.844% 0%)`,
`#!color-swatch rgb(90.648% 35.967% 6.5514%)`,
`#!color-swatch rgb(90.448% 32.079% 12.235%)`,
`#!color-swatch rgb(100% 0.00023% -0.00002%)`
\].

```pycon3
>>> color = Color("display-p3", [0, 1, 0])
>>> for x in color.steps("red", space="lch", out_space="srgb", max_delta=20, steps=10):
...     print(x.to_string(percent=True))
...
rgb(0% 98.694% 11.114%)
rgb(25.043% 95.745% 0%)
rgb(38.1% 92.729% 0%)
rgb(47.023% 89.644% 0%)
rgb(54.067% 86.49% 0%)
rgb(59.956% 83.266% 0%)
rgb(65.025% 79.973% 0%)
rgb(69.455% 76.61% 0%)
rgb(73.353% 73.18% 0%)
rgb(76.786% 69.684% 0%)
rgb(79.796% 66.125% 0%)
rgb(82.412% 62.507% 0%)
rgb(84.651% 58.835% 0%)
rgb(86.526% 55.112% 0%)
rgb(88.045% 51.345% 0%)
rgb(89.213% 47.54% 0%)
rgb(90.034% 43.704% 0%)
rgb(90.512% 39.844% 0%)
rgb(90.648% 35.967% 6.5514%)
rgb(90.448% 32.079% 12.235%)
rgb(100% 0.00023% -0.00002%)
```

## Overlaying Colors

The `overlay` method allows a transparent color to be overlaid on top of another color creating the composite of the
two. To perform an overlay, a background color must be provided to the color along with an optional color space. If a
color is to be overlaid within a smaller color space, the colors will be mapped to the smaller space. It is probably,
not recommended to overlay in cylindrical color spaces, but there is no restrictions prohibiting such actions.

In the example below, we take the `#!color rgb(100% 0% 0% / 0.5)` and overlay it on the color `#!color black`. This
yields the color: `#!color rgb(127.5 0 0)`.

```pycon3
>>> color = Color("rgb(100% 0% 0% / 0.5)")
>>> color.overlay("black").to_string()
'rgb(127.5 0 0)'
```

A new color will be returned instead of modifying the current color unless `in_place` is set `True`.

## Null Hues

Color spaces that have hue coordinates often have rules about when the hue is considered relevant. For instance, in the
HSL color space, if saturation is zero, the hue is considered null. This is because the color is "without color";
therefore, it has no hue, or the hue is undefined.

Many libraries, like [d3-color](https://github.com/d3/d3-color), [chroma.js](https://gka.github.io/chroma.js/), and
[color.js](https://github.com/LeaVerou/color.js) all represent null hues with `NaN` (not a number). This is usually done
to make color interpolation easier. Some, like d3-color, are a bit more liberal with `NaN` and will target special cases
that are above and beyond the normal rules to help ensure good interpolation. For instance, they not only mark hue null
on HSL colors when saturation is zero, but also when lightness is zero or one hundred (essentially appearing black or
white). In fact, they'll mark saturation as `NaN` when lightness indicates "black" or "white".

Additionally, some libraries allow marking non-hue channels as `NaN`; color.js allows a user to manually specify
channels with `NaN` so they can mask off channels for interpolation.

ColorAide also uses `NaN` during interpolating, but we do not carry that baggage around outside of interpolating.
Colors will not return `NaN` in their coordinates, so the user doesn't have to worry about checking for those cases when
assigning values, but it will calculate when hues are null when doing interpolation. If a space needs to account for hue
when interpolating (mainly cylindrical color spaces) then ColorAide will flag the hue channel as null by assigning the
coordinate a `NaN` prior to the actual interpolation.

ColorAide will consider the following color spaces as having a null hue in the following cases:

Color\ Space | Null\ Condition
------------ | ---------------
HSV          | `s<=0` or very near 0%[^1]
HSL          | `s<=0` or very near 0%[^1]
HWB          | `(w + b)>=100`or very near 100%[^1]
LCH          | `c<=0` or very near 0%[^1]

[^1]: When determining whether a hue is null, we use a threshold of `0.0005` "nearness".

///Footnotes Go Here///

To determine at any time if a hue is considered null, the `is_hue_null` method can be used. Any space that considers
hue will return `True` or `False` if their hue is null or not null respectively. Any space that does not specifically
calculate hue, will simply return `False`. The method will consider the current color space by default, but you can
query any color spaces by providing a different one.

```pycon3
>>> Color("lab(53.389% 0 0)").is_hue_null()
False
>>> Color("lab(53.389% 0 0)").is_hue_null("lch")
True
>>> Color("lab(53.389% 0 0)").is_hue_null("hsl")
True
>>> Color("lab(53.389% 0 0)").is_hue_null("hsv")
True
>>> Color("lab(53.389% 0 0)").is_hue_null("hwb")
True
```

Due to the way colors convert, all spaces may not yield the same value as in this example, so it is best to test in the
space that is being targeted.
