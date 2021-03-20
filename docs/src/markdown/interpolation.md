# Color Interpolation

## Interpolating

The `interpolate` method allows a user to create an interpolation function. This can be used to create a list of
gradient colors, or whatever is needed. This function drives most of the features under the interpolation umbrella.
The [`steps`](#steps) and [`mix`](#color-mixing) functions are both built on top of `interpolate`.

A returned interpolation functions accept an input between 0 - 1, if values are provided out of this range, the color
will be extrapolated and the results may be surprising.

In this example, we create a an interpolation between `#!color rebeccapurple` and `#!color-fit lch(85% 100 85)` (color
previews are fit to the sRGB gamut). We then step through values of `0.1`, `0.2`, `0.3`, etc.

```color
i = Color("rebeccapurple").interpolate("lch(85% 100 85)", space='lch')
[i(x/20).to_string() for x in range(20)]
```

This allows us to create a range of colors that we can use in a gradient.

```color
Color("rebeccapurple").interpolate(
    "lch(85% 100 85)",
    space='lch'
)
```

If desired, we can target one or more specific channels for mixing which will keep all the other channels constant on
the base color. Channels can be any channel associated with the color space in which the interpolation is taking place
(including `alpha`).

In the following example, we have a base color of `#!color lch(52% 58.1 22.7)` which we mix with
`#!color lch(56% 49.1 257.1)`. We also specify that we want to only mix the `hue` channel. Applying this logic, we will
end up with a range of colors that maintain the same lightness and chroma, but with different hues.

We can see as we step through the colors that only the hue is interpolated.

```color
Color("lch(52% 58.1 22.7)").interpolate(
    "lch(56% 49.1 257.1)",
    space="lch",
    adjust=["hue"]
)
```

Additionally, hues are special, and we can control the way the interpolation is evaluated. The `hue` parameter
accepts such values as `shorter`, `longer`, `increasing`, `decreasing`, and `specified` (`shorter` being the default).
Below, we can see how the interpolation varies using `shorter` vs `longer`.

```color
i = Color("lch(52% 58.1 22.7)").interpolate(
    "lch(56% 49.1 257.1)",
    space="lch",
    adjust=["hue"]
)
i(0.2477).to_string()
i = Color("lch(52% 58.1 22.7)").interpolate(
    "lch(56% 49.1 257.1)",
    space="lch",
    adjust=["hue"],
    hue="longer"
)
i(0.2477).to_string()
```

To help visualize the different hue methods, consider the following evaluation between `#!color rebeccapurple` and
`#!color lch(85% 85 805)` in the table below. Check out the [CSS level 4 specification](https://drafts.csswg.org/css-color-4/#hue-interpolation)
to learn more about each one.

`shorter`:
: 
    ```color
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="shorter"
    )
    ```

`longer`:
: 
    ```color
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="longer"
    )
    ```

`increasing`:
: 
    ```color
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="increasing"
    )
    ```

`decreasing`:
: 
    ```color
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="decreasing"
    )
    ```

`specified`:
: 
    ```color
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="specified"
    )
    ```

We can also do non-linear interpolation by providing a function. Here we use a function that returns `p ** 3` creating
the colors (color previews are fit to the sRGB gamut):

```color
Color("lch(50% 50 0)").interpolate(
    "lch(90% 50 20)",
    progress=lambda p: p ** 3
)
```

## Color Mixing

Colors can be mixed together to create new colors. Mixing is built on top of the [`interpolate`](#interpolating)
function and will return a color between the current and specified color. If colors are requested to be interpolated
within a color space smaller than the original, the colors will be gamut mapped into the desired color space.

!!! tip
    Mix, just like interpolation, also accepts the `accept` and `hue` parameters.

As an example, if we had the color `#!color red` and the color
`#!color blue`, and we wanted to mix them, we can just call the `mix` method, and we'll get:

```color
Color("red").mix(Color("blue"))
```

The `mix` method will mix the two colors in the color space of the color calling the method. If needed, a different
color space can be specified with the `space` parameter. Notice below that this creates a different color.
The results of mixing in a different color space may be more desirable as color mixing may be more natural.

```{.color fit}
Color("red").mix(Color("blue"), space="lch")
```

By default, colors are mixed at 50%, but the percentage can be controlled. Here we mix the color `#!color blue` into
the color `#!color red` at 20%. This gives us the color of `#!color rgb(204 0 51)`.

```color
Color("red").mix(Color("blue"), 0.2)
```

Mix can also accept a string and will create the color for us which is great if we don't need to work with the second
color afterwards.

```color
Color("red").mix("blue", 0.2)
```

Mixing will always return a new color unless `in_place` is set `#!py3 True`.

## Steps

The `steps` method creates a list of discrete colors. Like mixing, it is also built on [`interpolate`](#interpolating).
The steps to take between the two colors can be configured with the three options, `steps` (minimum number of steps),
`max_steps`, and `max_delta_e` (max allowable delta E distance between steps). The default delta E method is delta E 76,
which is a simple euclidean distancing in the Lab color space.

In this example, we we specify the color `#!color-fit color(display-p3 0 1 0)` and interpolate steps between
`#!color red`. The result gives us an array of colors (color previews are fit to the sRGB gamut):

```{.color fit}
Color("display-p3", [0, 1, 0]).steps(
    "red",
    space="lch",
    out_space="srgb",
    max_delta_e=20,
    steps=3,
    max_steps=15
)
```

## Overlaying Colors

The `overlay` method allows a transparent color to be overlaid on top of another color creating the composite of the
two. To perform an overlay, a background color must be provided to the color along with an optional color space. If a
color is to be overlaid within a smaller color space, the colors will be mapped to the smaller space.

!!! tip "Cylindrical Spaces"
    It is generally recommended to overlay in non-cylindrical spaces, but there is no limitation to do so.

In the example below, we take the `#!color rgb(100% 0% 0% / 0.5)` and overlay it on the color `#!color black`. This
yields the color: `#!color rgb(127.5 0 0)`.

```color
Color("rgb(100% 0% 0% / 0.5)").overlay("black")
```

If desired, you can specify a different space to overlay in via the `space` parameter. Color space can affect the
results.

```color
Color("rgb(100% 0% 0% / 0.5)").overlay("black", space="display-p3")
```

A new color will be returned instead of modifying the current color unless `in_place` is set `#!py3 True`.

## Null Handling

Color spaces that have hue coordinates often have rules about when the hue is considered relevant. For instance, in the
HSL color space, if saturation is zero, the hue is considered null. This is because the color is "without color";
therefore, it has no hue, or the hue is undefined.

Many libraries, like [d3-color](https://github.com/d3/d3-color), [chroma.js](https://gka.github.io/chroma.js/), and
[color.js](https://github.com/LeaVerou/color.js), represent null hues with `NaN` (not a number). This is usually done
to make color interpolation easier. Some, like d3-color, are a bit more liberal with `NaN` and will target special cases
that are above and beyond the normal rules to help ensure good interpolation. For instance, they not only mark hue null
on HSL colors when saturation is zero, but also when lightness is zero or one hundred (essentially appearing black or
white). In fact, they'll mark saturation as `NaN` when lightness indicates "black" or "white".

ColorAide also uses `NaN`, or in Python `#!py3 float('nan')`. In certain situations, when a hue is deemed undefined, the
hue value will be set to `coloraide.NaN`, which is just a constant containing `#!py3 float('nan')`. When interpolating,
if one color's channel has a `NaN`, the other color's channel will be used as the result. If both colors have a `NaN`
for the same channel, then `0` will be returned.

Notice that in this example, because white's saturation is zero, the hue is undefined. Because the hue is undefined,
when the color is mixed with a second color (`#!color purple`), the hue of the second color is used.

```color
color = Color('white').convert('hsl')
color.coords()
color2 = Color('purple').convert('hsl')
color2.coords()
color.mix(color2, space="hsl")
```

This is essentially how the `adjust` parameter works with [`interploate`](#interpolate), [`step`](#step), and
[`mix`](#mix). `adjust` simply ensures that the secondary color has `NaN` set to specified channels.

Technically, any channel can be set to `NaN`, but it must be done by instantiating a `Color` object with raw data or by
manually setting it via a channel property or accessor. CSS string inputs do not allow the `NaN` value.

```color
from coloraide import NaN
Color("srgb", [1, NaN, 1]).coords()
Color("red").set('green', NaN).coords()
```

When printing to a string, `NaN`s are always converted to `0`:

```color
from coloraide import NaN
Color("srgb", [1, NaN, 1])
```

At any time, a channel can be checked for whether it is `NaN` by using the `is_nan` method:

```color
Color("white").convert('hsl').is_nan('hue')
```

It can be useful to check whether a channel is `NaN` as `NaN` values can't be added, subtracted, multiplied, etc. They
will always return `NaN` unless you directly replace them.

```color
color = Color("white").convert('hsl')
color.hue = color.hue + 3
color.is_nan('hue')
color.hue = 3
color.is_nan('hue')
```
