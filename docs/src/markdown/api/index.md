# Color API

## `#!py coloraide.NaN` {#nan}

/// define
Description

-   `NaN` is a convenience constant for `#!py float('nan')`.

Import path

-   `NaN` is imported from the `coloraide` library:

    ```py
    from coloraide import NaN
    ```
///

## `#!py coloraide.stop` {#stop}

```py
class stop:
    def __init__(
        self,
        color: ColorInput,
        value: float
    ) -> None:
        ...
```

/// define
Description

-   `stop` objects are used in [`interpolate`](#interpolate) methods. They allow a user to specify a color stop for a
    given color during the interpolation process.

Import Path

-  `stop` is imported from `coloraide` library:

    ```py
    from coloraide import stop
    ```

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, a dictionary describing the color, or another `Color` class object.
    `value`    |              | A numerical value specifying the new color stop for the given color.
///

## `#!py coloraide.hint` {#hint}

```py
def hint(
    mid: float,
) -> Callable[..., float]:
```

/// define
Description

-  `hint` returns an easing function that adjust the midpoint between two color stops.

Import Path

-  `hint` is imported from `coloraide` library:

    ```py
    from coloraide import hint
    ```

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `mid`      |              | A numerical value, relative to the two color stops it occurs between. The value will be used as the new midpoint.
///

## `#!py coloraide.Color` {#color}

```py
class Color:
    def __init__(
        self,
        color: ColorInput,
        data: VectorLike | None = None,
        alpha: float = util.DEF_ALPHA,
        **kwargs: Any
    ) -> None:
        ...
```

/// define
Description

-   The `Color` class object is a wrapper around the internal color space objects. `Color` is the base Color object and
    only registers a select number of color spaces by default. It provides an API interface to allow users to specify
    and manipulate colors.

Import path

-  `Color` is imported from the `coloraide` library:

    ```py
    from coloraide import Color
    ```

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, a dictionary describing the color, or another `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py None`  | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py 1`     | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
///

## `#!py coloraide.everything.ColorAll` {#colorall}

```py
class ColorAll(Color):
    def __init__(
        self,
        color: ColorInput,
        data: VectorLike | None = None,
        alpha: float = util.DEF_ALPHA,
        **kwargs: Any
    ) -> None:
        ...
```

/// define
Description

-   The `ColorAll` class object is derived from [`Color`](#color) and extends the registered color spaces to include all
    offered by ColorAide.

Import path

-  `ColorAll` is imported from the `coloraide` library:

    ```py
    from coloraide.everything import ColorAll
    ```

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, a dictionary describing the color, or another `ColorAll` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py None`  | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py 1`     | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
///

## `#!py Color.register` {#register}

```py
def register(
    cls,
    plugin: Plugin | Sequence[Plugin],
    *,
    overwrite: bool = False,
    silent: bool = False
) -> None:
    ...
```

/// define
Description

-   Register a plugin(s).

Parameters

- 
    Parameters  | Defaults      | Description
    ----------- | ------------- | -----------
    `plugin`    |               | A plugin instance or list of plugin instances to register.
    `overwrite` | `#!py False`  | `overwrite` will allow an already registered plugin to be overwritten if the plugin to register specifies a `name` that is already used for registration.
    `silent`    | `#!py False`  | `silent` will avoid throwing an error if the `name` is already found and `overwrite` is set to `#!py False` in the specified category.
///

## `#!py Color.deregister` {#deregister}

```py
@classmethod
def deregister(
    cls,
    plugin: str | Sequence[str], *,
    silent: bool = False
) -> None:
    ...
```

/// define
Description

-   Remove an already registered plugin(s).

Parameters

- 
    Parameters  | Defaults       | Description
    ----------- | -------------- | -----------
    `plugin`    |                | A string or list of strings that describe the plugin(s) to be removed. Strings should be in the format `category:name` where `category` is either `space`, `delta-e`, `cat`, `filter`, `contrast`, `interpolate`, or `fit` and `name` is the name the plugin was registered under. `*` will remove all plugins and `category:*` will remove all within a specific category.
    `silent`     | `#!py False`  | `silent` will avoid throwing an error if the `name` can not be found in the specified category.
///

## `#!py Color.match` {#match}

```py
@classmethod
def match(
    cls,
    string: str,
    start: int = 0,
    fullmatch: bool = False
) -> ColorMatch | None:
    ...
```

/// define
Description

-   The `match` class method provides access to the color matching interface and allows a user to provide a color string
    and get back a `ColorMatch` object. `ColorMatch` objects contain three properties:

    ```py
    class ColorMatch:
        def __init__(
            self,
            color: Color,
            start: int,
            end: int
        ) -> None:
            ...
    ```

    Parameter | Description
    --------- | -----------
    `color`   | The `Color` object.
    `start`   | The starting point within the string buffer where the color was found.
    `end`     | The ending point within the string buffer where the color was found.

    Match does not search the entire buffer, but simply matches at the location specified by `start`.

Parameters

- 
    Parameters  | Defaults      | Description
    ----------- | ------------- | -----------
    `string`    |               | A string representing the color.
    `start`     | `#!py 0`      | Accepts an integer offset into the provided string buffer to start the match.
    `fullmatch` | `#!py False`  | A boolean which defines whether match must match to the end of the string buffer.

Return

-   Returns a `ColorMatch` object.
///

## `#!py Color.new` {#new}

```py
def new(
    self,
    color: ColorInput,
    data: VectorLike | None = None,
    alpha: float = util.DEF_ALPHA,
    **kwargs: Any
) -> Color:
    ...
```

/// define
Description

-   The `new` class method exposes the interface of creating new color objects. Using `new` is the same as using
    [`Color()`](#color).

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py None`  | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py 1`     | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.

Return

-   Returns a [`Color`](#color) object.
///

## `#!py Color.random` {#random}

```py
@classmethod
def random(
    cls,
    space: str,
    *,
    limits: Sequence[Sequence[float] | None] | None = None
) -> Color:
    ...
```

/// define
Description

-   Generate a random color in the provided `space`. The color space's channel range will be used as a limit for the
    channel. For color spaces with no clearly defined gamut, these values can be arbitrary. In such cases, it may be
    advisable to fit the returned color space to a displayable gamut.

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `space`    |              | The color space name in which to generate a random color in.
    `limits`   | `#!py None`  | An optional list of constraints for various color channels. Each entry should either be a sequence contain a minimum and maximum value, or should be `#!py  None`. `#!py None` values will be ignored and the color space's specified channel range will be used instead. Any missing entries will be treated as `#!py None`.

Return

-   Returns a [`Color`](#color) object.
///

## `#!py Color.clone` {#clone}

```py
def clone(
    self
):
```

/// define
Description

-   The `clone` method provides a way to create a duplicate of the current `Color` instance.

Return

-   Returns a [`Color`](#color) object.
///


## `#!py Color.update` {#update}

```py
def update(
    self,
    color: ColorInput,
    data: VectorLike | None = None,
    alpha: float = util.DEF_ALPHA,
    *,
    norm: bool = True,
    **kwargs: Any
) -> Color:
    ...
```

/// define
Description

-   The `update` method provides a way to update the underlying color space with coordinates from any color space. The
    method's signature is the same as [`new`](#new) except that it adds an additional `norm` parameter used to skip
    achromatic hue normalization when converting to the current color space. The object itself will assume the
    equivalent color in the current color space that matches the input color's value (assuming no algorithmic
    limitations preventing an equivalent color).

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py None`  | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py 1`     | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.
    `norm`     | `#!py True`  | When set to `#!py False`, this prevents achromatic normalization when updating from a different color space. If no update occurs, nothing is done.

Return

-   Returns a reference to the current `Color` object.
///

## `#!py Color.mutate` {#mutate}


```py
def mutate(
    self,
    color: ColorInput,
    data: VectorLike | None = None,
    alpha: float = util.DEF_ALPHA,
    **kwargs: Any
) -> Color:
    ...
```

/// define
Description

-   The `mutate` method is similar to [`update`](#update) except that it does not convert the input color to the current
    color space, but instead replaces the current color space and values with the input color's color space and values.

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string, or other `Color` class object. If given `data`, a string must be used and should represent the color space to use.
    `data`     | `#!py None`  | `data` accepts a list of numbers representing the coordinates of the color. If provided, `color` must be a string specifying the color space.
    `alpha`    | `#!py 1`     | `alpha` accepts a number specifying the `alpha` channel. Must be used in conjunction with `data` or it will be ignored.

Return

-   Returns a reference to the current [`Color`](#color) object.
///

## `#!py Color.convert` {#convert}

```py
def convert(
    self,
    space: str,
    *,
    fit: bool | str = False,
    in_place: bool = False,
    norm: bool = True
) -> Color:
    ...
```

/// define
Description

-   Converts a [`Color`](#color) object from one color space to another. If the current color space matches the
    specified color space, a clone of the current color will be returned with no changes to the channel values. If
    `in_place` is `#!py True`, the current object will be modified in place.

Parameters

- 
    Parameters | Defaults      | Description
    ---------- | ------------- | -----------
    `space`    |               | A string representing the desired final color space.
    `fit`      | `#!py False`  | Parameter specifying whether the current color should be gamut mapped into the final, desired color space. If set to `#!py3 True`, the color will be gamut mapped using the default gamut mapping method. If set to a string, the string will be interpreted as the name of the gamut mapping method to be used.
    `in_place` | `#!py False`  | Boolean specifying whether the convert should alter the current [`Color`](#color) object or return a new one.
    `norm`     | `#!py True`   | When set to `#!py False`, this prevents achromatic normalization when converting from a different color space. If no update occurs, nothing is done.

Return

-   Returns a reference to the converted [`Color`](#color) object. If `in_place` is `True`, the return will be a
    reference to the current [`Color`](#color) object.
///

## `#!py Color.space` {#space}

```py
def space(
    self
) -> str:
    ...
```

/// define
Description

-   Retrieves the current color space name as specified by the underlying color space object.

Return

-   Returns a string with the name of the current color space.
///

## `#!py Color.normalize` {#normalize}

```py
def normalize(
    self,
    *,
    nans: bool = True
) -> Color:
    ...
```

/// define
Description

-   Force normalization of a color's channels by cleaning up channels that setting hue to undefined if the color is
    achromatic. if `nans` is set to `#!py False`, the hue normalization step (setting hue to undefined) will be skipped.
    Normalize modifies the current color in place.

Parameters

- 
    Parameters | Defaults      | Description
    ---------- | ------------- | -----------
    `nans`    | `#!py True`    | Perform hue normalization (setting hue to undefined if the color is achromatic).

Return

-   Returns a reference to the current [`Color`](#color) object after normalizing the channels for undefined hues.
///

## `#!py Color.to_dict` {#to_dict}

```py
def to_dict(
    self,
    *,
    nans: bool = True
) -> Mapping[str, Any]:
    ...
```

/// define
Description

-   Dump the color object to a simple dictionary.

    ```py
    {
        'space': 'srgb',            # Color space name
        'coords': [1.0, 0.0, 0.0],  # Color channel values
        'alpha': 1.0                # Alpha channel value
    }
    ```

Parameters

- 
    Parameters | Defaults      | Description
    ---------- | ------------- | -----------
    `nans`     | `#!py True`   | Return channel values having undefined values resolved as defined values.

Return

-   A dictionary containing the color space name and channel values.
///

## `#!py Color.to_string` {#to_string}

```py
def to_string(
    self,
    **kwargs: Any
) -> str:
    ...
```

/// define
Description

-   Method that converts the current color to an output format supported by the color space. While a number of the
    parameters are common, some may be specific to the color space. The [usage guide](../strings.md#) covers color space
    specific options in more details.

Parameters

-   Common parameters:

    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `alpha`    | `#!py None`  | Boolean or `#!py3 None` value which determines whether the output includes `alpha`. If `#!py3 None`, the default alpha will only be shown if less than 1. If `#!py3 True`, alpha will always be shown. If `#!py3 False`, alpha will be omitted.
    `precision`| `#!py 5`     | Integer value that sets precision and scale. Precision and scale will match the value if greater than zero. If `0`, values will be rounded to the nearest integer. If `-1`, number will be output at the highest precision.
    `fit`      | `#!py True`  | A boolean that controls whether gamut mapping is performed on string creation. By default, colors will be fit to their own color space. This can be disabled by setting to `#!py3 False`.
    `color`    | `#!py False` | A boolean that will determine if the `color(space coord+ / alpha)` format is used for string output. Has highest precedence.
    `percent`  | Varies       | A boolean that will output color channels as percents. Not all color spaces support percents, or may support percents only in certain scenarios. Default value may be determined by the color space.

    sRGB specific parameters:

    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `hex`.     | `#!py False` | String output will be in `#RRGGBBAA` format.
    `names`    | `#!py False` | Boolean indicating a preference for CSS color names. When translating a color to it's closest hex form, if that hex value matches a CSS color name, that color name will be returned as the output. `hex` does not have to be `#!py3 True` for this to apply.
    `compress` | `#!py False` | If `hex` is `#!py3 True` and `compress` is `#!py3 True`, hex values will be compressed if possible: `#RRGGBBAA` --> `#RGBA`.

    Space dependent parameters:

    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `comma`    | `#!py False` | If supported by the color space and the current output format, commas will be used instead of space format: `rgba(0, 0, 0, 1)` --> `rgb(0 0 0 /1)`.

Return

-   Returns a string representation of the current color.
///

## `#!py Color.luminance` {#luminance}

```py
def luminance(
    self,
    *,
    white: VectorLike | None = cat.WHITES['2deg']['D65']

) -> float:
    ...
```

/// define
Description

-   Get the relative luminance. Relative luminance is obtained from the Y coordinate in the XYZ color space. XYZ, in
    this case, has a D65 white point.

Parameters

- 
    Parameters  | Defaults           | Description
    ----------- | ------------------ | -----------
    `white`     | `#!py None`        | Specify the white in which to chromatically adapt the points from, if none is specified, the current color's white point is assumed.

Return

-   Returns an float indicating the relative luminance.
///

## `#!py Color.contrast`

```py
def contrast(
    self,
    color: ColorInput,
    method: str | None = None
) -> float:
    ...
```

/// define
Description

-   Get the contrast ratio based on the relative luminance between two colors.

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | -------------| -----------
    `color`    |              | A color string or [`Color`](#color) object representing a color.
    `method`   | `#!py None`  | Specify the method used to obtain the contrast value. If `#!py None`, the default specified by the class will be used.

Return

-   Returns a float indicating the contrast ratio between two colors.
///

## `#!py Color.distance` {#distance}

```py
def distance(
    self,
    color: ColorInput,
    *,
    space: str = "lab"
) -> float:
    ...
```

/// define
Description

-   Performs a euclidean distance algorithm on two colors.

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `color`    |              | A color string or [`Color`](#color) object representing a color.
    `space`    | `#!py3 "lab"`| Color space to perform distancing algorithm in.

Return

-   Returns a float indicating euclidean distance between the two colors.
///

## `#!py Color.delta_e` {#delta_e}

```py
def delta_e(
    self,
    color: ColorInput,
    *,
    method: str | None = None,
    **kwargs: Any
) -> float:
    ...
```

/// define
Description

-   Performs a delta E distance algorithm on two colors. Default algorithm that is used is Delta E 1976 (`76`). Some
    methods have additional weighting that can be configured through method specific options which are represented by
    `**kwargs`.

    Available methods:

    Name                                     | Input           | Parameters
    ---------------------------------------- | --------------- | --------------------
    [∆E^\*^~ab~][de76]\ (CIE76)              | `76`            |
    [∆E^\*^~cmc~][decmc]\ (CMC\ l:c\ (1984)) | `cmc`           | `l=2, c=1`
    [∆E^\*^~94~][de94]\ (CIE94)              | `94`            | `kl=1, k1=0.045, k2=0.015`
    [∆E^\*^~00~ ][de2000]\ (CIEDE2000)       | `2000`          | `kl=1, kc=1, kh=1`
    [∆E~HyAB~][dehyab]\ (HyAB)               | `hyab`          | `space="lab"`
    ∆E~ok~                                   | `ok`            | `scalar=1`
    [∆E~itp~][deitp]\ (ICtCp)                | `itp`           | `scalar=720`
    [∆E~z~][dez]\ (Jzazbz)                   | `jz`            |
    [∆E~99o~][de99o]\ (DIN99o)               | `99o`           |
    ∆E~cam16~                                | `cam16`         | `model=ucs`
    ∆E~HCT~                                  | `hct`           |

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `color`    |              | A color string or [`Color`](#color) object representing a color.
    `method`   | `#!py None`  | String that specifies the method to use. If `#!py3 None`, the default will be used.
    `**kwargs` |              | Any distancing specific parameters to pass to ∆E method.

Return

-   Returns a float indicating the delta E distance between the two colors.
///

## `#!py Color.closest` {#closest}

```py
def closest(
    self,
    colors: Sequence[ColorInput],
    *,
    method: str | None = None,
    **kwargs: Any
) -> Color:
    ...
```

/// define
Description

-   Given a list of colors, calculates the closest color to the calling color object.

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `colors`   |              | A list of color strings, [`Color`](#color) object, or dictionary representing a color.
    `method`   | `#!py None`  | String that specifies the method of color distancing to use.
    `**kwargs` |              | Any distancing specific parameters to pass to ∆E method.

Return

-   The [`Color`](#color) that is closest to the calling color object. In the off chance that an empty list is passed in
    `#!py3 None` will be returned.
///

## `#!py Color.mask` {#mask}

```py
def mask(
    self,
    channel: str | Sequence[str],
    *,
    invert: bool = False,
    in_place: bool = False
) -> Color:
    ...
```

/// define
Description

-   The `mask` method will set any and all specified channels to `NaN`. If `invert` is set to `#!py True`, `mask` will
    set any and all channels not specified to `NaN`.

Parameters

- 
    Parameters  | Defaults      | Description
    ----------- | ------------- | -----------
    `channel`   |               | A string specifying a channel, or a list of strings specifying multiple channels. Specified channels will be masked (or the only channels not masked if `invert` is `#!py3 True`).
    `invert`    | `#!py False`  | Use inverse masking logic and mask all channels that are not specified.
    `in_place`  | `#!py False`  | Boolean used to determine if the current color should be modified "in place" or a new [`Color`](#color) object should be returned.

Return

-   Returns a reference to the masked [`Color`](#color) object. If `in_place` is `True`, the return will be a
    reference to the current [`Color`](#color) object.
///

## `#!py Color.interpolate` {#interpolate}

```py
@classmethod
def interpolate(
    cls,
    colors: Sequence[ColorInput | interpolate.stop | Callable[..., float]],
    *,
    space: str | None = None,
    out_space: str | None = None,
    progress: Mapping[str, Callable[..., float]] | Callable[..., float] | None = None,
    hue: str = util.DEF_HUE_ADJ,
    premultiplied: bool = True,
    extrapolate: bool = False,
    domain: list[float] | None = None,
    method: str = "linear",
    **kwargs: Any
) -> Interpolator:
    ...
```

/// define
Description

-   The `interpolate` method creates a function that takes a value between 0 - 1 and interpolates a new color based on
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
    `longer`        | Angles are adjusted so that θ₂ - θ₁ ∈ {[-360, -180], [180, 360]}.
    `increasing`    | Angles are adjusted so that θ₂ - θ₁ ∈ [0, 360].
    `decreasing`    | Angles are adjusted so that θ₂ - θ₁ ∈ [-360, 0]
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

- 
    Parameters      | Defaults          | Description
    --------------- | ----------------- | -----------
    `colors`        |                   | A list of color strings, [`Color`](#color) objects, dictionaries representing a color, [`stop`](#piecewise) objects, or easing functions.
    `space`         | `#!py "lab"`      | Color space to interpolate in.
    `out_space`     | `#!py None`       | Color space that the new color should be in. If `#!py None`, the return color will be in the same color space as specified by `space`.
    `progress`      | `#!py None`       | An optional function that that allows for custom logic to perform non-linear interpolation.
    `hue`           | `#!py "shorter"`  | Define how color spaces which have hue angles are interpolated. Default evaluates between the shortest angle.
    `premultiplied` | `#!py True`       | Use premultiplied alpha when interpolating.
    `extrapolate`   | `#!py False`      | Interpolations should extrapolate when values exceed the domain range ([0, 1] by default).
    `domain`        | `#!py None`       | A list of numbers defining the domain range of the interpolation.
    `method`        | `#!py "linear"`   | The interpolation method to use.

Return

-   Returns a function that takes a range within the specified domain, the default being `[0..1]`. The function returns
    a new, interpolated [`Color`](#color) object.
///

## `#!py Color.steps` {#steps}

```py
@classmethod
def steps(
    cls,
    colors: Sequence[ColorInput | interpolate.stop | Callable[..., float]],
    *,
    steps: int = 2,
    max_steps: int = 1000,
    max_delta_e: float = 0,
    delta_e: str | None = None,
    **interpolate_args: Any
) -> list[Color]:
    ...
```

/// define
Description

-   Creates an `interpolate` function and iterates through it with user defined step parameters to produce discrete
    color steps. Will attempt to provide the minimum number of `steps` without exceeding `max_steps`. If `max_delta_e`
    is provided, the distance between each stop will be cut in half until there are no colors with a distance greater
    than the specified `max_delta_e`. The default ∆E method is used by default, but it can be changed with the `delta_e`
    parameter.

    If more than one color is provided, the steps will be returned from the interpolations between all the provided
    colors.

    Like [`interpolate`](#interpolate), the default interpolation space is `lab`.

Parameters

- 
    Parameters                 | Defaults                           | Description
    -------------------------- | ---------------------------------- | -----------
    `color`                    |                                    | A list of color strings, [`Color`](#color) objects, dictionaries representing a color, [`stop`](#piecewise) objects, or easing functions.
    `steps`                    | `#!py 2`                           | Minimum number of steps.
    `max_steps`                | `#!py 1000`                        | Maximum number of steps.
    `max_delta_e`              | `#!py 0`                           | Maximum delta E distance between the color stops. A value of `0` or less will be ignored.
    `delta_e`                  | `#!py None`                        | A string indicating which [∆E method](../distance.md#delta-e) to use. If nothing is supplied, the class object's current default ∆E method will be used.
    `#!py **interpolate_args`  | See\ [`interpolate`](#interpolate) | Keyword arguments defined in [`interpolate`](#interpolate).

Return

-   List of [`Color`](#color) objects.
///

## `#!py Color.discrete` {#discrete}

```py
@classmethod
def discrete(
    cls,
    colors: Sequence[ColorInput | interpolate.stop | Callable[..., float]],
    *,
    space: str | None = None,
    out_space: str | None = None,
    steps: int | None = None,
    domain: list[float] | None = None,
    **interpolate_steps_args: Any
) -> Interpolator:
    ...
```

/// define
Description

-   Generates an `interpolate` function with discrete color scale. By default it assumes as many discrete colors as the
    user inputs, but `steps` can be used to generate more or less using the input colors. As `discrete` is built on
    [`steps`](#steps), it takes all the same arguments.

    Like [`interpolate`](#interpolate), the default interpolation space is `lab`.

Parameters

- 
    Parameters                       | Defaults               | Description
    -------------------------------- | ---------------------- | -----------
    `color`                          |                        | A list of color strings, [`Color`](#color) objects, dictionaries representing a color, [`stop`](#piecewise) objects, or easing functions.
    `space`                          | `#!py "lab"`           | Color space to interpolate in.
    `out_space`                      | `#!py None`            | Color space that the new color should be in. If `#!py None`, the return color will be in the same color space as specified by `space`.
    `steps`                          | `#!py None`            | Minimum number of steps. If `None` the `steps` is assumed as the number of input colors.
    `#!py **interpolate_steps_args`  | See\ [`steps`](#steps) | Keyword arguments defined in [`interpolate`](#interpolate).

Return

-   Returns a function that takes a range within the specified domain, the default being `[0..1]`. The function returns
    a new, interpolated [`Color`](#color) object.
///

## `#!py Color.mix` {#mix}

```py
def mix(
    self,
    color: ColorInput,
    percent: float = util.DEF_MIX,
    *,
    in_place: bool = False,
    **interpolate_args: Any
) -> Color:
    ...
```

/// define
Description

-   Interpolates between two colors returning a color that represents the mixing of the base color and the provided
    `color` mixed at the provided `percent`, where `percent` applies to how much the provided `color` contributes to the
    the final result.

Parameters

- 
    Parameters                 | Defaults                           | Description
    -------------------------- | ---------------------------------- | -----------
    `color`                    |                                    | A color string, [`Color`](#color) object, and/or dictionary representing a color.
    `percent`                  | `#!py 0.5`                         | A numerical value between 0 - 1 representing the percentage at which the parameter `color` will be mixed.
    `in_place`                 | `#!py False`                       | Boolean used to determine if the the current color should be modified "in place" or a new [`Color`](#color) object should be returned.
    `#!py **interpolate_args`  | See\ [`interpolate`](#interpolate) | Keyword arguments defined in [`interpolate`](#interpolate).

Return

-   Returns a reference to the new [`Color`](#color) object or a reference to the current [`Color`](#color) if
    `in_place` is `#!py3 True`.
///

## `#!py3 Color.average` {#average}

```py
@classmethod
def average(
    cls,
    colors: Iterable[ColorInput],
    *,
    space: str | None = None,
    out_space: str | None = None,
    premultiplied: bool = True,
    **kwargs: Any
) -> Color:
```

/// define
Description

-   Get the average mean of all channels given a particular set of input colors.

Parameters

- 
    Parameters       | Defaults    | Description
    ---------------- | ------------| -----------
    `colors`         |             | An iterable of color strings, [`Color`](#color) objects, and/or dictionaries representing a color.
    `space`          | `#!py None` | An optional string to specify what color space the colors should be averaged in. If none is provided, Oklab is assumed.
    `out_space`      | `#!py None` | Color space that the new color should be in. If `#!py None`, the return color will be in the same color space as specified via `space`.
    `premultiplied`  | `#!py True` | Specify whether colors should be premultiplied during the averaging process.

Return

-   Returns a reference to the new [`Color`](#color) object representing the average of the input colors.

///

## `#!py Color.filter` {#cvd}

```py
def filter(
    self,
    name: str,
    amount: float | None = None,
    *,
    space: str | None = None,
    in_place: bool = False,
    out_space: str | None = None,
    **kwargs: Any
) -> Color:
    ...
```

/// define
Description

-   Apply a color filter to alter a given color. The non-CVD filters are based on the W3C [Filter Effects][filter-effects]
    and behave in the same manner. Colors are evaluated in the sRGB Linear color space unless otherwise specified via
    the `space` parameter. No other color space will be accepted except sRGB and sRGB Linear.

    An `amount` can be provided to adjust how much the color is filtered. Any clamping that occurs with the `amount`
    parameter, and related ways in which `amount` are applied, follow the W3C [Filter Effects][filter-effects] spec.

    Some filters, such as CVDs, may take additional arguments via `kwargs`.

    Filters           | Name         | Default
    ----------------- | ------------ | -------
    Brightness        | `brightness` | `#!py 1`
    Saturation        | `saturate`   | `#!py 1`
    Contrast          | `contrast`   | `#!py 1`
    Opacity           | `opacity`    | `#!py 1`
    Invert            | `invert`     | `#!py 1`
    Hue\ rotation     | `hue-rotate` | `#!py 0`
    Sepia             | `sepia`      | `#!py 1`
    Grayscale         | `grayscale`  | `#!py 1`

    CVD\ Filters      | Name         | Default
    ----------------- | ------------ | -------
    Protanopia\ CVD   | `protan`     | `#!py 1`
    Deuteranopia\ CVD | `deutan`     | `#!py 1`
    Tritanopia\ CVD   | `tritan`     | `#!py 1`

Parameters

- 
    Parameters  | Defaults       | Description
    ----------- | ---------------| -----------
    `name`      |                | The name of the filter that should be applied.
    `amount`    | See\ above     | A numerical value adjusting to what degree the filter is applied. Input range can vary depending on the filter being used. Default can also dependent on the filter being used.
    `space`     | `#!py3 None`   | Controls the algorithm used for simulating the given CVD.
    `in_place`  | `#!py3 False`  | Boolean used to determine if the the current color should be modified "in place" or a new [`Color`](#color) object should be returned. 
    `out_space` | `#!py None`    | Color space that the new color should be in. If `#!py None`, the return color will be in the same color space as specified via `space`.
    `**kwargs`  |                | Additional filter specific parameters.

    CVDs also take an optional `method` parameter that allows for specifying the CVD algorithm to use.

    Simulation\ Approach             | Name
    -------------------------------- | ----
    Brettel 1997                     | `brettel`
    Viénot, Brettel, and Mollon 1999 | `vienot`
    Machado 2009                     | `machado`

Return

-   Returns a reference to the new [`Color`](#color) object or a reference to the current [`Color`](#color) if
    `in_place` is `#!py3 True`.
///

## `#!py Color.harmony` {#harmony}

```py
def harmony(
    self,
    name: str,
    *,
    space: str | None = None,
    out_space: str | None = None
) -> list[Color]:
    ...
```

/// define
Description

-   The `harmony` method uses the current color and returns a set of harmonious colors (including the current color).
    The color harmonies are based on the classical color harmonies of color theory. By default, harmonious colors are
    selected under the perceptually uniform OkLCh color space, but other cylindrical color spaces can be used.

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

- 
    Parameters  | Defaults       | Description
    ----------- | ---------------| -----------
    `name`      |                | Name of the color harmony to use.
    `space`     | `#!py 'oklch'` | Color space under which the harmonies will be calculated. Must be a cylindrical space.
    `out_space` | `#!py None`    | Color space that the new color should be in. If `#!py None`, the return color will be in the same color space as specified via `space`.

Return

-   Returns a list of [`Color`](#color) objects.
///

## `#!py Color.compose` {#compose}

```py
def compose(
    self,
    backdrop: ColorInput | Sequence[ColorInput],
    *,
    blend: str | bool = True,
    operator: str | bool = True,
    space: str | None = None,
    out_space: str | None = None,
    in_place: bool = False
) -> Color:
    ...
```

/// define
Description

-   Apply compositing which consists of a [blend mode](../compositing.md#blend-modes) and a [Porter Duff operator](../compositing.md#compositing-operators)
    for alpha compositing. The current color is treated as the source (top layer) and the provided color as the backdrop
    (bottom layer). Colors will be composited in the `srgb` color space unless otherwise specified.

    Colors should generally be RGB-ish colors (sRGB, Display P3, A98 RGB, etc.). The algorithm is designed only for
    RGB-ish colors. Non-RGB-ish colors are likely to provide nonsense results.

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

- 
    Parameters  | Defaults       | Description
    ----------- | -------------- | -----------
    `backdrop`  |                | A background color represented with either a string or [`Color`](#color) object.
    `blend`     | `#!py3 None`   | A blend mode to use to use when compositing. Values should be a string specifying the name of the blend mode to use. If `#!py None`, [`normal`](#normal) will be used. If `#!py False`, blending will be skipped.
    `operator`  | `#!py3 None`   | A Porter Duff operator to use for alpha compositing. Values should be a string specifying the name of the operator to use. If `#!py None`, [`source-over`](#source-over) will be used. If `#!py False`, alpha compositing will be skipped.
    `space`     | `#!py3 None`   | A color space to perform the overlay in. If `#!py None`, the base color's space will be used.
    `out_space` | `#!py None`    | Color space that the new color should be in. If `#!py None`, the return color will be in the same color space as specified by `space`.
    `in_place`  | `#!py3 False`  | Boolean used to determine if the the current color should be modified "in place" or a new [`Color`](#color) object should be returned.

Return

-   Returns a reference to the new [`Color`](#color) object or a reference to the current [`Color`](#color) if
    `in_place` is `#!py3 True`.
///

## `#!py Color.clip` {#clip}

```py
def clip(
    self,
    space: str | None = None
) -> Color:
```

/// define
Description

-   Performs simple clipping on color channels that are out of gamut.

Parameters

- 
    Parameters | Defaults      | Description
    ---------- | ------------- | -----------
    `space`    | `#!py None`   | The color space that the color must be mapped to. If space is `#!py None`, then the current color space will be used.

Return

-   Returns a reference to the current [`Color`](#color) after fitting its coordinates to the specified gamut.
///

## `#!py Color.fit` {#fit}

```py
def fit(
    self,
    space: str | None = None,
    *,
    method: str | None = None,
    **kwargs: Any
) -> Color:
    ...
```

/// define
Description

-   Fits color to the current or specified color gamut.

    By default, `lch-chroma` gamut mapping is used. This is essentially an approach that holds lightness and hue
    constant in the CIELCh color space while reducing chroma until the color is in gamut. Clipping is done at each step
    of the way and the color distance measured to see how close our color is to the intended color.

    The supported gamut mapping methods are:

    Name         | Input
    ------------ | -----
    Clipping     | `clip`
    OkLCh Chroma | `oklch-chroma`
    LCh Chroma   | `lch-chroma`

Parameters

- 
    Some methods could have additional parameters to configure the behavior, these would be done through `**kwargs`.
    None of built-in gamut mapping methods currently have additional parameters.

    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `space`    | `#!py None`        | The color space that the color must be mapped to. If space is `#!py None`, then the current color space will be used.
    `method`   | `#!py None`        | String that specifies which gamut mapping method to use. If `#!py None`, `lch-chroma` will be used.

Return

-   Returns a reference to the current [`Color`](#color) after fitting its coordinates to the specified gamut.
///

## `#!py Color.in_gamut` {#in_gamut}

```py
def in_gamut(
    self, space: str | None = None,
    *,
    tolerance: float = util.DEF_FIT_TOLERANCE
) -> bool:
```

/// define
Description

-   Checks if the current color is in the current or specified gamut.

Parameters

- 
    Parameters | Defaults         | Description
    ---------- | ---------------- | -----------
    `space`    | `#!py None`      | The color space that the color must be fit within. If space is `#!py None`, then the current color space will be used.
    `tolerance`| `#!py 0.000075`  | Tolerance allowed when checking bounds of color.

Return

-   Returns a boolean indicating whether the color is in the specified gamut.
///

## `#!py Color.get` {#get}

```py
def get(
    self,
    name: str | list[str] | tuple[str, ...],
    *,
    nans: bool = True
) -> float | list[float]:
```

/// define
Description

-   Retrieves the coordinate value from the specified channel or values from a sequence of specified channels. Channels
    must be a channel name in the current color space or a channel name in the specified color space using the syntax:
    `space.channel`.

Parameters

- 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `name`     |                    | Channel name or sequence of channel names. Channel names can define the color space and channel name to retrieve value from a different color space.
    `nans`     | `#!py True`        | Determines whether an undefined value is allowed to be returned. If disabled, undefined values will be resolved before returning.
Return

-   Returns a numerical value that is stored internally for the specified channel, or a calculated value in the case
    that a channel in a different color space is requested. If more than one value is requested, the a list of numerical
    values will be returned.
///

## `#!py Color.set` {#set}

```py
def set(
    self,
    name: str | dict[str, float | Callable[..., float]],
    value: float | Callable[..., float] | None = None,
    *,
    nans: bool = True
) -> Color:
```

/// define
Description

-   Sets the given value to the specified channel. If the `name` is provided in the form `space.channel`, the value will
    be applied to the channel of the specified color space while keeping current color space the same.

    The `value` can be a numerical value or a function that accepts a numerical channel value and returns a numerical
    channel value.


    `name` can also be a dictionary of channels, each with a `value`. In this case, the `value` parameter of the
    function can be ignored.

    This function returns the current colors reference so that multiple sets can be chained together.

Parameters

- 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `name`     |                    | A string containing a channel name or color space and channel separated by a `.` specifying the what channel to set. If `value` is omitted, `name` can also be a dictionary containing multiple channels, each specifying their own value to set.
    `value`    |                    | A numerical value, a string value accepted by the specified color space, or a function.
    `nans`     | `#!py True`        | When doing relative sets via a callback input, ensure the channel value passed to the callback is a real number, not an undefined value.

Return

-   Returns a reference to the current [`Color`](#color) object.
///

## `#!py Color.coords` {#coords}

```py
def coords(
    self,
    *,
    nans: bool = True
) -> Vector:
    ...
```

/// define
Description

-   Get the color channels (no alpha). If `nans` is set to `#!py False`, all undefined values will be returned as
    defined.

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `nans`     | `#!py True`  | If `nans` is set to `#!py False`, all undefined values will be returned as defined.

Return

-   Returns a list of `#!py float` values, one for each color channel.

///

## `#!py Color.alpha` {#coords}

```py
def alpha(
    self,
    *,
    nans: bool = True
) -> float:
    ...
```

/// define
Description

-   Get the alpha channel's value. If `nans` is set to `#!py False`, an undefined value will be returned as defined.

Parameters

- 
    Parameters | Defaults     | Description
    ---------- | ------------ | -----------
    `nans`    | `#!py True`  | If `nans` is set to `#!py False`, an undefined value will be returned as defined.

Return

-   Returns a `#!py float`.
///

## `#!py Color.is_achromatic` {#is_achromatic}

```py
def is_achromatic(
    self
) -> bool:
    ...
```

/// define
Description

-   Can be called on any color to determine if the color is achromatic. If a color is achromatic, or very close to
    achromatic, it will return `#!py True`.

Return

-   Returns a boolean indicating whether the color is achromatic.
///

## `#!py Color.is_nan` {#is_nan}

```py
def is_nan(
    self,
    name: str
) -> bool:
    ...
```

/// define
Description

-   Retrieves the coordinate value from the specified channel and checks whether the value is undefined (set to NaN).
    Channel must be a channel name in the current color space or a channel name in the specified color space using the
    syntax: `space.channel`.

Parameters

- 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `name`     |                    | A string indicating what channel property to check.

Return

-   Returns a boolean indicating whether the specified color space's channel is `NaN`.
///

## `#!py Color.white` {#white}

```py
def white(
    self
) -> Vector:
    ...
```

/// define
Description

-   Retrieves the white point for the current color's color space.

Return

-   Returns a set of XYZ coordinates that align with the white point for the given color space.
///

## `#!py Color.blackbody` {#blackbocy}

```py
@classmethod
def blackbody(
    cls,
    temp: float,
    duv: float = 0.0,
    *,
    scale: bool = True,
    scale_space: str | None = None,
    out_space: str | None = None,
    method: str | None = None,
    **kwargs: Any
) -> Color:
```

/// define
Description

-   Creates a color from a temperature in Kelvin and an optional ∆~uv~. The color will be scaled within the linear RGB
    space specified by `scale_space` and can be disabled by setting `scale` to `#!py False`. By default, the
    Ohno 2013 algorithm is used and can be configured via `method`.

Parameters

- 
    Parameters      | Defaults             | Description
    --------------- | -------------------- | -----------
    `temp`          |                      | A positive temperature in Kelvin. Accepted range of temperature is based on the algorithm.
    `duv`           | `#!py 0.0`           | An optional ∆~uv~ specifying the distance from the black body curve.
    `scale`         | `#!py True`          | Scale the color with a linear RGB color space as defined by `scale_space`.
    `scale_space`   | `#!py 'srgb-linear'` | If `scale` is enabled, `scale_space` defines the RGB color space in which the returned color should be scaled within. The color space should be a linear space for best results. If undefined, `srgb-linear` will be used.
    `out_space`     | `#!py None`          | Color space that the new color should be in. If `#!py None`, the return color will be in the same color space as specified by `space` or `xyz-d65` if `space` is `#!py None`.
    `method`        | `#!py None`          | A string specifying the algorithm to use. By default `robertson-1968` is used.
    `**kwargs`      |                      | Any plugin specific parameters to pass to the `blackbody` method.

Return

-   Returns a reference to the current [`Color`](#color).
///

## `#!py Color.cct` {#cct}

```py
def cct(
    self,
    *,
    method: str | None = None,
    **kwargs: Any
) -> Vector:
```

/// define
Description

-   Returns the associated CCT and ∆~uv~ for a given color. If the color is beyond an acceptable range for the
    algorithm or the color is very far from the locus, the result may be surprising.

Parameters

- 
    Parameters  | Defaults             | Description
    ----------- | -------------------- | -----------
    `method`    | `#!py None`          | A string specifying the algorithm to use. By default `robertson-1968` is used.
    `**kwargs`  |                      | Any plugin specific parameters to pass to the `blackbody` method.

Return

-   Returns a list containing the correlated color temperature in Kelvin and the ∆~uv~.
///

## `#!py Color.chromatic_adaptation`

```py
@classmethod
def chromatic_adaptation(
    cls,
    w1: tuple[float, float],
    w2: tuple[float, float],
    xyz: VectorLike,
    *,
    method: str | None = None
) -> Vector:
    ...
```

/// define
Description

-   A class method that converts an XYZ set of coordinates between two given white points. The first white point must
    match the white point of the current coordinates and the second white point must be the desired white point to use.
    `method` dictates the method of chromatic adaptation to use.

Parameters

- 
    Parameters | Defaults           | Description
    ---------- | ------------------ | -----------
    `w1`       |                    | Current white point of the XYZ coordinates.
    `w2`       |                    | Desired white point of the XYZ coordinates.
    `xyz`      |                    | The XYZ coordinates to adapt.
    `method`   | `#!py3 None`       | The method of chromatic adaptation to use. If not specified, the current class's default method will be used.

Return

-   Returns a set of XYZ coordinates that have been chromatically adapted to the desired white point.
///

## `#!py Color.xy` {#xy}

```py
def xy(
    self,
    *,
    white: VectorLike | None = None
) -> Vector:
```

/// define
Description

-   Retrieves the CIE 1931 (x, y) chromaticity coordinates for a given color.

Parameters

- 
    Parameters  | Defaults           | Description
    ----------- | ------------------ | -----------
    `white`     | `#!py None`        | Specify the white in which to chromatically adapt the points from, if none is specified, the current color's white point is assumed.

Return

-   Returns a tuple of CIE 1931 (x, y) chromaticity points for the given color. The XYZ translation to xy will use the
    current color's white point to ensure the values are relative to the proper white point.
///

## `#!py Color.uv` {#xy}

```py
def uv(
    self,
    mode: str = '1976',
    *,
    white: VectorLike | None = None
) -> Vector:
    ...
```

/// define
Description

-   Retrieves the UCS 1960 (u, v) chromaticity coordinates for a given color or the CIE 1976 UCS (u', v') chromaticity
    coordinates, the latter being the default.

Parameters

- 
    Parameters  | Defaults           | Description
    ----------- | ------------------ | -----------
    `mode`      | `#!py3 '1976'`     | A string indicating what mode to use. `1976` refers to the (u', v') points as described by CIE 1976 UCS and `1960` describes the (u, v) points as documented by CIE 1960 UCS.
    `white`     | `#!py None`        | Specify the white in which to chromatically adapt the points from, if none is specified, the current color's white point is assumed.

Return

-   Returns a tuple of (u, v) -- either 1976 (u', v') or 1960 (u, v) -- chromaticity points for the given color. The XYZ
   translation to uv will use the current color's white point to ensure the values are relative to the proper white
   point.
///

## `#!py Color.get_chromaticity` {#get_chromaticity}

```py
def get_chromaticity(
    self,
    cspace: str = 'uv-1976',
    *,
    white: VectorLike | None = None
) -> Vector:
    ...
```

/// define
Description

-   Retrieves the 1931 xy, 1960 uv, or 1976 u'v' chromaticity coordinates with the luminance (Y). Coordinates are
    returned in the format specified by `cspace` and will use the white point of the current color.

Parameters

- 
    Parameters  | Defaults           | Description
    ----------- | ------------------ | -----------
    `cspace`    | `#!py 'uv-1976'`   | A string indicating what chromaticity space to use. `uv-1976` being the default.
    `white`     | `#!py None`        | Specify the white in which to chromatically adapt the points from, if none is specified, the current color's white point is assumed.

Return

-   Returns a list of chromaticity coordinates. Results will either be in [x, y, Y] for 1931 xy, [u, v, Y] for 1960 uv,
    or [u', v', Y] for 1976 u'v'.
///

## `#!py Color.chromaticity` {#get_chromaticity}

```py
@classmethod
def chromaticity(
    cls,
    space: str,
    coords: VectorLike,
    cspace: str = 'uv-1976',
    *,
    scale: bool = False,
    scale_space: str | None = None,
    white: VectorLike | None = None
) -> Color:
    ...
```

/// define
Description

-   Returns a color that satisfies the provided chromaticity coordinates. Coordinates can be in the form 1931 xyY, 1960
    uvY, or 1976 u'v'Y and can be configured via `cspace`. The target space to convert to should be specified via
    `space`. Chromaticity coordinates should math the white space of the targeted space, but if they are not the white
    point of the chromaticity coordinates can be specified with `white`.

Parameters

- 
    Parameters      | Defaults             | Description
    --------------- | -------------------- | -----------
    `space`         |                      | Color space to chromaticities to.
    `coords`        |                      | The chromaticity coordinates. Values can be in either 3D form (with luminance Y).
    `cspace`        | `#!py 'uv-1976'`     | A string indicating what chromaticity space to use. `uv-1976` being the default.
    `white`         | `#!py None`          | Specify the white in which to chromatically adapt the points from, if none is specified, the targeted color's white point is assumed.
    `scale`         | `#!py True`          | Scale the color with a linear RGB color space as defined by `scale_space`.
    `scale_space`   | `#!py None`          | If `scale` is enabled, `scale_space` defines the RGB color space in which the returned color should be scaled within. The color space should be a linear space for best results. If undefined, `srgb-linear` will be used.

Return

-   Returns a reference to a new [`Color`](#color) object that satisfies the chromaticity coordinates.
///

## `#!py Color.convert_chromaticity` {#convert_chromaticity}

```py
@classmethod
def convert_chromaticity(
    cls,
    cspace1: str,
    cspace2: str,
    coords: VectorLike
) -> Vector:
    ...
```

/// define
Description

-   Converts a 2D chromaticity pair from one chromaticity space to another. Supported spaces are `xy-1931`, `uv-1960`,
    and `uv-1976`.

Parameters

- 
    Parameters  | Defaults           | Description
    ----------- | ------------------ | -----------
    `cspace1`   |                    | Initial chromaticity space for the given coordinates.
    `cspace2`   |                    | Target chromaticity space for the given coordinates.
    `coords`    |                    | The 2D chromaticity coordinates to convert.

Return

-   Returns the converted 2D chromaticity coordinates.
