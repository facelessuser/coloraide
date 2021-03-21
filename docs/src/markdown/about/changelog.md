# Changelog

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
  done in sRGB, and LCH will request overlay to be done in LAB.
- **FIX**: Add support for premultiplied alpha when interpolating via `premultiplied` option.

## 0.1.0a1

- **NEW**: Initial alpha release. Library is experimental and API is unstable.

--8<-- "refs.txt"
