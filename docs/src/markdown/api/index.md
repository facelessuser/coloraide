# Color API

## `coloraide.NaN` {#nan}

Description
: `NaN` is a convenience constant for `float('nan')`.

Import path
: 
    `NaN` is imported from the `coloraide` library:

    ```py3
    from coloraide import NaN
    ```

## `coloraide.stop` {#stop}

```py3
class stop(
    color,
    s
):
```

Description
: 
    `stop` objects are used in [`interpolate`](#interpolate) methods. They allow a user to control specify a color stop
    for a given color during the interpolation process.

Import Path
: 
    `stop` is imported from `coloraide` library:

    ```py3
    from coloraide import stop
    ```

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, a dictionary describing the color, or another `Color` class object.
    `value`    |              | A numerical value specifying the new color stop for the given color.

## `coloraide.hint` {#hint}

```py3
class hint(
    mid,
):
```

Description
: 
    `hint` returns an easing function that adjust the midpoint between two color stops.

Import Path
: 
    `hint` is imported from `coloraide` library:

    ```py3
    from coloraide import hint
    ```

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `mid`      |              | A numerical value, relative to the two color stops it occurs between, that will be used as the new midpoint.

## `coloraide.Color` {#color}

```py3
class Color:
    def __init__(
        self,
        color,
        data=None,
        alpha=util.DEF_ALPHA,
        *,
        filters=None, **kwargs
    ):
```

Description
: 
    The `Color` class object is a wrapper around the internal color space objects. `Color` is the base Color object
    and only registers a select number of color spaces. It provides an API interface to allow users to specify and
    manipulate colors. Color objects can be iterated, which will return each color channel. They are also indexable by
    channel name or by channel index.

Import path
: 
    `Color` is imported from the `coloraide` library:

    ```py3
    from coloraide import Color
    ```

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, a dictionary describing the color, or another `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py3 None` | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py3 1`    | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `filters`  | `#!py3 None` | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

## `coloraide.everything.ColorAll` {#colorall}

```py3
class ColorAll(Color):
    def __init__(
        self,
        color,
        data=None,
        alpha=util.DEF_ALPHA,
        *,
        filters=None, **kwargs
    ):
```

Description
: 
    The `ColorAll` class object is derived from [`Color`](#color) and extends the registered color spaces to include all
    offered by ColorAide.

Import path
: 
    `ColorAll` is imported from the `coloraide` library:

    ```py3
    from coloraide.everything import ColorAll
    ```

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, a dictionary describing the color, or another `ColorAll` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py3 None` | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py3 1`    | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `filters`  | `#!py3 None` | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.


## `Color.register` {#register}

```py
@classmethod
def register(
    cls,
    plugin,
    *,
    overwrite=False,
    silent=False
):
```

Description
: 
    Register a plugin(s).

Parameters
: 
    Parameters  | Defaults      | Description
    ----------- | ------------- | -----------
    `plugin`    |               | A plugin object or list of plugin objects to register.
    `overwrite` | `#!py3 False` | `overwrite` will avoid allow an already registered plugin to be overwritten if the plugin to register specifies a `name` that is already used for registration.
    `silent`    | `#!py3 False` | `silent` will avoid throwing an error if the `name` is already found in the specified category.

## `Color.deregister` {#deregister}

```py
@classmethod
def deregister(
    cls,
    plugin,
    *,
    silent=False
):
```

Description
: 
    Remove an already registered plugin(s).

Parameters
: 
    Parameters  | Defaults       | Description
    ----------- | -------------- | -----------
    `plugin`    |                | A string or list of strings that describe the plugin to be removed. Strings should be in the format `category:name` where `category` is either `space`, `delta-e`, or `fit` and `name` is the name the plugin was registered under. `*` will remove all plugins and `category:*` will remove all within a specific category.
    `silent`     | `#!py3 False` | `silent` will avoid throwing an error if the `name` can not be found in the specified category.

## `Color.match` {#match}

```py3
@classmethod
def match(
    cls,
    string,
    start=0,
    fullmatch=False,
    *,
    filters=None
):
```

Description
: 
    The `match` class method provides access to the color matching interface and allows a user to provide a color string
    and get back a `ColorMatch` object. `ColorMatch` objects contain three properties:

    ```py3
    class ColorMatch:
        def __init__(
            self,
            color,
            start,
            end
        ):
    ```

    1. `color`: the `Color` object.
    2. `start`: the starting point within the string buffer where the color was found.
    3. `end`: the ending point within the string buffer where the color was found.

    Match does not search the entire buffer, but simply matches at the location specified by `start`.

Parameters
: 
    Parameters  | Defaults      | Description
    ----------- | ------------- | -----------
    `string`    |               | A string representing the color.
    `start`     | `#!py3 0`     | Accepts an integer offset into the provided string buffer to start the match.
    `fullmatch` | `#!py3 False` | A boolean which defines whether match must match to the end of the string buffer.
    `filters`   | `#!py3 None`  | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

Return
: 
    Returns a `ColorMatch` object.

## `Color.new` {#new}

```py3
def new(
    self,
    color,
    data=None,
    alpha=util.DEF_ALPHA,
    *,
    filters=None,
    **kwargs
):
```

Description
: 
    The `new` class method exposes the interface of creating new color objects. Using `new` is the same as using
    [`Color()`](#color).

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py3 None` | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py3 1`    | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `filters`  | `#!py3 None` | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

Return
: 
    Returns a [`Color`](#color) object.

## `Color.random` {#random}

```py3
@classmethod
def random(
    cls,
    space,
    *,
    limits=None
):
```

Description
: 
    Generate a random color in the provided `space`. The color space's channel range will be used as a limit for the
    channel. For color spaces with no clearly defined gamut, these values can be arbitrary. In such cases, it may be
    advisable to fit the returned color space to a displayable gamut.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `space`    |              | The color space name in which to generate a random color in.
    `limits`   | `#!py3 None` | An optional list of constraints for various color channels. Each entry should either be a sequence contain a minimum and maximum value, or should be `#!py3 None`. `#!py3 None` values will be ignored and the color space's specified channel range will be used instead. Any missing entries will be treated as `#!py3 None`.

Return
: 
    Returns a [`Color`](#color) object.

## `Color.clone` {#clone}

```py3
def clone(
    self
):
```

Description
: 
    The `clone` method provides a way to create a duplicate of the current `Color` instance.

Return
: 
    Returns a [`Color`](#color) object.


## `Color.update` {#update}

```py3
def update(
    self,
    color,
    data=None,
    alpha=util.DEF_ALPHA,
    *,
    filters=None,
    **kwargs
):
```

Description
: 
    The `update` method provides a way to update the underlying color spaces with coordinates from any color space. The
    methods signature looks just like [`new`](#new) and accepts color strings, `Color` objects, or raw data points
    specified with a color space string and coordinates. The object itself will be updated and remain in its current
    color space.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py3 None` | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py3 1`    | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `filters`  | `#!py3 None` | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

Return
: 
    Returns a reference to the current `Color` object.

## `Color.mutate` {#mutate}


```py3
def mutate(
    self,
    color,
    data=None,
    alpha=util.DEF_ALPHA,
    *,
    filters=None,
    **kwargs
):
```

Description
: 
    The `mutate` method is just like [`update`](#update) except that it will not only update the color space, but mutate
    it to the provided color space.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py3 None` | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py3 1`    | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `filters`  | `#!py3 None` | `filters` accepts a list of color spaces to allow. When `#!py3 None` is provided (the default) all supported color spaces are accepted.

Return
: 
    Returns a reference to the current [`Color`](#color) object.

## `Color.convert` {#convert}

```py3
def convert(
    self,
    space,
    *,
    fit=False,
    in_place=False
):
```

Description
: 
    Converts a [`Color`](#color) object from one color space to another. If the current color space matches the
    specified color space, the object will be cloned.

Parameters
: 
    Parameters | Defaults      | Description
    ---------- | ------------- | -----------
    `space`    |               | A string representing the desired final color space.
    `fit`      | `#!py3 False` | Parameter specifying whether the current color should be gamut mapped into the final, desired color space. If set to `#!py3 True`, the color will be gamut mapped using the default gamut mapping method. If set to a string, the string will be interpreted as the name of the gamut mapping method to be used.
    `in_place` | `#!py3 False` | Boolean specifying whether the convert should alter the current [`Color`](#color) object or return a new one.

Return
: 
    Returns a reference to the converted [`Color`](#color) object. If `in_place` is `True`, the return will be a
    reference to the current [`Color`](#color) object.

## `Color.space` {#space}

```py3
def space(
    self
):
```

Description
: 
    Retrieves the current color space of the color.

Return
: 
    Returns a string with the name of the current color space.

## `Color.normalize` {#normalize}

```py3
def to_dict(
    self
):
```

Description
: 
    Force normalization of a color's channels by cleaning up channels that shouldn't be undefined and setting any
    channels to undefined if they meet the specific color's criteria dictating such, e.g., hue is undefined in HSL when
    saturation is zero. Normalize modifies the current color in place.

Return
: 
    Returns a reference to the current [`Color`](#color) object after normalizing the channels for undefined hues.

## `Color.to_dict` {#to_dict}

```py3
def to_dict(
    self,
    **kwargs
):
```

Description
: 
    Dump the color object to a simple dictionary.

Return
: 
    A dictionary containing the color space name, the channel name with their respective values.

## `Color.to_string` {#to_string}

```py3
def to_string(
    self,
    **kwargs
):
```

Description
: 
    Method that converts the current color to an output format supported by the color space. While a number of the
    parameters are common, some may be specific to the color space. The [usage guide](../strings.md#) covers color space
    specific options in more details.

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

Return
: 
    Returns a string representation of the current color.

## `Color.luminance` {#luminance}

```py3
def luminance(
    self
):
```

Description
: 
    Get the relative luminance. Relative luminance is obtained from the Y coordinate in the XYZ color space. XYZ, in
    this case, has a D65 white point.

Return
: 
    Returns an float indicating the relative luminance.

## `Color.contrast`

```py3
def contrast(
    self,
    color
):
```

Description
: 
    Get the contrast ratio based on the relative luminance between two colors.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string or [`Color`](#color) object representing a color.

Return
: 
    Returns a float indicating the contrast ratio between two colors.

## `Color.distance` {#distance}

```py3
def distance(
    self,
    color,
    *,
    space=util.DEF_DISTANCE_SPACE
):
```

Description
: 
    Performs a euclidean distance algorithm on two colors.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `color`    |              | A color string or [`Color`](#color) object representing a color.
    `space`    | `#!py3 "lab"`| Color space to perform distancing algorithm in.

Return
: 
    Returns a float indicating euclidean distance between the two colors.

## `Color.delta_e` {#delta_e}

```py3
def delta_e(
    self,
    color,
    *,
    method=None,
    **kwargs
):
```

Description
: 
    Performs a delta E distance algorithm on two colors. Default algorithm that is used is Delta E 1976 (`76`). Some
    methods have additional weighting that can be configured through method specific options which are represented by
    `**kwargs`.

    Available methods:

    Name                                     | Input           | Parameters
    ---------------------------------------- | --------------- | --------------------
    [∆E^\*^~ab~][de76]\ (CIE76)              | `76`            |
    [∆E^\*^~cmc~][decmc]\ (CMC\ l:c\ (1984)) | `cmc`           | `l=2, c=1`
    [∆E^\*^~94~][de94]\ (CIE94)              | `94`            | `kl=1, k1=0.045, k2=0.015`
    [∆E^\*^~00~ ][de2000]\ (CIEDE2000)       | `2000`          | `kl=1, kc=1, kh=1`
    [∆E~itp~][deitp]\ (ICtCp)                | `itp`           | `scalar=720`
    [∆E~z~][dez]\ (Jzazbz)                   | `jz`            |
    [∆E~99o~][de99o]\ (DIN99o)               | `99o`           |
    [∆E~HyAB~][dehyab]\ (HyAB)               | `hyab`          | `space="lab"`
    ∆E~ok~                                   | `ok`            | `scalar=1`

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `color`    |              | A color string or [`Color`](#color) object representing a color.
    `method`   | `#!py3 None` | String that specifies the method to use. If `#!py3 None`, the default will be used.
    `**kwargs` |              | Any distancing specific parameters to pass to ∆E method.

Return
: 
    Returns a float indicating the delta E distance between the two colors.

## `color.closest` {#closest}

```py3
def closest(
    self,
    colors,
    *,
    method=None,
    **kwargs
):
```

Description
: 
    Given a list of colors, calculates the closest color to the calling color object.

Parameters
: 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `colors`   |              | A list of color strings, [`Color`](#color) object, or dictionary representing a color.
    `method`   | `#!py3 None` | String that specifies the method of color distancing to use.
    `**kwargs` |              | Any distancing specific parameters to pass to ∆E method.

Return
: 
    The [`Color`](#color) that is closest to the calling color object. In the off chance that an empty list is passed in
    `#!py3 None` will be returned.

## `color.mask` {#mask}

```py3
def mask
    self,
    channels,
    invert=False,
    in_place=False
):
```

Description
: 
    The `mask` method will set any and all specified channels to `NaN`. If `invert` is set to `#!py3 True`, `mask` will
    set any and all channels not specified to `NaN`.

Parameters
: 
    Parameters  | Defaults      | Description
    ----------- | ------------- | -----------
    `channel`   |               | A string specifying a channel, or a list of strings specifying multiple channels. Specified channels will be masked (or the only channels not masked if `invert` is `#!py3 True`).
    `invert`    | `#!py3 False` | Use inverse masking logic and mask all channels that are not specified.
    `in_place`  | `#!py3 False` | Boolean used to determine if the current color should be modified "in place" or a new [`Color`](#color) object should be returned.

Return
: 
    Returns a reference to the masked [`Color`](#color) object. If `in_place` is `True`, the return will be a
    reference to the current [`Color`](#color) object.

## `Color.interpolate` {#interpolate}

```py3
@classmethod
def interpolate(
    cls,
    colors,
    *,
    stop=0,
    space="lab",
    progress=None,
    out_space=None,
    hue=util.DEF_HUE_ADJ,
    premultiplied=True,
    extrapolate=False,
    method='linear'
):
```

Description
: 
    The `interpolate` method creates a function that takes a value between 0 - 1 and interpolates a new color based on
    the input value.

    If more than one color is provided, the returned function will span the interpolations between all the provided
    colors with the same range of 0 - 1.

    Interpolation can be customized by limiting the interpolation to specific color channels, providing custom
    interpolation functions, and even adjusting the hue logic used.

    [`stop`](#stop) objects can wrapped around colors to specify new color stops and easing functions can be placed
    between colors to alter the transition progress between the two colors.

    Hue\ Evaluation | Description
    --------------- | -----------
    `shorter`       | Angles are adjusted so that θ₂ - θ₁ ∈ [-180, 180].
    `longer`        | Angles are adjusted so that θ₂ - θ₁ ∈ {0, [180, 360)}.
    `increasing`    | Angles are adjusted so that θ₂ - θ₁ ∈ [0, 360).
    `decreasing`    | Angles are adjusted so that θ₂ - θ₁ ∈ (-360, 0]
    `specified`     | No fixup is performed. Angles are interpolated in the same way as every other component.

    The method of interpolation to can also be selected via the `method` parameter.

    Method     | Description
    ---------- | -----------
    `linear`   | An linear interpolation that employs piecewise logic to interpolate between two or more colors.
    `bspline`  | An interpolation method that employs cubic B-spline curves to calculate an interpolation path through multiple colors.
    `natural`  | A natural interpolation spline based on the cubic B-spline curve.
    `monotone` | An interpolation method that utilizes a monotonic cubic spline based on the Hermite spline.
    `catrom`   | Interpolation based on the Catmull-Rom cubic spline.

Parameters
: 
    Parameters      | Defaults          | Description
    --------------- | ----------------- | -----------
    `color`         |                   | A list of color strings, [`Color`](#color) objects, dictionaries representing a color, [`stop`](#piecewise) objects, or easing functions.
    `space`         | `#!py3 "lab"`     | Color space to interpolate in.
    `progress`      | `#!py3 None`      | An optional function that that allows for custom logic to perform non-linear interpolation.
    `out_space`     | `#!py3 None`      | Color space that the new color should be in. If `#!py3 None`, the color will be in the same color space as the base color.
    `hue`           | `#!py3 "shorter"` | Define how color spaces which have hue angles are interpolated. Default evaluates between the shortest angle.
    `premultiplied` | `#!py3 True`      | Use premultiplied alpha when interpolating.
    `extrapolate`   | `#!py3 False`     | Interpolations should extrapolate when values exceed the domain range ([0, 1] by default).
    `domain`        | `#!py3 None`      | A list of numbers defining the domain range of the interpolation.
    `method`        | `#!py3 "linear"`  | The interpolation method to use.

Return
: 
    Returns a function that takes a range from `[0..1]`. The function returns a reference to the interpolated
    [`Color`](#color) object.

## `Color.steps` {#steps}

```py3
def steps(
    self,
    color,
    *,
    steps=2,
    max_steps=1000,
    max_delta_e=0,
    delta_e=None,
    **interpolate_args
):
```

Description
: 
    Creates an `interpolate` function and iterates through it with user defined step parameters to produce discrete
    color steps. Will attempt to provide the minimum number of `steps` without exceeding `max_steps`. If `max_delta_e`
    is provided, the distance between each stop will be cut in half until there are no colors with a distance greater
    than the specified `max_delta_e`. The default ∆E method is used by default, but it can be changed with the `delta_e`
    parameter.

    If more than one color is provided, the steps will be returned from the interpolations between all the provided
    colors.

    Like [`interpolate`](#interpolate), the default interpolation space is `lab`.

Parameters
: 
    Parameters                 | Defaults                           | Description
    -------------------------- | ---------------------------------- | -----------
    `color`                    |                                    | A list of color strings, [`Color`](#color) objects, dictionaries representing a color, [`stop`](#piecewise) objects, or easing functions.
    `steps`                    | `#!py3 2`                          | Minimum number of steps.
    `max_steps`                | `#!py3 1000`                       | Maximum number of steps.
    `max_delta_e`              | `#!py3 0`                          | Maximum delta E distance between the color stops. A value of `0` or less will be ignored.
    `delta_e`                  | `#!py3 None`                       | A string indicating which [∆E method](../distance.md#delta-e) to use. If nothing is supplied, the class object's current default ∆E method will be used.
    `#!py3 **interpolate_args` | See\ [`interpolate`](#interpolate) | Keyword arguments defined in [`interpolate`](#interpolate).

Return
: 
    List of [`Color`](#color) objects.

## `Color.mix` {#mix}

```py3
def mix(
    self,
    color,
    percent=util.DEF_MIX,
    *,
    in_place=False,
    **interpolate_args
):
```

Description
: 
    Interpolates between two colors returning a color that represents the mixing of the base color and the provided
    `color` mixed at the provided `percent`, where `percent` applies to how much the provided `color` contributes to the
    the final result.

Parameters
: 
    Parameters                 | Defaults                           | Description
    -------------------------- | ---------------------------------- | -----------
    `color`                    |                                    | A color string or [`Color`](#color) object representing a color.
    `percent`                  | `#!py3 0.5`                        | A numerical value between 0 - 1 representing the percentage at which the parameter `color` will be mixed.
    `in_place`                 | `#!py3 False`                      | Boolean used to determine if the the current color should be modified "in place" or a new [`Color`](#color) object should be returned.
    `#!py3 **interpolate_args` | See\ [`interpolate`](#interpolate) | Keyword arguments defined in [`interpolate`](#interpolate).

Return
: 
    Returns a reference to the new [`Color`](#color) object or a reference to the current [`Color`](#color) if
    `in_place` is `#!py3 True`.

## `Color.filter` {#cvd}

```py
def filter(
    self,
    name,
    amount=None,
    *,
    space='srgb-linear',
    in_place=False,
    **kwargs: Any
):
```

Description
: 
    Apply a color filter to alter a given color. Filters are based on the W3C [Filter Effects][filter-effects] and
    behave in the same manner. Colors are evaluated in the sRGB Linear color space unless otherwise specified via the
    `space` parameter. No other color space will be accepted except sRGB and sRGB Linear.

    An `amount` can be provided to adjust how much the color is filtered. Any clamping that occurs with the `amount`
    parameter, and related ways in which `amount` are applied, follow the W3C [Filter Effects][filter-effects] spec.

    Some filters, such as CVDs, may take additional arguments via `kwargs`.

    Filters           | Name         | Default
    ----------------- | ------------ | -------
    Brightness        | `brightness` | `#!py3 1`
    Saturation        | `saturate`   | `#!py3 1`
    Contrast          | `contrast`   | `#!py3 1`
    Opacity           | `opacity`    | `#!py3 1`
    Invert            | `invert`     | `#!py3 1`
    Hue\ rotation     | `hue-rotate` | `#!py3 0`
    Sepia             | `sepia`      | `#!py3 1`
    Grayscale         | `grayscale`  | `#!py3 1`
    Protanopia\ CVD   | `protan`     | `#!py3 1`
    Deuteranopia\ CVD | `deutan`     | `#!py3 1`
    Tritanopia\ CVD   | `tritan`     | `#!py3 1`

Parameters
: 
    Parameters                 | Defaults                           | Description
    -------------------------- | ---------------------------------- | -----------
    `name`                     |                                    | The name of the filter that should be applied.
    `amount`                   | See\ above                         | A numerical value adjusting to what degree the filter is applied. Input range can vary depending on the filter being used. Default can also dependent on the filter being used.
    `space`                    | `#!py3 None`                       | Controls the algorithm used for simulating the given CVD.
    `in_place`                 | `#!py3 False`                      | Boolean used to determine if the the current color should be modified "in place" or a new [`Color`](#color) object should be returned. 
    `**kwargs`                 |                                    | Additional filter specific parameters.

    CVDs also take an optional `method` parameter that allows for specifying the CVD algorithm to use.

    Simulation\ Approach             | Name
    -------------------------------- | ----
    Brettel 1997                     | `brettel`
    Viénot, Brettel, and Mollon 1999 | `vienot`
    Machado 2009                     | `machado`

Return
: 
    Returns a reference to the new [`Color`](#color) object or a reference to the current [`Color`](#color) if
    `in_place` is `#!py3 True`.

## `Color.harmony` {#harmony}

```py
def harmony(
    self,
    name,
    *,
    space
):
```

Description
: 
    The `harmony` method uses the current color and returns a set of harmonious colors (including the current color).
    The color harmonies are based on the classical color harmonies of color theory. By default, harmonious colors are
    performed under the perceptually uniform OkLCh color space, but other cylindrical color spaces can be used.

    Harmony             | Name
    ------------------- | ------------
    Monochromatic       | `mono`
    Complementary       | `complement`
    Split\ Complement   | `split`
    Analogous           | `analogous`
    Triadic             | `triad`
    Tetradic\ Square    | `square`
    Tetradic\ Rectangle | `rectangle`

Parameters
: 
    Parameters                 | Defaults                           | Description
    -------------------------- | ---------------------------------- | -----------
    `name`                     |                                    | Name of the color harmony to use.
    `space`                    | `#!py3 'oklch'`                    | Color space under which the harmonies will be calculated. Must be a cylindrical space unless using `mono` which can take non cylindrical spaces.

Return
: 
    Returns a list of [`Color`](#color) objects.

## `Color.compose` {#compose}

```py
def compose(
    self,
    backdrop,
    *,
    blend=None,
    operator=None,
    space=None,
    out_space=None,
    in_place=False
):
```

Description
: 
    Apply compositing which consists of a [blend mode](../compositing.md#blend-modes) and a [Porter Duff operator](../compositing.md#compositing-operators) for alpha compositing. The current color is treated as the source (top
    layer) and the provided color as the backdrop (bottom layer). Colors will be composited in the `srgb` color space
    unless otherwise specified.

    Colors should generally be RGB-ish colors (sRGB, Display P3, A98 RGB, etc.). Some non-RGB-ish colors may work okay,
    with the defaults, but many the algorithm is really designed for RGB-ish colors. Non-RGB-ish colors are likely to
    provide nonsense results.

    Supported blend modes are:

    Blend Modes  | &nbsp;       | &nbsp;       | &nbsp;
    ------------ | ------------ | ------------ | ------------
    `normal`     | `multiply`   | `darken`     | `lighten`
    `burn`       | `dodge`      | `screen`     | `overlay`
    `hard-light` | `exclusion`  | `difference` | `soft-light`
    `hue`        | `saturation` | `luminosity` | `color`
    `color`      | `hue`        | `saturation` | `luminosity`

    Supported Port Duff operators are:

    Operators          | &nbsp;        | &nbsp;             | &nbsp;
    ------------------ | ------------- | ------------------ | ------------
    `clear`            | `copy`        | `destination`      |`source-over`
    `destination-over` | `source-in`   | `destination-in`   | `source-out`
    `destination-out`  | `source-atop` | `destination-atop` | `xor`
    `lighter`          | &nbsp;        | &nbsp;             | &nbsp;

Parameters
: 
    Parameters                 | Defaults                           | Description
    -------------------------- | ---------------------------------- | -----------
    `backdrop`                 |                                    | A background color represented with either a string or [`Color`](#color) object.
    `blend`                    | `#!py3 None`                       | A blend mode to use to use when compositing. Values should be a string specifying the name of the blend mode to use. If `#!py3 None`, [`normal`](#normal) will be used. If `#!py3 False`, blending will be skipped.
    `operator`                 | `#!py3 None`                       | A Porter Duff operator to use for alpha compositing. Values should be a string specifying the name of the operator to use. If `#!py3 None`, [`source-over`](#source-over) will be used. If `#!py3 False`, alpha compositing will be skipped.
    `space`                    | `#!py3 None`                       | A color space to perform the overlay in. If `#!py3 None`, the base color's space will be used.
    `out_space`                | `#!py3 None`                       | A color space to output the resultant color to.
    `in_place`                 | `#!py3 False`                      | Boolean used to determine if the the current color should be modified "in place" or a new [`Color`](#color) object should be returned.

Return
: 
    Returns a reference to the new [`Color`](#color) object or a reference to the current [`Color`](#color) if
    `in_place` is `#!py3 True`.

## `Color.clip` {#clip}

```py
def clip(
    self,
    space=None
)
```

Description
: 
    Performs simple clipping on color channels that are out of gamut.

Parameters
: 
    Parameters | Defaults      | Description
    ---------- | ------------- | -----------
    `space`    | `#!py3 None`  | The color space that the color must be mapped to. If space is `#!py3 None`, then the current color space will be used.

Return
: 
    Returns a reference to the current [`Color`](#color) after fitting its coordinates to the specified gamut.

## `Color.fit` {#fit}

```py3
def fit(
    self,
    space=None,
    *,
    method=None,
    **kwargs
):
```

Description
: 
    Fits color to the current or specified color gamut.

    By default, `oklch-chroma` gamut mapping is used. This is essentially an approach that holds lightness and hue
    constant in the OkLCh color space while reducing chroma until the color is in gamut. Clipping is done at each step
    of the way and the color distance measured to see how close our color is to the intended color.

    The supported gamut mapping methods are:

    Name         | Input
    ------------ | -----
    Clipping     | `clip`
    OkLCh Chroma | `oklch-chroma`
    LCh Chroma   | `lch-chroma`

Parameters
: 
    Some methods could have additional parameters to configure the behavior, these would be done through `**kwargs`.
    None of built-in gamut mapping methods currently have additional parameters.

    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `space`    | `#!py3 None`       | The color space that the color must be mapped to. If space is `#!py3 None`, then the current color space will be used.
    `method`   | `#!py3 None`       | String that specifies which gamut mapping method to use. If `#!py3 None`, `oklch-chroma` will be used.

Return
: 
    Returns a reference to the current [`Color`](#color) after fitting its coordinates to the specified gamut.

## `Color.in_gamut` {#in_gamut}

```py3
def in_gamut(
    self,
    space=None,
    *,
    tolerance=util.DEF_FIT_TOLERANCE
):
```

Description
: 
    Checks if the current color is in the current or specified gamut.

Parameters
: 
    Parameters | Defaults         | Description
    ---------- | ---------------- | -----------
    `space`    | `#!py3 None`     | The color space that the color must be fit within. If space is `#!py3 None`, then the current color space will be used.
    `tolerance`| `#!py3 0.000075` | Tolerance allowed when checking bounds of color.

Return
: 
    Returns a boolean indicating whether the color is in the specified gamut.

## `Color.get` {#get}

```py3
def get(
    self,
    name
):
```

Description
: 
    Retrieves the coordinate value from the specified channel. Channel must be a channel name in the current color space
    or a channel name in the specified color space using the syntax: `space.channel`.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `name`     |                    | Channel name or color space and channel name to retrieve value from.

Return
: 
    Returns a numerical value that is stored internally for the specified channel, or a calculated value in the case
    that a channel in a different color space is requested.

## `Color.set` {#set}

```py3
def set(
    self,
    name,
    value
):
```

Description
: 
    Sets the given value to the specified channel. If the `name` is provided in the form `space.channel`, the value will
    be applied to the channel of the specified color space while keeping current color space the same.

    The `value` can be a numerical value, a CSS string compatible with the specified color space, or a function that
    accepts a numerical channel value and returns a numerical channel value.

    This function returns the current colors reference so that multiple sets can be chained together.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `name`     |                    | A string containing a channel name or color space and channel separated by a `.` specifying the what channel to set. If `value` is omitted, `name` can also be a dictionary containing multiple channels, each specifying their own value to set.
    `value`    |                    | A numerical value, a string value accepted by the specified color space, or a function.

Return
: 
    Returns a reference to the current [`Color`](#color) object.

## `Color.is_nan` {#is_nan}

```py3
def is_nan(
    self,
    name
):
```

Description
: 
    Retrieves the coordinate value from the specified channel and checks whether the value is `NaN`. Channel must be a
    channel name in the current color space or a channel name in the specified color space using the syntax:
    `space.channel`.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `name`     |                    | A string indicating what channel property to check.

Return
: 
    Returns a boolean indicating whether the specified color space's channel is `NaN`.

## `Color.white` {#white}

```py3
def white(
    self
):
```

Description
: 
    Retrieves the white point for the current color's color space.

Return
: 
    Returns a set of XYZ coordinates that align with the white point for the given color space.

## `Color.chromatic_adaptation`

```py3
@classmethod
def chromatic_adaptation(
    cls,
    w1,
    w2,
    xyz,
    *,
    method=None
):
```

Description
: 
    A class method that converts an XYZ set of coordinates between a two given white points. The first white point must
    match the white point of that the coordinates are currently using and the second white point must be the desired
    white point to use. `method` dictates the method of chromatic adaptation to use.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `w1`       |                    | Current white point of the XYZ coordinates.
    `w2`       |                    | Desired white point of the XYZ coordinates.
    `xyz`      |                    | The XYZ coordinates to adapt.
    `method`   | `#!py3 None`       | The method of chromatic adaptation to use. If not specified, the current class's default method will be used.

Return
: 
    Returns a set of XYZ coordinates that have been chromatically adapted to the desired white point.


## `Color.xy` {#xy}

```py3
def xy(
    self
):
```

Description
: 
    Retrieves the CIE 1931 (x, y) chromaticity coordinates for a given color.

Return
: 
    Returns a tuple of CIE 1931 (x, y) chromaticity points for the given color.

## `Color.uv` {#xy}

```py3
def uv(
    self,
    mode='1976'
):
```

Description
: 
    Retrieves the UCS 1960 (u, v) chromaticity coordinates for a given color or the CIE 1976 UCS (u', v') chromaticity
    coordinates, the latter being the default.

Parameters
: 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `mode`     | `#!py3 '1976'`     | A string indicating what mode to use. `1976` refers to the (u', v') points as described by CIE 1976 UCS and `1960` describes the (u, v) points as documented by CIE 1960 UCS.

Return
: 
    Returns a tuple of (u, v) -- either 1976 (u', v') or 1960 (u, v) -- chromaticity points for the given color.
