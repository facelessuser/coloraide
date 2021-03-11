# Color API

## `Color`

```py3
class Color:
    def __init__(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
```

The `Color` class object is a wrapper around the internal color space objects. It provides an API interface to allow
users to specify and manipulate colors.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py3 None` | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py3 1`    | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `filters`  | `#!py3 None` | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

### `match`

```py3
@classmethod
def match(cls, string, start=0, fullmatch=False, *, filters=None):
```

The `match` class method provides access to the color matching interface and allows a user to provide a color string
and get back a `ColorMatch` object. `ColorMatch` objects contain three properties:

1. `color`: the `Color` object.
2. `start`: the starting point within the string buffer where the color was found.
3. `end`: the ending point within the string buffer where the color was found.

Match does not search the entire buffer, but simply matches at the location specified by `start`.

Return
: 
    Returns a `ColorMatch` object.

Parameters
: 
    Parameters  | Defaults      | Description
    ----------- | ------------- | -----------
    `string`    |               | A string representing the color.
    `start`     | `#!py3 0`     | Accepts a integer offset into the provided string buffer to start the match.
    `fullmatch` | `#!py3 False` | A boolean which defines whether match must match to the end of the string buffer.
    `filters`   | `#!py3 None`  | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

### `new`

```py3
@classmethod
def new(cls, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
```

The `new` class method exposes the interface of creating new color objects. Using `new` is the same as using
[`Color()`](#color).

Return
: 
    Returns a [`Color`](#color) object.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py3 None` | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py3 1`    | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `filters`  | `#!py3 None` | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

### `clone`

```py3
def clone(self):
```

The `clone` method provides a way to create a duplicate of the current `Color` instance.

Return
: 
    Returns a [`Color`](#color) object.


### `update`

```py3
def update(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
```

The `update` method provides a way to update the underlying color spaces with coordinates from any color space. The
methods signature looks just like [`new`](#new) and accepts color strings, `Color` objects, or raw data points specified
with a color space string and coordinates. The object itself will be updated and remain in its current color space.

Return
: 
    Returns a reference to the current `Color` object.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py3 None` | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py3 1`    | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `filters`  | `#!py3 None` | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

### `mutate`


```py3
def mutate(self, color, data=None, alpha=util.DEF_ALPHA, *, filters=None, **kwargs):
```

The `mutate` method is just like [`update`](#update) except that it will not only update the color space, but mutate it
to the provided color space.

Return
: 
    Returns a reference to the current [`Color`](#color) object.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py3 None` | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py3 1`    | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `filters`  | `#!py3 None` | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

### `space`

```py3
def space(self):
```

Retrieves the current color space of the color.

Return
: 
    Returns a string with the name of the current color space.

### `coords`

```py3
def coords(self):
```

Returns a list of the color's coordinates. This does **not** include the alpha channel. Alpha can be accessed via the
`alpha` property or `get` and `set` accessors.

Return
: 
    Returns a list of numbers indicating the current coordinate values.

### `to_string`

```py3
def to_string(self, **kwargs):
```

Method that converts the current color to an output format supported by the color space. While a number of the
parameters are common, some may be specific to the color space. The [usage guide](../strings.md#) covers color space
specific options in more details.

Return
: 
    Returns a string representation of the current color.

Parameters
: 
    Common parameters:

    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `alpha`    | `#!py3 None` | Boolean or `#!py3 None` value which determines whether the output includes `alpha`. If `#!py3 None` (the default) alpha will only be shown if less than 1. If `#!py3 True`, alpha will always be shown. If `#!py3 False`, alpha will be omitted.
    `precision`| `#!py3 5`    | Integer value that sets precision and scale. Precision and scale will match the value if greater than zero. If `0`, values will be rounded to the nearest integer. If `-1`, number will be output at the highest precision.
    `fit`      | `#!py3 True` | A boolean that controls whether gamut mapping is performed on string creation. By default, colors will be fit to their own color space. This can be disabled by setting to `#!py3 False`.
    `color`    | `#!py3 False`| A boolean that will determine if the `color(space coord+ / alpha)` format is used for string output. Has highest precedence.

    sRGB specific parameters:

    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `hex`.     | `#!py3 False`| String output will be in `#RRGGBBAA` format.
    `names`    | `#!py3 False`| Boolean indicating a preference for CSS color names. When translating a color to it's closest hex form, if that hex value matches a CSS color name, that color name will be returned as the output. `hex` does not have to be `#!py3 True` for this to apply.
    `compress` | `#!py3 False`| If `hex` is `#!py3 True` and `compress` is `#!py3 True`, hex values will be compressed if possible: `#RRGGBBAA` --> `#RGBA`.

    Space dependent parameters:

    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `comma`    | `#!py3 False`| If supported by the color space and the current output format, commas will be used instead of space format: `rgba(0, 0, 0, 1)` --> `rgb(0 0 0 /1)`.

### `convert`

```py3
def convert(self, space, *, fit=False, in_place=False):
```

Converts a [`Color`](#color) object from one color space to another. If the current color space matches the specified
color space, the object will be cloned.

Return
: 
    Returns a reference to the converted [`Color`](#color) object. If `in_place` is `True`, the return will be a
    reference to the current [`Color`](#color) object.

Parameters
: 
    Parameters | Defaults      | Description
    ---------- | ------------- | -----------
    `space`    |               | A string representing the desired final color space.
    `fit`      | `#!py3 False` | Boolean specifying whether the current color should be gamut mapped into the final, desired color space.
    `in_place` | `#!py3 False` | Boolean specifying whether the convert should alter the current [`Color`](#color) object or return a new one.

### `luminance`

```py3
def luminance(self):
```

Get the relative luminance. Relative luminance is obtained from the Y coordinate in the XYZ color space.

Return
: 
    Returns an float indicating the relative luminance.

### `contrast`

```py3
def contrast(self, color):
```

Get the contrast ratio based on the relative luminance between two colors.

Return
: 
    Returns a float indicating the contrast ratio between two colors.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string or [`Color`](#color) object representing a color.


### `distance`

```py3
def distance(self, color, *, space=util.DEF_DISTANCE_SPACE):
```

Performs a euclidean distance algorithm on two colors.

Return
: 
    Returns a float indicating euclidean distance between the two colors.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `color`    |              | A color string or [`Color`](#color) object representing a color.
    `space`    | `#!py3 "lab"`| Color space to perform distancing algorithm in.

### `delta_e`

```py3
def delta_e(self, color, *, method=None, **kwargs):
```

Performs a delta E distance algorithm on two colors. Default algorithm that is used is Delta E 1976 (`76`). Some methods
have additional weighting that can be configured through method specific options which are represented by `**kwargs`.

Available methods:

Name             | Input
---------------- | -----
CIE76            | `76`
CIE94            | `94`
CIEDE2000        | `2000`
CMC\ l:c\ (1984) | `cmc`

Return
: 
    Returns a float indicating the delta E distance between the two colors.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `color`    |              | A color string or [`Color`](#color) object representing a color.
    `method`   | `#!py3 None` | String that specifies the method to use. If `#!py3 None`, the default will be used.

### `interpolate`

```py3
def interpolate(self, color, *, space="lab", progress=None, out_space=None, adjust=None, hue=util.DEF_HUE_ADJ, premultiplied=False):
```

The `interpolate` method creates a function that takes a value between 0 - 1 and interpolates a new color based on the
input value.

Interpolation can be customized by limiting the interpolation to specific color channels, providing custom interpolation
functions, and even adjusting the hue logic used.

Hue\ Evaluation | Description
--------------- | -----------
`shorter`       | Angles are adjusted so that θ₂ - θ₁ ∈ [-180, 180].
`longer`        | Angles are adjusted so that θ₂ - θ₁ ∈ {0, [180, 360)}.
`increasing`    | Angles are adjusted so that θ₂ - θ₁ ∈ [0, 360).
`decreasing`    | Angles are adjusted so that θ₂ - θ₁ ∈ (-360, 0]
`specified`     | No fixup is performed. Angles are interpolated in the same way as every other component.

Parameters
: 
    Parameters      | Defaults          | Description
    --------------- | ----------------- | -----------
    `color`         |                   | A color string or [`Color`](#color) object representing a color.
    `space`         | `#!py3 "lab"`     | Color space to interpolate in.
    `progress`      | `#!py3 None`      | An optional function that that allows for custom logic to perform non-linear interpolation.
    `out_space`     | `#!py3 None`      | Color space that the new color should be in. If `#!py3 None`, the color will be in the same color space as the base color.
    `adjust`        | `#!py3 None`      | A list of channel names that should be interpolated. If `#!py3 None`, all channels will be interpolated.
    `hue`           | `#!py3 "shorter"` | Define how color spaces which have hue angles are interpolated. Default evaluates between the shortest angle.
    `premultiplied` | `#!py3 False`     | Use premultiplied alpha when interpolating.

### `steps`

```py3
def steps(self, color, *, steps=2, max_steps=1000, max_delta_e=0, **interpolate_args):
```

Creates an `interpolate` function and iterates through it with user defined step parameters to produce discrete color
steps. Will attempt to provide the minimum number of `steps` without exceeding `max_steps`. If `max_delta_e` is
provided, the distance between each stop will be cut in half until there are no colors with a distance greater than the
specified `max_delta_e`.

Return
: 
    List of [`Color`](#color) objects.


Parameters
: 
    Parameters   | Defaults           | Description
    ------------ | ------------------ | -----------
    `color`      |                    | A color string or [`Color`](#color) object representing a color.
    `steps`      | `#!py3 2`          | Minimum number of steps.
    `max_steps`  | `#!py3 1000`       | Maximum number of steps.
    `max_delta_e`| `#!py3 0`          | Maximum delta E distance between the color stops. A value of `0` or less will be ignored.

    !!! note
        All other keyword arguments defined in `**interpolate_args` will be passed to the `interpolate` method.

### `mix`

```py3
def mix(self, color, percent=util.DEF_MIX, *, space=None, in_place=False, **interpolate_args):
```

Interpolates between two colors returning a color that represents the mixing of the base color and the provided `color`
mixed at the provided `percent`, where `percent` applies to how much the provided `color` contributes to the the final
result.

Return
: 
    Returns a reference to the new [`Color`](#color) object or a reference to the current [`Color`](#color) if
    `in_place` is `#!py3 True`.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `color`    |                    | A color string or [`Color`](#color) object representing a color.
    `percent`  | `#!py3 0.5`        | A numerical value between 0 - 1 representing the percentage at which the parameter `color` will be mixed.
    `space`    | `#!py3 None`       | A string specifying the color space in which the "mixing"/interpolation is done. If `#!py3 None`, the base color's color space will be used.
    `in_place` | `#!py3 False`      | Boolean used to determine if the the current color should be modified "in place" or a new [`Color`](#color) object should be returned.


### `fit`

```py3
def fit(self, space=None, *, method=None, in_place=False):
```

Fits color to the current or specified color gamut.

By default, `lch-chroma` gamut mapping is used. This is essentially an approach that holds lightness and hue constant
in the LCH color space while reducing chroma until the color is in gamut. Clipping is done at each step of the way and
the color distance measured to see how close our color is to the intended color.

The supported gamut mapping methods are:

Name       | Input
---------- | -----
LCH Chroma | `lch-chroma`
Clipping   | `clip`

Return
: 
    Returns a reference to the new [`Color`](#color) object or a reference to the current [`Color`](#color) if
    `in_place` is `#!py3 True`.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `space`    | `#!py3 None`       | The color space that the color must be mapped to. If space is `#!py3 None`, then the current color space will be used.
    `method`   | `#!py3 None`       | String that specifies which gamut mapping method to use. If `#!py3 None`, `lch-chroma` will be used.

### `in_gamut`

```py3
def in_gamut(self, space=None, *, tolerance=util.DEF_FIT_TOLERANCE):
```

Checks if the current color is in the current or specified gamut.

Parameters
: 
    Parameters | Defaults         | Description
    ---------- | ---------------- | -----------
    `space`    | `#!py3 None`     | The color space that the color must be fit within. If space is `#!py3 None`, then the current color space will be used.
    `tolerance`| `#!py3 0.000075` | Tolerance allowed when checking bounds of color.

### `get`

```py3
def get(self, name):
```

Retrieves the coordinate value from the specified channel. Channel must be a channel name in the current color space or
a channel name in the specified color space using the syntax: `space.channel`.

Return
: 
    Returns a numerical value that is stored internally for the specified channel, or a calculated value in the case
    that a channel in a different color space is requested.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `name`     |                    | Channel name or color space and channel name to retrieve value from.

### `set`

```py3
def set(self, name, value):  # noqa: A003
```

Sets the given value to the specified channel. If the `name` is provided in the form `space.channel`, the value will be
applied to the channel of the specified color space while keeping current color space the same.

The `value` can be a numerical value, a CSS string compatible with the specified color space, or a function that accepts
a numerical channel value and returns a numerical channel value.

This function returns the current colors reference so that multiple sets can be chained together.

Return
: 
    Returns a reference to the current [`Color`](#color) object.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `name`     |                    | Channel name or color space and channel name to retrieve value from.
    `value`    |                    | A numerical value, a string value accepted by the specified color space, or a function.

### `is_nan`

```py3
def is_nan(self, name):
```

Retrieves the coordinate value from the specified channel and checks whether the value is `NaN`. Channel must be a
channel name in the current color space or a channel name in the specified color space using the syntax:
`space.channel`.

Return
: 
    Returns a boolean indicating whether the specified color space's channel is `NaN`.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `name`     |                    | A string indicating what channel property to check.

### Dynamic Channel Properties

Depending on the given color space, channel properties will be available on the color object as well. These are
dynamically available depending on what the current color space is.

For instance, if the color space is sRGB, the channels `red`, `green`, `blue`, and `alpha` will all be available.

These properties are read and writable. When read, they will return the numerical value stored in the specified channel.
When written, they can accept a numerical value or a string value using CSS syntax acceptable for that channel in that
color space.

For more complex setting operations, or to chain multiple set operations, please use [`get`](#get).
