# Color Interpolation

## Interpolating

The `interpolate` method allows a user to create an interpolation function. This can be used to create a list of
gradient colors, or whatever is needed. This function is used to drive all the features under the interpolation
umbrella.

A returned interpolation function accepts an input between 0 - 1, if values are provided out of this range, the color
will be extrapolated and the results may be surprising.

In this example, we create an interpolation between `#!color rebeccapurple` and `#!color lch(85% 100 85)` (color
previews are fit to the sRGB gamut). We then step through values of `0.1`, `0.2`, `0.3`, etc.

```playground
i = Color("rebeccapurple").interpolate("lch(85% 100 85)", space='lch')
[i(x/10).to_string() for x in range(10)]
```

This allows us to create a range of colors that we can use in a gradient.

```playground
Color("rebeccapurple").interpolate(
    "lch(85% 100 85)",
    space='lch'
)
```

Interpolation can also be done across multiple colors. The function, just like when interpolating between two colors,
takes a range of 0 - 1. When interpolating multiple colors, [piecewise interpolation](#piecewise-interpolation)
is used (which is covered in more detail later).

```playground
Color('black').interpolate(['red', 'white'])
```

If desired, we can target one or more specific channels (even alpha) for interpolation which will keep all the other
base color channels constant. Specified channels must be associated with the color space in which the interpolation is
taking place.

In the following example, we have a base color of `#!color lch(52% 58.1 22.7)` which we then interpolate with
`#!color lch(56% 49.1 257.1)`. We also specify that we want to only interpolate the `hue` channel by applying a mask to
all the other channels except `hue`. Applying this logic, we will end up with a range of colors that maintains the same
lightness and chroma, but with different hues. To learn more about masking and null hues, check out
[Null Handling](#null-handling).

We can see as we step through the colors that only the hue is interpolated.

```playground
i = Color("lch(52% 58.1 22.7)").interpolate(
    Color("lch(56% 49.1 257.1)").mask("hue", invert=True),
    space="lch"
)
[i(x/10).to_string() for x in range(10)]
```

Additionally, hues are special, and we can control the way the interpolation is evaluated. The `hue` parameter
accepts such values as `shorter`, `longer`, `increasing`, `decreasing`, and `specified` (`shorter` being the default).
Below, we can see how the interpolation varies using `shorter` vs `longer`.

```playground
i = Color("lch(52% 58.1 22.7)").interpolate(
    Color("lch(56% 49.1 257.1)").mask("hue", invert=True),
    space="lch"
)
i(0.2477).to_string()
i = Color("lch(52% 58.1 22.7)").interpolate(
    Color("lch(56% 49.1 257.1)").mask("hue", invert=True),
    space="lch",
    hue="longer"
)
i(0.2477).to_string()
```

To help visualize the different hue methods, consider the following evaluation between `#!color rebeccapurple` and
`#!color lch(85% 85 805)`. Below we will demonstrate each of the different hue evaluations. To learn more check out the
[CSS level 4 specification](https://drafts.csswg.org/css-color-4/#hue-interpolation) to learn more about each one.

=== "shorter"
    ```playground
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="shorter"
    )
    ```

=== "longer"
    ```playground
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="longer"
    )
    ```

=== "increasing"
    ```playground
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="increasing"
    )
    ```

=== "decreasing"
    ```playground
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="decreasing"
    )
    ```

=== "specified"
    ```playground
    Color("rebeccapurple").interpolate(
        "lch(85% 100 805)",
        space='lch',
        hue="specified"
    )
    ```

We can also apply easing functions by providing a function via `progress`. Here we use a function that returns
`#!py3 t ** 3` for the period when interpolating each channel:

```playground
Color("lch(50% 50 0)").interpolate(
    "lch(90% 50 20)",
    progress=lambda t: t ** 3
)
```

We can even apply a specific easing functions to a specific channels. Below, we apply `#!py3 t ** 3` to `alpha` while
`#!py3 t` (the default) is applied to all other channels. This can be done to one or more channels, all with
different functions.

```playground
Color("lch(50% 50 0)").interpolate(
    "lch(90% 50 20 / 0)",
    progress={
        'alpha': lambda t: t ** 3
    }
)
```

You can also set all the channels to a function via `all` and then override specific channels.

```playground
Color("lch(50% 50 0)").interpolate(
    "lch(90% 50 20 / 0)",
    progress={
        'all': lambda t: 1 - t,
        'alpha': lambda t: t ** 3
    }
)
```

## Mixing

Colors can be mixed together to create new colors. Mixing is built on top of the [`interpolate`](#interpolating)
function and will return a color between the current and specified color. If colors are requested to be interpolated
within a color space smaller than the original, the colors will be gamut mapped into the desired color space.

!!! tip
    Mix, just like interpolation, also accepts the `accept` and `hue` parameters.

As an example, if we had the color `#!color red` and the color
`#!color blue`, and we wanted to mix them, we can just call the `mix` method, and we'll get:

```playground
Color("red").mix(Color("blue"))
```

The `mix` method will mix the two colors in the CIELAB color space by default. If needed, a different color space can be
specified with the `space` parameter. Notice below that this creates a different color. The results of mixing in a
different color space may be more desirable as color mixing may be more natural.

```playground
Color("red").mix(Color("blue"), space="lch")
```

By default, colors are mixed at 50%, but the percentage can be controlled. Here we mix the color `#!color blue` into
the color `#!color red` at 20%. This gives us the color of `#!color rgb(204 0 51)` (after fitting).

```playground
Color("red").mix(Color("blue"), 0.2)
```

Mix can also accept a string and will create the color for us which is great if we don't need to work with the second
color afterwards.

```playground
Color("red").mix("blue", 0.2)
```

Mixing will always return a new color unless `in_place` is set `#!py3 True`.

## Steps

The `steps` method creates a list of discrete colors. Like mixing, it is also built on [`interpolate`](#interpolating).
Just provide two colors, and specify how many `steps` are wanted.

```playground
Color("red").steps("blue", steps=10)
```

If desired, multiple colors can be provided, and steps will be returned for all the interpolation regions. When
interpolating multiple colors, [piecewise interpolation](#piecewise-interpolation) is used (which is covered in more
detail later).

```playground
Color("red").steps(["orange", "yellow", "green"], steps=10)
```

Steps can also be configured to return colors based on a maximum Delta E distance. This means you can ensure the
distance between all colors is no greater than a certain value.

In this example, we specify the color `#!color color(display-p3 0 1 0)` and interpolate steps between `#!color red`.
The result gives us an array of colors, where the distance between any two colors should be no greater than the Delta E
result of 10.

```playground
Color("display-p3", [0, 1, 0]).steps(
    "red",
    space="lch",
    out_space="srgb",
    max_delta_e=10
)
```

`max_steps` can be used to limit the results of `max_delta_e`. Obviously, this affects the Delta E between the colors
inversely. It should be noted that steps are injected equally between every color when satisfying a max Delta E limit in
order to avoid shifting the midpoint. In some cases, in order to satisfy both the `max_delta_e` and the `max_steps`
requirement, the number of steps may even be clipped such that they are less than the `max_steps` limit. `max_steps` is
set to `#!py3 1000` by default, but can be set to `#!py3 None` if no limit is desired.

```playground
Color("display-p3", [0, 1, 0]).steps(
    "red",
    space="lch",
    out_space="srgb",
    max_delta_e=10,
    max_steps=10
)
```

When specifying a `max_delta_e`, `steps` will function as a minimum required steps and will push the delta even smaller
if the required steps is greater than the calculated steps via the maximum Delta E limit.

```playground
Color("display-p3", [0, 1, 0]).steps(
    "red",
    space="lch",
    out_space="srgb",
    max_delta_e=10,
    steps=50
)
```

The default delta E method is Delta E 76, which is a simple euclidean distancing in the CIELAB color space. While a
Delta E 2000 is far more accurate, it is a much more expensive operation.

## Piecewise Interpolation

The [`interploate`](#interpolating) and [`steps`](#steps) methods allow for piecewise interpolation across multiple
color ranges. Anytime, multiple colors are provided via a list, the piecewise logic will be applied to the various
segments.

```playground
Color('red').interpolate(['white', 'black', 'blue'])
```

When interpolating between two colors, we showed that you can control the transition by setting easing functions to
the `progress` parameter or control hue interpolation with the `hue` parameter. For piecewise interpolation, when
`progress`, `hue`, or `premultiplied` are set via the function parameters, that will be the defaults used between all
the provided colors, but you can also setup specific interpolation configurations between any two colors by using the
[`Piecewise`](./api/index.md#piecewise) object. For instance, in the example below, we can apply an easing between just
the `#!color white` and `#!color black` colors. Notice that we wrap `#!color black` in a `Piecewise` object so that the
easing function is applied to `#!color black` and the color immediately before it (`#!color white`).

```playground
Color('red').interpolate(['white', Piecewise('black', progress=lambda t: t * (2 - t)), 'blue'])
```

Additionally, you can set color stops using the `Piecewise` object's `stop` parameter. This will ensure that the given
color is interpolated at 100% at that percentage of the total interpolation. In the example below, we specify that in
the entire gradient that at 75% the color will be `#!color green`.

```playground
Color('orange').interpolate([Piecewise('green', 0.75), 'blue'])
```

As the base color cannot be wrapped in a `Piecewise` object, the `steps` and `interpolation` method provide a `stop`
parameter that specifically sets a stop for the base color. In the example below, we specify that the base color's stop
will be at 75%, but since the base is always the first color, what it really means is that the color will remain as the
base color until 75% and then begin the transition to the next color. In this case, the gradient remains
`#!color orange` until it reaches 75% and then transitions to `#!color green` completing the full transition at 100%.

```playground
Color('orange').interpolate('green', stop=0.75)
```

And when we put it all together:

```playground
Color('red').interpolate([Piecewise('white', 0.6), Piecewise('black', 0.8), 'blue'], stop=0.4)
```

As previously mentioned, this can also be applied to steps as well.

```playground
Color('red').steps([Piecewise('white', 0.6), Piecewise('black', 0.8), 'blue'], stop=0.4, steps=15)
```

## Undefined/Null/NaN Handling {#null-handling}

Color spaces that have hue coordinates often have rules about when the hue is considered relevant. For instance, in the
HSL color space, if saturation is zero, the hue is considered null. This is because the color is "without color" or
achromatic; therefore, it has no hue, or the hue is undefined.

Many libraries, like [d3-color](https://github.com/d3/d3-color), [chroma.js](https://gka.github.io/chroma.js/), and
[color.js](https://github.com/LeaVerou/color.js), represent null hues with `NaN` (not a number). This is usually done
to make color interpolation easier. Some, like d3-color, are a bit more liberal with `NaN` and will target special cases
that are above and beyond the normal rules to help ensure good interpolation. For instance, they not only mark hue
undefined on HSL colors when saturation is zero, but also when lightness is zero or one hundred (essentially appearing
black or white). In fact, they'll mark saturation as `NaN` when lightness indicates "black" or "white".

ColorAide also uses `NaN`, or in Python `#!py3 float('nan')`, to represent undefined channels. In certain situations,
when a hue is deemed undefined, the hue value will be set to `coloraide.NaN`, which is just a constant containing
`#!py3 float('nan')`.

When interpolating, if one color's channel has a `NaN`, the other color's channel will be used as the result. If both
colors have a `NaN` for the same channel, then `NaN` will be returned.

Notice that in this example, because white's saturation is zero, the hue is undefined. Because the hue is undefined,
when the color is mixed with a second color (`#!color purple`), the hue of the second color is used.

```playground
color = Color('white').convert('hsl')
color.coords()
color2 = Color('purple').convert('hsl')
color2.coords()
color.mix(color2, space="hsl")
```

Technically, any channel can be set to `NaN`. And there are various ways to do this. The
[Color Manipulation documentation](./manipulation.md#undefined-values) goes into the details of how these `Nan` values
naturally occur and the various ways a user and manipulate them.
