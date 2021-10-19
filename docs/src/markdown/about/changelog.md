# Changelog

## 0.4.0

- **NEW**: Officially support Python 3.10.
- **NEW**: Slightly more accurate Oklab matrix calculation.
- **NEW**: Exported dictionary form can now be used as a normal color input in functions like `contrast`, `interpolate`,
  etc.
- **NEW**: Color objects will accept a dictionary mapping when `alpha` is not specified. When this occurs, `alpha` is
  assumed to be `1`.
- **FIX**: Fix an object compare issue.

## 0.3.0

!!! warning "Breaking Change"
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
