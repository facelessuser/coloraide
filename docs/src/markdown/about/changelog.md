# Changelog

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
