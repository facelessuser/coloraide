# Changelog

## 0.1.0a2

- **FIX**: Cylindrical spaces, when calling `overlay` can now request to be overlaid in a different space. This is
  because alpha composition does not work well in cylindrical spaces. HSL, HSV, and HWB will now request `overlay` to be
  done in sRGB, and LCH will request overlay to be done in LAB.
- **FIX**: Add support for premultiplied alpha when interpolating via `premultiplied` option.

## 0.1.0a1

- **NEW**: Initial alpha release. Library is experimental and API is unstable.

--8<-- "refs.txt"
