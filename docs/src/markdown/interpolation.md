# Color Interpolation

Interpolation is a type of estimation that finds new data points based on the range of a discrete set of known data
points. When used in the context of color, it is finding a color between two colors on an imaginary line that connects
them together within their color space. These lines could be curved or straight, and sometimes they don't even have to
pass through the points, just an approximate path that roughly follows the points. The main thing is that this line
is calculated based on the references, in our case, colors.

Interpolation is often how colors are "mixed", finding a color somewhere on a line that connects two colors, or
gradients, smoothly transitioning through all colors on a line that connects two colors. Interpolation is an extremely
useful and power tool.

One of the most commonly used forms of interpolation is linear interpolation which describes a straight line through
two points. ColorAide currently only implements this form of interpolation and it is the foundation for a number of
useful methods, such as [`steps`](#steps) and [`mix`](#mixing).

## Interpolating

The `interpolate` method allows a user to create a linear interpolation function using two. A returned interpolation
function accepts an input between 0 - 1 and will cause a new color between the specified colors to be returned. If a an
input value exceeds the the range, a color will be returned that is extrapolated on the imaginary line that continues
beyond the specified colors which may be surprising.

By default, colors are interpolated in the perceptually uniform Oklab color space, though any supported color space can
be used instead. This also applies to all methods that use interpolation, such as [steps](#steps), [mix](#mixing), etc.

As an example, below we create an interpolation between `#!color rebeccapurple` and `#!color lch(85% 100 85)`. We then
step through values of `0.1`, `0.2`, `0.3`, etc. This returns colors at various positions on the line that connects
the two colors, `0` returning `#!color rebeccapurple` and `1` returning `#!color lch(85% 100 85)`.

```playground
i = Color("rebeccapurple").interpolate("lch(85% 100 85)", space='lch')
[i(x/10).to_string() for x in range(10)]
```

If we create enough steps, we can create a gradient.

```playground
Color("rebeccapurple").interpolate(
    "lch(85% 100 85)",
    space='lch'
)
```

!!! tip "Interpolating in Constrained Gamuts"
    Some color spaces, like sRGB, have a limited gamut, but have extended ranges that allow them to represent out of
    gamut colors in a sane way. Other models, like HSL, HSV, and HWB have the same limited gamut, but have no sane way
    to represent out of gamut colors. If colors are requested to be interpolated and are too big to be interpolated
    in the requested color space and cannot properly be represented in that space or model, the colors will be gamut
    mapped before interpolation.

Interpolation can also be done across multiple colors. The function, just like when interpolating between two colors,
takes a range of 0 - 1, only this range now applies to the range that spans all the colors, not just two. As it may be
impossible to draw a straight line that passes through a series of colors, [piecewise interpolation](#piecewise-interpolation)
is used at anytime there is more than one color. As this type of interpolation will be cover more later, suffice it to
say that this method breaks up the interpolation into individual segments/pieces consisting of only two of the colors
in the series and applies linear interpolation to these segments/pieces individually.

```playground
Color('black').interpolate(['red', 'white'])
```

## Hue Interpolation

In interpolation, hues are handled special allowing us to control the way in which hues are evaluated. By default, the
shortest angle between two hues is interpolated between, but the `hue` allows us to redefine this behavior in a number
of different ways: `shorter`, `longer`, `increasing`, `decreasing`, and `specified`. Below, we can see how the
interpolation varies using `shorter` vs `longer` (interpolate between the largest angle).

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
`#!color lch(85% 85 805)`. Below we will demonstrate each of the different hue evaluations. To learn more, check out the
[CSS level 4 specification](https://drafts.csswg.org/css-color-4/#hue-interpolation) which describes each one.

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

## Masking

If desired, we can mask off specific channels that we do not wish to interpolate. Masking works by cloning the color
and setting the specified channels as undefined (internally set to `NaN`). When interpolating, if one color's channel
has a `NaN`, the other color's channel will be used as the result, keeping that channel at a constant value. If both
colors have a `NaN` for the same channel, then `NaN` will be returned.

!!! tip "Magic Behind NaN"
    There are times when `NaN` values can happen naturally, such as with achromatic colors with hues. To learn more,
    check out [Undefined Handling/NaN Handling](#null-handling).

In the following example, we have a base color of `#!color lch(52% 58.1 22.7)` which we then interpolate with
`#!color lch(56% 49.1 257.1)`. We then mask off the second color's channels except for `hue`. Applying this logic, we
will end up with a range of colors that maintains the same lightness and chroma as the first color, but with different
hues. We can see as we step through the colors that only the hue is interpolated.

```playground
i = Color("lch(52% 58.1 22.7)").interpolate(
    Color("lch(56% 49.1 257.1)").mask(['lightness', 'chroma', 'alpha']),
    space="lch"
)
[i(x/10).to_string() for x in range(10)]
```

You can also create inverted masks. An inverted mask will mask all *except* the specified channel.

```playground
i = Color("lch(52% 58.1 22.7)").interpolate(
    Color("lch(56% 49.1 257.1)").mask('hue', invert=True),
    space="lch"
)
[i(x/10).to_string() for x in range(10)]
```

!!! tip "Magic Behind Masking"
    Masking actually clones the color, setting the specified channels to undefined values. To learn more about masking
    and undefined values, check out [Undefined Handling](#null-handling).

## Using Easing Functions

Linear interpolation is not only linear in terms of the straightness of the imaginary line connecting two colors, but
also in regards to the rate we travel along that line to return colors. Normally, if we were to request an interpolation
point at `#!py3 0.5`, we'd get a color exactly in the middle between the two colors.

With an easing function we can actually control the rate at which we travel the interpolation line, compressing the rate
at the start or end of the line, elongating the rate in the middle, or compress the rate periodically. The possibilities
are endless.

Sometimes, it is easier to visualize what something means than to just have it explained. Here we apply an easing
function by setting `progress`. Here we change the rate of progress along the line using different easing functions.

```playground
import math

Color("green").interpolate(
    "blue",
    progress=lambda t: t ** 3
)
Color("green").interpolate(
    "blue",
    progress=lambda t: 8 * t ** 4 if t < 0.5 else 1 - ((-2 * t + 2) ** 4) / 2
)
Color("green").interpolate(
    "blue",
    progress=lambda t: math.sin((t * math.pi) / 2)
)
```

ColorAide even lets you apply easing functions to specific channels. This can be done to one or more channels at a time.
Below, we apply `#!py3 t ** 3` to `alpha` while allowing all other channels to interpolate normally.

```playground
Color("lch(50% 50 0)").interpolate(
    "lch(90% 50 20 / 0)",
    progress={
        'alpha': lambda t: t ** 3
    }
)
```

We can also set all the channels to a function via `all` and then override specific channels.

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

!!! tip "Interpolation Options"
    Any options not consumed by `mix` will be passed to the underlying `interpolation` function. This includes options
    like `hue`, `progress`, etc.

The `mix` function is built on top of the [`interpolate`](#interpolating) function and provides a simple, intuitive
interface for mixing two colors. Simply pass in a color to mix with the base color, and you'll get an equal mix of the
two.

```playground
Color("red").mix(Color("blue"))
```

By default, colors are mixed at 50%, but the percentage can be controlled. Here we mix the color `#!color blue` into
the color `#!color red` at 20%. With `#!color blue` at 20% and `#!color red` at 80%, this gives us a more reddish color.

```playground
Color("red").mix(Color("blue"), 0.2)
```

As with all interpolation based functions, if needed, a different color space can be specified with the `space`
parameter. Notice below that this creates a different color. The results of mixing in a different color space may be
more desirable as color mixing may be more natural.

```playground
Color("red").mix(Color("blue"), space="hsl")
```

Mix can also accept a string and will create the color for us which is great if we don't need to work with the second
color afterwards.

```playground
Color("red").mix("blue", 0.2)
```

Mixing will always return a new color unless `in_place` is set `#!py3 True`.

## Steps

!!! tip "Interpolation Options"
    Any options not consumed by `mix` will be passed to the underlying `interpolation` function. This includes options
    like `hue`, `progress`, etc.

The `steps` method provides an intuitive interface to create lists of discrete colors. Like mixing, it is also built on
[`interpolate`](#interpolating). Just provide two colors, and specify how many `steps` are wanted.

```playground
Color("red").steps("blue", steps=10)
```

If desired, multiple colors can be provided, and steps will be returned for all the interpolated segments. When
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

`max_steps` can be used to limit the results of `max_delta_e` in case result balloons to an unexpected size. Obviously,
this affects the Delta E between the colors inversely. It should be noted that steps are injected equally between every
color when satisfying a max Delta E limit in order to avoid shifting the midpoint. In some cases, in order to satisfy
both the `max_delta_e` and the `max_steps` requirement, the number of steps may even be clipped such that they are less
than the `max_steps` limit. `max_steps` is set to `#!py3 1000` by default, but can be set to `#!py3 None` if no limit is
desired.

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

`steps` uses the color class's default ∆E method to calculate max ∆E, the current default ∆E being ∆E^\*^~ab~. While
using something like ∆E^\*^~00~ is far more accurate, it is a much more expensive operation. If desired, the class's
default ∆E can be changed via subclassing the color object and and changing `DELTA_E` class variable or by manually
specifying the method via the `delta_e` parameter.


=== "∆E^\*^~ab~."
    ```playground
    Color("display-p3", [0, 1, 0]).steps(
        "red",
        space="lch",
        out_space="srgb",
        max_delta_e=10,
        delta_e="76"
    )
    ```

=== "∆E^\*^~00~"
    ```playground
    Color("display-p3", [0, 1, 0]).steps(
        "red",
        space="lch",
        out_space="srgb",
        max_delta_e=10,
        delta_e="2000"
    )
    ```

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

## Undefined/NaN Handling {#null-handling}

Color spaces that have hue coordinates often have rules about when the hue is considered relevant. For instance, in the
HSL color space, if saturation is zero, the hue is essentially powerless. This is because the color is "without color"
or achromatic; therefore, the hue can have no affect on the actual color.

ColorAide will generally respect the values a user provides, so if an achromatic HSL color is given a hue of 270
degrees, ColorAide will accept it, but the hue will not affect the color in any meaningful way.

During conversions, such context is lost, and if an achromatic color is converted to the color space like HSL, the
resultant color will have a hue that is noted as undefined. This is simply because there is no good hue for achromatic
colors as they play no part in the color. All hues actually incorrect as achromatic colors have no real hue. Instead,
colors will be returned with a value that represents that the hue is missing or undefined, or maybe better worded, could
not be defined.

Many libraries, like [d3-color](https://github.com/d3/d3-color), [chroma.js](https://gka.github.io/chroma.js/), and
[color.js](https://github.com/LeaVerou/color.js), represent null hues with `NaN` (not a number). This is usually done
to make color interpolation easier. Some, like d3-color, are a bit more liberal with `NaN` and will target special cases
that are above and beyond the normal rules to help ensure good interpolation. For instance, they not only mark hue
undefined on HSL colors when saturation is zero, but they'll mark saturation as `NaN` when lightness indicates "black"
or "white".

ColorAide also uses `NaN`, or in Python `#!py3 float('nan')`, to represent undefined channels. In certain situations,
when a hue is deemed undefined, the hue value will be set to `coloraide.NaN`, which is just a constant containing
`#!py3 float('nan')`.

When interpolating, if one color's channel has a `NaN`, the other color's channel will be used as the result. If both
colors have a `NaN` for the same channel, then `NaN` will be returned.

Notice that in this example, because white's saturation is zero, the hue is undefined. Because the hue is undefined,
when the color is mixed with a second color (`#!color green`), the hue of the second color is used.

```playground
color = Color('white').convert('hsl')
color.coords()
color2 = Color('green').convert('hsl')
color2.coords()
color.mix(color2, space="hsl")
```

But if we manually set the hue to `#!py 0` instead of `NaN`, we can see that the mixing goes quite differently.

```playground
color = Color('white').convert('hsl').set('hue', 0)
color.coords()
color2 = Color('green').convert('hsl')
color2.coords()
color.mix(color2, space="hsl")
```

Technically, any channel can be set to `NaN`. And there are various ways to do this. The
[Color Manipulation documentation](./manipulation.md#undefined-values) goes into the details of how these `Nan` values
naturally occur and the various ways a user and manipulate them.
