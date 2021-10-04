# Changelog

## 0.1

First non-alpha prerelease. Notable changes from the last alpha listed below.

- **NEW**: All color channels now accept the `none` key word to specify an undefined channel. They can also optionally
  output CSS strings with the key word.
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
