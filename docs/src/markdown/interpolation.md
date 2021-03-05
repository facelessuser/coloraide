# Color Interpolation

## Interpolating

The `interpolate` method allows a user to create an interpolation function. This can be used to create a list of
gradient colors, or whatever is needed. This function drives most of the features handled by interpolation.

Interpolation functions accept an input between 0 - 1, if values are provided out of this range, the color will be
extrapolated and the results may be surprising.

Here we create a an interpolation between `#!color rebeccapurple` and `#!color-fit lch(85% 100 85)` (color previews are
fit to the sRGB gamut). We then step through values of `0.1`, `0.2`, `0.3`, etc. which creates a range of colors that we
can use in a gradient to get:
`#!color-gradient
i = Color("rebeccapurple").interpolate("lch(85% 100 85)", space='lch')
result = list(map(lambda x: i(x/10), range(10)))
`.

```pycon3
>>> i = Color("rebeccapurple").interpolate("lch(85% 100 85)", space='lch')
>>> for x in range(10):
...     i(x/10).to_string()
...
'rgb(102 51 153)'
'rgb(142.02 45.34 154.31)'
'rgb(178.58 36.391 149.5)'
'rgb(211.11 28.452 139.16)'
'rgb(238.61 32.963 124.24)'
'rgb(255 53.083 105.75)'
'rgb(249.21 108.41 101.4)'
'rgb(255 130.24 87.774)'
'rgb(255 154.42 74.129)'
'rgb(255 179.93 62.148)'
```

If desired, we can target one or more specific channels for mixing which will keep all the other channels constant on
the base color. Channels can be any channel associated with the color space in which the interpolation is taking place
(including `alpha`).

In the following example, we have a base color of `#!color lch(52% 58.1 22.7)` which we mix with
`#!color lch(56% 49.1 257.1)`. We also specify that we want to only mix the `hue` channel. Applying this logic, we will
end up with a range of colors that maintain the same lightness and chroma, but with different hues:
`#!color-gradient
i = Color("lch(52% 58.1 22.7)").interpolate("lch(56% 49.1 257.1)", space="lch", adjust=["hue"])
result = list(map(lambda x: i(x/10), range(10)))
`.

We can see as we step through the colors that only the hue is interpolated:

```pycon3
>>> i = Color("lch(52% 58.1 22.7)").interpolate("lch(56% 49.1 257.1)", space="lch", adjust=["hue"])
>>> for x in range(10):
...     i(x/10).to_string()
...
'lch(52% 58.1 22.7)'
'lch(52% 58.1 10.14)'
'lch(52% 58.1 357.58)'
'lch(52% 58.1 345.02)'
'lch(52% 58.1 332.46)'
'lch(52% 58.1 319.9)'
'lch(52% 58.1 307.34)'
'lch(52% 58.1 294.78)'
'lch(52% 58.1 282.22)'
'lch(52% 58.1 269.66)'
```

Additionally, hues are special, and we can control the way the interpolation is evaluated. The `hue` parameter
accepts such values as `shorter`, `longer`, `increasing`, `decreasing`, and `specified` (`shorter` being the default).
Below, we can see how the interpolation varies using `shorter` vs `longer`.

```pycon3
>>> i = Color("lch(52% 58.1 22.7)").interpolate("lch(56% 49.1 257.1)", space="lch", adjust=["hue"])
>>> i(0.2477).to_string()
'lch(52% 58.1 351.59)'
>>> i = Color("lch(52% 58.1 22.7)").interpolate("lch(56% 49.1 257.1)", space="lch", adjust=["hue"], hue="longer")
>>> i(0.2477).to_string()
'lch(52% 58.1 80.761)'
```

To help visualize the different hue methods, consider the following evaluation between `#!color rebeccapurple` and
`#!color lch(85% 85 805)` in the table below. Check out the [CSS level 4 specification](https://drafts.csswg.org/css-color-4/#hue-interpolation)
to learn more about each one.

Hue\ Logic   | Result
------------ | ------
`shorter`    | `#!color-gradient i = Color("rebeccapurple").interpolate("lch(85% 100 805)", space='lch', hue="shorter"); result = list(map(lambda x: i(x/20), range(20)))`
`longer`     | `#!color-gradient i = Color("rebeccapurple").interpolate("lch(85% 100 805)", space='lch', hue="longer"); result = list(map(lambda x: i(x/20), range(20)))`
`increasing` | `#!color-gradient i = Color("rebeccapurple").interpolate("lch(85% 100 805)", space='lch', hue="increasing"); result = list(map(lambda x: i(x/20), range(20)))`
`decreasing` | `#!color-gradient i = Color("rebeccapurple").interpolate("lch(85% 100 805)", space='lch', hue="decreasing"); result = list(map(lambda x: i(x/20), range(20)))`
`specified`  | `#!color-gradient i = Color("rebeccapurple").interpolate("lch(85% 100 805)", space='lch', hue="specified"); result = list(map(lambda x: i(x/20), range(20)))`

We can also do non-linear interpolation by providing a function. Here we use a function that returns `p ** 3` creating
the colors (color previews are fit to the sRGB gamut):
`#!color-gradient
i = Color("lch(50% 50 0)").interpolate("lch(90% 50 20)", progress=lambda p: p ** 3)
result = list(map(lambda x: i(x/10), range(10)))
`.

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

The `mix` method will mix the two colors in the color space of the color calling the method. If needed, a different
color space can be specified with the `space` parameter. Notice that this creates a different color:
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

Mix can also accept a string and will create the color for us which is great if we don't need to work with the second
color afterwards.

```pycon3
>>> Color("red").mix("blue", 0.2).to_string()
'rgb(204 0 51)'
```

Mixing will always return a new color unless `in_place` is set `True`.

## Steps

The `steps` method creates a list of discrete colors. Like mixing, it is also built on [`interpolate`](#interpolating).
The steps to take between the two colors can be configured with the three options, `steps` (minimum number of steps),
`max_steps`, and `max_delta_e` (max allowable delta E distance between steps). The default delta E method is delta E 76,
which is a simple euclidean distancing in the Lab color space.

In this example, we we specify the color `#!color-fit color(display-p3 0 1 0)` and interpolate steps between
`#!color red`. The result gives us an array of colors (color previews are fit to the sRGB gamut):
`#!color-steps
result = list(Color("display-p3", [0, 1, 0]).steps("red", space="lch", out_space="srgb", max_delta_e=20, steps=10))
`.

```pycon3
>>> color = Color("display-p3", [0, 1, 0])
>>> for x in color.steps("red", space="lch", out_space="srgb", max_delta_e=20, steps=10):
...     print(x.to_string(percent=True))
...
rgb(0% 98.693% 11.113%)
rgb(25.045% 95.744% 0%)
rgb(38.102% 92.728% 0%)
rgb(47.027% 89.643% 0%)
rgb(54.07% 86.488% 0%)
rgb(59.96% 83.264% 0%)
rgb(65.029% 79.971% 0%)
rgb(69.459% 76.608% 0%)
rgb(73.357% 73.177% 0%)
rgb(76.79% 69.681% 0%)
rgb(79.8% 66.123% 0%)
rgb(82.415% 62.505% 0%)
rgb(84.654% 58.832% 0%)
rgb(86.529% 55.109% 0%)
rgb(88.047% 51.342% 0%)
rgb(89.215% 47.538% 0%)
rgb(90.036% 43.702% 0%)
rgb(90.513% 39.841% 0%)
rgb(90.649% 35.964% 6.5496%)
rgb(90.448% 32.076% 12.232%)
rgb(100% 0.00006% 0.00001%)
```

## Overlaying Colors

The `overlay` method allows a transparent color to be overlaid on top of another color creating the composite of the
two. To perform an overlay, a background color must be provided to the color along with an optional color space. If a
color is to be overlaid within a smaller color space, the colors will be mapped to the smaller space.

!!! Note "Cylindrical Spaces"
    Certain color spaces, like cylindrical spaces (HSV, HSL, HWB, and LCH), will not be overlaid in their own space.
    This is because these spaces do not work well with the overlay algorithm. Instead, such spaces will be mapped to
    more suitable spaces; such as, HSL, HSV, and HWB to sRGB and LCH to LAB.

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
[color.js](https://github.com/LeaVerou/color.js), represent null hues with `NaN` (not a number). This is usually done
to make color interpolation easier. Some, like d3-color, are a bit more liberal with `NaN` and will target special cases
that are above and beyond the normal rules to help ensure good interpolation. For instance, they not only mark hue null
on HSL colors when saturation is zero, but also when lightness is zero or one hundred (essentially appearing black or
white). In fact, they'll mark saturation as `NaN` when lightness indicates "black" or "white".

ColorAide also uses `NaN` during interpolating, but we do not carry that baggage around outside of interpolating.
Colors will not return `NaN` in their coordinates, so the user doesn't have to worry about checking for those cases when
assigning values, but it will calculate when hues are null when doing interpolation. If a space needs to account for hue
when interpolating (mainly cylindrical color spaces) then ColorAide will flag the hue channel as null by assigning the
coordinate a `NaN` prior to the actual interpolation.

ColorAide will consider the following color spaces as having a null hue in the following cases. For "very near" cases,
the threshold noted in the table is used. LCH uses a much larger threshold as conversions are more unstable as zero is
approached.

Color\ Space | Null\ Condition                   | Nearness\ Threshold
------------ | --------------------------------- | -------------------
HSV          | `s<=0` or very near 0             | `0.0005`
HSL          | `s<=0` or very near 0%            | `0.0005`
HWB          | `(w + b) >= 100`or very near 100% | `0.0005`
LCH          | `c<=0` or very near 0%            | `0.015`

To determine at any time if a hue is considered null, the `is_hue_null` method can be used. Any space that considers
hue will return `True` or `False` if their hue is null or not. Any space that does not specifically calculate hue, will
simply return `False`. The method will consider the current color space by default, but we can query any color spaces by
providing a different one.

```pycon3
>>> Color("hsl(0 0% 50%)").is_hue_null()
True
>>> Color("grey").is_hue_null("lch")
True
>>> Color("grey").is_hue_null("hsl")
True
>>> Color("grey").is_hue_null("hsv")
True
>>> Color("grey").is_hue_null("hwb")
True
>>> Color("grey").is_hue_null("lab")
False
```

Due to the way colors convert, all spaces may not yield the same value as they do in this example, so it is best to test
in the space that is being targeted.
