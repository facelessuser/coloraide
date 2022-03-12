# Changelog

## 0.12.0

- **NEW**: Add a gamut mapping variant that matches the CSS Color Level 4 spec.
- **FIX**: Fix precision rounding issue.

## 0.11.0

!!! warning "Breaking Changes"

    1. Prior to 0.11.0, if you specified a cylindrical space directly, ColorAide would normalize undefined hues the same
       way that the conversion algorithm did. In the below case, saturation is zero, so the hue was declared undefined.

        ```py
        >>> Color('hsl(270 0% 50%)')
        color(--hsl none 0 0.5 / 1)
        ```

        We should not have been doing this, and it made some cases of interpolation a bit confusing. It is no longer
        done as the hues are in fact specified by the user, even if they are powerless in relation to contributing to
        the rendered color. When a cylindrical color is converted or if a user declares the channel as undefined with
        `none` or some other way, then the channel will be declared undefined, because in these cases, they truly are.

        ```py
        >>> Color('white').convert('hsl')
        color(--hsl none 0 1 / 1)
        >>> Color('color(--hsl none 0 0.5)')
        color(--hsl none 0 0.5)
        ```

        If you are working directly in a cylindrical color space and ever wish to force the normalization of color hues
        as undefined when the color meets the usual requirements as specified by the color space's current rules, just
        call `normalize` on the color and it will apply the same logic that occurs during the conversion process.

        ```py
        >>> Color('hsl(270 0% 50%)').normalize()
        color(--hsl none 0 0.5 / 1)
        ```
    2. If you relied on commas in CSS forms that did not support them, this behavior is no longer allowed. It was
       thought that CSS may consider allowing comma formats in formats like `hwb()`, etc., and it was considered, but
       ultimately the decision was to avoid adding such support. We've updated our input and output support to reflect
       this. Color spaces can always be subclassed and have this support added back, if desired, but will not be shipped
       as the default anymore.
    3. The D65 form of Luv and LCHuv is now the only supported Luv based color spaces by default now. D50 Luv and LCHuv
       have been dropped and `luv` and `lchuv` now refers to the D65 version. In most places, the D65 is the most common
       used white space as most monitors are calibrated for this white point. The only reason CIELAB and CIELCH are D50
       by default is that CSS requires it. Anyone interested in using Luv with a different white point can easily
       subclass the current Luv and create a new plugin color space that uses the new white point.
    4. Renamed DIN99o Lch identifier to the short name of `lch99o`.

- **NEW**: ColorAide now only ships with the D65 version Luv and LCHuv as D65, in most places is the expected white
  space. Now, the identifier `luv` and `lchuv` will refer to the D65 version of the respective color spaces. D50
  variants are no longer available by default.
- **NEW**: Add the HSLuv color space.
- **NEW**: DIN99o Lch identifier was renamed from `din99o-lch` to `lch99o`. To use in CSS `color()` form, use
  `--lch99o`.
- **NEW**: Refactor chroma reduction/MINDE logic to cut processing time in half. Gamut mapping results remain very
  similar.
- **NEW**: Be more strict with CSS inputs and outputs. `hwb()`, `lab()`, `lch()`, `oklab()`, and `oklch()` no longer
  support comma string formats.
- **NEW**: Officially drop Python 3.6 support.
- **FIX**: Do not assume user defined, powerless hues as undefined. If they are defined by the user, they should be
  respected, even if they have no effect on the current color. This helps to ensure interpolations acts in an
  unsurprising way. If a user manually specifies the channel with `none`, then it will be considered undefined, or if
  the color goes through a conversion to a space that cannot pick an appropriate hue, they will also be undefined.

## 0.10.0

- **NEW**: Switch back to using CIELCH for gamut mapping (`lch-chroma`). There are still some edge cases that make
  `oklch-chroma` less desirable.
- **FIX**: Fix an issue where when attempting to generate steps some ∆E distance apart, the maximum step range was not
  respected and could result in large hangs.

## 0.9.0

!!! warning "Breaking Changes"
    Custom gamut mapping plugins no longer return coordinates and require the method to update the passed in color.

- **NEW**: Improved, faster gamut mapping algorithm.
- **NEW**: FIT plugins (gamut mapping) no longer return coordinates but should modify the color passed in.
- **NEW**: Expose default interpolation space as a class variable that can be controlled when creating a custom class
  via class inheritance.
- **NEW**: Colors can now directly specify the ∆E method that is used when interpolating color steps and using
  `max_delta_e` via the new `delta_e` argument. If the `delta_e` parameter is omitted, the color object's default ∆E
  method will be used.
- **NEW**: Oklab is now the default interpolation color space.
- **NEW**: Interpolation will now avoid fitting colors that are out of gamut unless the color space cannot represent
  out of gamut colors. Currently, all of the RGB colors (`srgb`, `display-p3`, etc.) all support extended ranges, but
  the HSL, HWB, and HSV color models for `srgb` (including spaces such as `okhsl` and `okhsv`) do not support extended
  ranges and will still be gamut mapped.
- **FIX**: Remove some incorrect code from the gamut mapping algorithm that would shortcut the mapping to reduce chroma
  to zero.

## 0.8.0

!!! warning "Breaking Changes"
    The use of `xyz` as the color space name has been changed in favor of `xyz-d65`. This better matches the CSS
    specification. As we are still in a prerelease state, we have not provided any backwards compatibility.

    CSS color input strings in the form `#!css-color color(xyz x y z)` will continue to be accepted as CSS will allow
    both the `xyz` and the `xyz-d65` identifier, but output serialization will prefer the
    `#!css-color color(xyz-d65 x y z)` form as using `xyz` is an alias for `xyz-d65`.

    Again, this breaking change only affects operations where the color space "name" is used in the API to specify usage
    of a specific color space in order to create a color, convert, mutate, interpolate, etc.

    ```python
    Color('red').convert('xyz')      # Bad
    Color('red').convert('xyz-d65')  # Okay

    Color('xyz' [0, 0, 0])      # Bad
    Color('xyz-d65' [0, 0, 0])  # Okay

    Color('red').interpolate('green', space='xyz')      # Bad
    Color('red').interpolate('green', space='xyz-d65')  # Okay

    # No changes to CSS inputs
    Color('color(xyz 0 0 0)')      # Okay
    Color('color(xyz-d65 0 0 0)')  # Okay
    ```

- **NEW**: Add the official CSS syntax `oklab()` and `oklch()` for the Oklab and Oklch color spaces respectively.
- **NEW**: Custom fit plugin's `fit` method now allows additional `kwargs` in its signature. The API will accept
  `kwargs` allowing a custom fit plugin to have configurable parameters. None of the current built-in plugins provide
  additional parameters, but this is provided in case it is found useful in the future.
- **NEW**: XYZ D65 space will now be known as `xyz-d65`, not `xyz`. Per the CSS specification, we also ensure XYZ D65
  color space serializes as `xyz-d65` instead of the alias `xyz`. CSS input string format will still accept the `xyz`
  identifier as this is defined in the CSS specification as an alias for `xyz-d65`, but when serializing a color to a
  string, the `xyz-d65` will be used as the preferred form.
- **NEW**: By default, gamut mapping is done with `oklch-chroma` which matches the current CSS specification. If
  desired, the old way (`lch-chroma`) can manually be specified or set as the default by subclassing `Color` and setting
  `FIT` to `lch-chroma`.
- **FIX**: Ensure the `convert` method's `fit` parameter is typed appropriately and is documented correctly.

## 0.7.0

- **NEW**: Formally expose `srgb-linear` as a valid color space.
- **NEW**: Distance plugins and gamut mapping plugins now use `classmethod` instead of `staticmethod`. This allows for
  inheritance from other classes and the overriding of plugin options included as class members.
- **NEW**: Tweak Lch chroma gamut mapping threshold.
- **FIX**: Issue where it is possible, when generating steps, to cause a shift in midpoint of colors if exceeding the
  maximum steps. Ensure that no stops are injected if injecting a stop between every color would exceed the max steps.

## 0.6.0

- **NEW**: Update spaces such that they provide a single conversion point which simplifies color space API and
  centralizes all conversion logic allowing us to pull chromatic adaptation out of spaces.
- **NEW**: `color()` output format never uses percent when serializing, but will optionally accept percent as input.
- **NEW**: Slight refactor of color space, delta E, and gamut mapping plugins. All now specify there name via the
  property `NAME` instead of methods `space()` for color spaces and `name()` for other plugins.
- **NEW**: Restructure source structure by flattening out some directories and better organizing source files. This
  changes some import paths.
- **NEW**: Color spaces do not specify `alpha` in `CHANNEL_NAMES` as the `alpha` name cannot be changed.
- **NEW**: Color space objects do not need a constant to track number of color channels.

## 0.5.0

- **NEW**: Add type annotations and refactor code to better accommodate the type annotations. Public API not really
  affected, but a bit of the internals have changed.
- **FIX**: Fix issue where `compose`, if `backdrop` list is empty, would not respect `in_place` option.

## 0.4.0

- **NEW**: Officially support Python 3.10.
- **NEW**: Slightly more accurate Oklab matrix calculation.
- **NEW**: Exported dictionary form can now be used as a normal color input in functions like `contrast`, `interpolate`,
  etc.
- **NEW**: Color objects will accept a dictionary mapping when `alpha` is not specified. When this occurs, `alpha` is
  assumed to be `1`.
- **FIX**: Fix an object compare issue.

## 0.3.0

!!! warning "Breaking Changes"
    XYZ changes below will cause breakage as `xyz` now refers to XYZ with D65 instead of D50. Also, CSS identifiers
    changed per the recent specification change.

- **NEW**: When calling `dir()` on `Color()`, ensure dynamic methods are in the list.
- **NEW**: `xyz` now refers to XYZ D65. CSS `#!css-color color()` function now specifies D65 color as either
  `#!css-color color(xyz x y z)` or `#!css-color color(xyz-d65 x y z)`. XYZ D50 is now specified as
  `#!css-color color(xyz-D50 x y z)`.
- **NEW**: Add CIELUV and CIELCH~uv~ D65 variants.

## 0.2.0

- **NEW**: Provide dedicated `clip` method. `clip` is still a specifiable method under the `fit` function. It is also
  a reserved name under `fit` and cannot be overridden via plugins or be removed.
- **NEW**: Add more conversion shortcuts to OK family of color spaces.
- **FIX**: Fix an issue where the shorter conversion path wasn't always taken as convert couldn't find to/from methods
  if the color space name had `-` in it.

## 0.1.0

First non-alpha prerelease. Notable changes from the last alpha listed below.

!!! warning "Breaking Changes"
    There are some breaking changes if coming from the previous alpha releases. All sRGB cylindrical spaces' non-hue
    data ranges are no longer scaled to 0 - 100, but use 0 - 1. Hue ranges have not changed.

- **NEW**: By accepting HSL, HSV, and HWB as non-hue channels as 0-100, we do lose a little precision, so for 1.0, we
  are switching to accepting and returning raw data values between 0 - 1. We've kept hue between 0 - 360 as it is easier
  for users to deal with hues between 0 - 360. Doing this will also match the new color spaces Okhsl and Okhsv that
  need to be kept at 0 - 1 to get better rounding.
- **NEW**: We do not currently restrict percentages anymore in `#!css-color color()` functions. There is no hard rules
  that we need to at this time and no currently specified spaces that do this in the CSS specification. This is relaxed
  for now until some future time when it becomes clear we must.
- **NEW**: New `okhsl` and `okhsv` color space.
- **NEW**: All color channels now accept the `none` keyword to specify an undefined channel. They can also optionally
  output CSS strings with the keyword.
- **NEW**: Interpolation will return an undefined channel if both colors have that channel set to undefined.
- **NEW**: Provide a way to dump a color object to a simple dictionary and have the `Color()` object accept that
  dictionary to recreate the color object.
- **NEW**: Provide `cat16` chromatic adaptation.
- **NEW**: Add `normalize` method to force channel normalization (evaluation of channels and setting undefined as
  appropriate).
- **NEW**: Interpolated and composited colors will normalize undefined channels when returning a color.
- **NEW**: Jzazbz now also has an alias for `az` and `bz` channels as `a` and `b` respectively.
- **FIX**: Fix an attribute "get" issue where attributes that were not present on the `Color()` object appeared to be
  present when using `hasattr()`.
- **FIX**: More accurate Oklab matrix.
