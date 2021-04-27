# Changelog

## 0.10a19

- **FIX**: Ensure that subclassed `Color` objects are normalized when performing operations with more than one color to
  prevent issues in case one subclassed object has overridden important functions.
- **FIX**: Spaces like `lab`, `lch`, etc., which specify certain channels as percent only should require the `color()`
  format to only accept percentages for those channels and output those channels as percentages when converting to a
  string.

## 0.10a18

- **NEW**: Refactor of internals.
- **NEW**: `interpolate` and `steps` can now accept multiple colors and will return an interpolation function that spans
  all specified colors via the range of `[0..1]`.
- **NEW**: Better control over piecewise interpolation: setting stops, adjusting options per segment, etc.
- **NEW**: `compose` can now accept multiple colors and will return a result where all colors are layered on top of each
  other.
- **NEW**: `new` method does not need to be a `classmethod`. Make it a normal method on the instance.
- **NEW**: Add Jzazbz and JzCzhz color spaces.
- **NEW**: Add D65 variants of CIELAB, CIELCH, and XYZ.
- **NEW**: Add ICtCp color space and Delta E ITP method.
- **FIX**: Actually make `mix` default to `lab` like `interpolate` and friends do.

## 0.1.0a17

- **FIX**: Ensure that both the Bradford CAT and the XYZ transformation matrix all use ASTM E308-01 white points. This
  fixes a number of conversion issues when going to and from D65 to D50 color spaces.

## 0.1.0a16

- **NEW**: Make `mix` use the same space logic as `interpolate` and `step`. Colors are mixed in CIELAB unless `space` is
  set to a different color space.
- **NEW**: Add support for blend modes as specified in [Compositing and Blending Level 1][compositing-level-1].
- **NEW**: Rename `overlay` to `compose` as all compositing (including blend modes) is done through `compose` now.
  `overlay` is still present and is deprecated and will be removed at some future point before a stable release.
  `compose` will assume `sRGB` space unless a different space is specified, but `overlay` will function as it always
  did.
- **FIX**: Fix some small internal issues with `in_place` logic.

## 0.1.0a15

- **NEW**: The adjust parameter on `interpolate`, `steps`, and `mix` has been dropped. Instead, a general purpose method
  has been added to the `Color` object to mask one or more channels at a time. This can be used to create a temporary
  color with masked channels for the purpose of interpolation.
- **FIX**: Ensure that when `alpha` is `NaN` that it is handled in `overlay`.
- **FIX**: When using raw data in the `color()` function, and there is too little data, fill data with `NaN`.
- **FIX**: Fix issue where API `interpolate` method does not pass `out_space` parameter down.
- **FIX**: Disabling or forcing alpha did not work properly for HSL colors via `to_string`.
- **FIX**: `contrast` and `luminance` should use XYZ with a D65 white point, not the default XYZ space which uses a D50
  white point.
- **FIX**: Fix bug in Delta E 2000 algorithm.

## 0.1.0a14

- **NEW**: sRGB string output parameter `hex_upper` has been renamed to just `upper`. Expose it in documentation as
  well.

## 0.1.0a13

- **FIX**: More efficient calculation of CIELAB, following CIE 15.3:2004. Results are still the same, but it makes the
  math a little simpler.
- **FIX**: HSV did not always set hue to `NaN` when saturation was `0`.
- **FIX**: Give better conversion results by having HWB colors pass through HSV instead of sRGB.
- **FIX**: Fix slight issue with REC.2020 and ProPhoto color space conversion. Small issue when using `<=` when `<` was
  desired.

## 0.1.0a12

- **FIX**: More stable saturation calculation for HSL to ensure divide by zero doesn't occur.
  `2(V - L) / (1 - abs(2 * L - 1))` is likely to yield zero in the denominator when `L` is very small, while the
  equivalent `(V - L) / min(L, 1 - L)` is not.

## 0.1.0a11

- **FIX**: Ensure that when `hex`, `compress`, and `names` is enabled in `to_string` for `srgb` that colors will still
  match the color name if the color can be compressed.

## 0.1.0a10

- **FIX**: Address two divide by zero cases in HSL algorithm. Was missing some special cases when luminance equals `1`
  or `0`.

## 0.1.0a9

- **FIX**: Ensure all cases of hue handling, in regards to gamut mapping, are done the same.

## 0.1.0a8

- **NEW**: Remove workaround to force cylindrical colors to overlay in non-cylindrical spaces. Allow colors to be
  overlaid in any color space. Original issues related to allowing cylindrical spaces as been fixed. Overlaying in
  cylindrical spaces may not make sense, but it is no longer prohibited.
- **FIX**: Ensure color comparison will yield true if two channels have `NaN`.

## 0.1.0a7

- **FIX**: Fix issue with translation of an input that is compressed hex with a specified alpha.

## 0.1.0a6

- **FIX**: Don't return detached color spaces from `steps`. Ensure they are wrapped with a `Color` object on return.

## 0.1.0a5

- **FIX**: Fix an issue where `update` can fail due to a color space detached from a parent.
- **FIX**: Adjust fit tolerance to be a little more forgiving, but make an adjustment for `in_gmaut` in relation to
  `HSL` as `saturation` can be wildly out of range for an `sRGB` color that is only slightly out of gamut.
- **FIX**: Ensure `in_gamut` handles `NaN` properly.

## 0.1.0a4

- **NEW**: Use `NaN` to track undefined hues.
- **NEW**: Remove `is_hue_null` and add new API function `is_nan` to test if any channel is currently set to `NaN`.
- **NEW**: Remove `get_default` from the `Color` class and instead allow properties that can be overridden when
  subclassing the `Color` object.

## 0.1.0a3

- **FIX**: Color object API was missing the ability to receive the `premultiplied` argument.

## 0.1.0a2

- **NEW**: Expose access to `srgb-linear` color space. This is mainly for development and testing and not listed in docs
  currently.
- **FIX**: Cylindrical spaces, when calling `overlay` can now request to be overlaid in a different space. This is
  because alpha composition does not work well in cylindrical spaces. HSL, HSV, and HWB will now request `overlay` to be
  done in sRGB, and CIELCH will request overlay to be done in CIELAB.
- **FIX**: Add support for premultiplied alpha when interpolating via `premultiplied` option.

## 0.1.0a1

- **NEW**: Initial alpha release. Library is experimental and API is unstable.

--8<-- "refs.txt"
