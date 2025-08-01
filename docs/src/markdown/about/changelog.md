# Changelog

## 5.0

-   **BREAKING**: CSS serialization no longer requires HSL and HWB to return percentage form during serialization when
    using the non-legacy (no comma) syntax. For consistency, HSL and HWB will only return percentage form with
    non-legacy serialization when `percent` is set `True` by user. Legacy format will still format strings with
    percentages. This matches all other color spaces in ColorAide that use modern CSS serialization syntax. If you rely
    on ColorAide serializing HSL in the non-legacy format with percentage output, simply add `percent=True` when calling
    `to_string()`.
-   **NEW**: `Channel` object's `limit` parameter can now accept a function to constrain a channel. This can allow for
    more complex boundary constraint, such as rounding the value as well a channel within a hard boundary range.
-   **NEW**: CAM16, CAM02, HCT, ZCAM, Hellwig, Luv, and LChuv will no longer force colors to black when lightness is
    zero except when chroma/saturation/colorfulness is also zero. This allows out of gamut colors with lightness of zero
    to properly be seen as out of gamut.
-   **NEW**: Add new `Luminant` mixin for color spaces which allows for internally targeting spaces that expose a
    lightness component.
-   **NEW**: Rename `Regular` space mixin as `Prism` for a more appropriate description. `Regular` is still available
    but deprecated.
-   **NEW**: UCS, xyY, and Lab-like spaces are now considered `Prism` and `Luminant` spaces.
-   **NEW**: Spaces can now declare if they are "subtractive" via a `SUBTRACTIVE` class attribute.
-   **NEW**: Every space now exposes a `linear()`, `indexes()`, and `names()` method opposed to just a select few.
-   **NEW**: `raytrace` gamut mapping will now successfully operate on `Prism` color spaces (formerly `Regular`) as well
    as `RGBish`. `Prism` spaces which are also `Luminant` are not handled.
-   **NEW**: Harmonies now better handle irregular `Prism` spaces.
-   **NEW**: CMYK now uses CMY as the base conversion space and ensures round trip with wide gamut colors.
-   **FIX**: Analogous and split complementary harmony results ordered in a more logical configuration.
-   **FIX**: Fix an issue with some HDR spaces in ray trace gamut mapping.
-   **FIX**: Fix Duv sign flips and poor precision near inflection points in the Robertson 1968 CCT curve.
-   **FIX**: Fix an issue where a custom range of mired points for the Robertson 1968 CCT curve can fall exactly where
    slopes change direction, causing a divide by zero. Catch this case and skip any point that falls in this region.

## 4.7.2

-   **ENHANCE**: Improve performance of color harmony generation.
-   **ENHANCE**: Improve performance of gamut mapping using the `raytrace` approach when a color must be coerced to an
    RGB space.
-   **FIX**: When a `Color` instance is passed as an input to the `Color` constructor, use a more reliable check to
    ensure the color instance is of a compatible color space.
-   **FIX**: Fix regression that caused `longer` hue interpolation to no longer work with `discrete` interpolation.

## 4.7.1

-   **FIX**: Fix an issue where chromatic adaptation was being initiated when it wasn't needed. While conversion results
    were unaffected by this behavior, it did contribute to additional overhead, slowing conversions in some cases.

## 4.7

-   **NEW**: Officially support Python 3.14.
-   **NEW**: `average()` now accepts weights for weighted averaging.
-   **ENHANCE**: Switch to deploying with PyPI's "Trusted Publisher".
-   **ENHANCE**: Performance improvements for various algebraic calculations.
-   **FIX**: Fix some corner cases with some algebraic calculations.

## 4.6

-   **NEW**: Add new `rounding` option to control rounding modes in `to_string()`, `to_dict()`, `coords()`, `alpha()`,
    and `get()`. New rounding modes are: `sigfig` and `decimal` which are in addition to the default `digits` mode.
-   **FIX**: Fix typing for inherited colors.

## 4.5.1

-   **FIX**: Ensure Jzazbz, JzCzhz, and ICtCp actually use `--jzazbz`, `--jzczhz`, and `--ictcp` by default when
    serialized in the `color()` format.

## 4.5

-   **NEW**: Support change in CSS HDR spec that now specifies Jzazbz, JzCzhz, and ICtCp serialization as using the
    respective named color functions: `jzazbz()`, `jzczhz()`, and `ictcp()`. The `color()` format also use the custom
    hyphenated names `--jzazbz`, `--jzczhz`, and `--ictcp` respectively by default. The non-hyphenated names are still
    supported in the `color()` form for backwards compatibility, but usage is discouraged as at some future time
    support for non-hyphenated names will be dropped as CSS has moved away from this as a supported convention.
-   **NEW**: Reference ranges for Jzazbz, JzCzhz, and ICtCp, now match the latest CSS HDR spec.
-   **FIX**: Fix order of magnitude calculation.

## 4.4.1

-   **FIX**: Fix XYB transform.

## 4.4

-   **NEW**: Add support for the CAM02 color model and add the CAM02 JMh, CAM02 UCS, CAM02 SCD, and CAM02 LCD color
    spaces.
-   **NEW**: Add the Hellwig corrections to CAM16 under a new color model variant called Hellwig which adds two new
    color spaces: Hellwig JMh and Hellwig H-k JMh. The H-K variant add additional changes that adjusts lightness for the
    Helmholtz–Kohlrausch effect.
-   **NEW**: Deprecate submodule name `cam16_jmh` and `zcam_jmh` in favor of the more generic `cam16` and `zcam` names.
    Legacy submodule names are still accessible but will now raise a deprecation warning.
-   **FIX**: Scale achromatic threshold depending on order of magnitude of component scaling. This ensures colors that
    are scaled roughly between 0 - 1 are not considered achromatic earlier than a space scaled roughly between 0 - 100.
-   **FIX**: Optimized matrix math operations should handle column vectors.
-   **FIX**: Fix some issues with RYB Biased.

## 4.3

-   **NEW**: Interpolate plugins now define a `get_space` hook allowing them to validate and return an appropriate
    default space if the normal default cannot be supported.
-   **NEW**: Drop Python 3.8 support as it is "end of life".
-   **NEW**: Solve cubic Bezier curves algebraically for faster more predictable results.
-   **FIX**: Typing fixes.

## 4.2.2

-   **FIX**: More precise inverse of RYB Biased.
-   **FIX**: Speed up solving of cubic Bezier for easing functions.
-   **FIX**: Protect against possible divide by zero in HCT reverse transform.

## 4.2.1

-   **FIX**: Hex output should force gamut mapping even if it is requested to disable it as output will be invalid
    otherwise.

## 4.2

-   **NEW**: Provide new color spaces Okl~r~ab/OkL~r~Ch which use a modified lightness prediction.
-   **NEW**: Add new matrix math functions that are specifically optimized for matrices and vectors of length 3 and
    leverage it in all appropriate places for a performance boost.
-   **NEW**: Combine logic of `algebra` optimized vectorize functions and deprecate unnecessary function.
-   **NEW**: Some typing fixes and adjustments.

## 4.1

-   **NEW**: The `powerless` parameter is deprecated in `average()` as it is required to be always on for proper polar
    space averaging.
-   **FIX**: Polar space averaging was not setting hues to undefined when colors are evenly distributed. This is
    required as circular means cannot be found in these cases.
-   **FIX**: When averaging within a polar space, if the result hue is determined to be undefined at the end of
    averaging, the color will be treated as if achromatic, setting saturation/chroma as necessary. This is needed to
    prevent serialization of achromatic colors to a non-achromatic color when undefined values are resolved.
-   **FIX**: Fully transparent colors should only contribute alpha in color averaging, regardless of `premultiply`
    setting. This prevents fully transparent color channels, which provide no meaningful data, from distorting averages.
-   **FIX**: When averaging in a polar space, if a color is considered achromatic but does not have an undefined hue,
    the hue will be treated as undefined. Essentially the `powerless` parameter is now always `True`. This ensures that
    achromatic colors properly contribute to the average without distorting the hue.

## 4.0.1

-   **FIX**: Fix issue with `continuous` interpolation (and any that are derived from it, e.g., cubic spline
    interpolations) that can cause bad hue fixup calculations.
-   **FIX**: Fix issue with `continuous` interpolation (and any that are derived from it, e.g., cubic spline
    interpolations) that can cause premultiplication to be applied to a color twice.

## 4.0

-   **NEW**: Officially support Python 3.13.
-   **NEW**: Define HTML output representation for Jupyter via `_repr_html_`.
-   **NEW**: `get()`, `coords()`, `alpha()`, `to_dict()` can now return channel values with a specified precision via
    the new `precision` parameter. Per channel precision can be controlled if a list of precision is given.
-   **NEW**: `to_string()` support for per channel precision was added and `precision` can now accept a list of
    precision.
-   **NEW**: Remove deprecated `model` parameter from `cam16` ∆E method. Space should be used instead.
-   **NEW**: Remove deprecated `algebra.npow` function. `algebra.spow` should be used instead.
-   **NEW**: New generic `minde-chroma` gamut mapping method that allows specifying any Lab-ish or LCh-ish space to
    operate in. `oklch-chroma`, `lch-chroma`, and `hct-chroma` are now derived from `minde-chroma` and just default to
    using the specified color space to provide backwards compatibility. `minde-chroma` defaults to using OkLCh by
    default. `lch-chroma` is still ColorAide's default gamut mapping currently.
-   **NEW**: All MINDE chroma reduction methods now skip distance checks if a JND of zero is specified. A JND of zero
    essentially disables the MINDE behavior and will reduce chroma as close to the gamut boundary as possible faster
    than it would previously.
-   **NEW**: MINDE chroma reduction plugins now dynamically figures out lightness range instead of requiring it to be
    specified as a class attribute.
-   **NEW**: MINDE chroma reduction gamut mapping and ray trace gamut mapping now allow for specifying an `adaptive`
    option which will bias the chroma reduction by the specified factor in a hue independent way relative to a midpoint
    of L = 50%.
-   **NEW**: Remove deprecated `lab` parameter from experimental `raytrace` gamut mapping method. Users should use
    `pspace` instead to specify the perceptual space to use.
-   **NEW**: Class method `layer()` added to replace `compose()` with a multi-color handling similar to other API
    methods such as `interpolate()`, etc.
-   **NEW**: `compose()` has been deprecated in favor of the new `layer()` method and will be removed at some future
    time but is available to help with transition.
-   **NEW**: Improve experimental `raytrace` gamut mapping approach when performed in certain perceptual spaces.
-   **NEW**: The experimental `raytrace` gamut mapping method now uses OkLCh by default instead of CIELCh (D65). Results
    may vary.
-   **BREAK**: Pre-configured `oklch-raytrace` and `lch-raytrace` variants of the experimental `raytrace` gamut mapping
    method have been removed to reduce included plugins. OkLCh is the default now and users can still specify CIELCh and
    other perceptual spaces if desired via the `pspace` parameter. Additionally, documentation has been added so users
    can easily recreate the aforementioned pre-configured methods themselves or their own desired variants.
-   **BREAK**: MINDE chroma reductions plugin combines the `DE` and `DE_OPTIONS` class attributes under `DE_OPTIONS`.
    Users who have a derived gamut mapping class must combined these two options under `DE_OPTIONS`.
-   **BREAK**: MINDE chroma reduction plugin now specifies the perceptual space via the `PSPACE` attribute instead of
    `SPACE`. Users who have a derived, personal gamut mapping plugin need to update the name accordingly.
-   **BREAK**: MINDE chroma reduction plugins now specify the JND under the `JND` class attribute instead of `LIMIT`.
    Users who have a derived, personal gamut mapping plugin need to update the name accordingly.
-   **BREAK**: Interpolation plugin renamed the parameter `create` to `color_cls` which is a more descriptive and less
    confusing name. If a user interpolation plugin is derived and overrides the `__init__` method, it should update to
    use `color_cls` instead of `create`.
-   **FIX**: HWB and HSV cannot normalize hue and saturation the same way as HSL when saturation is negative.
-   **FIX**: Fix corner case in ZCAM that could throw a domain error.
-   **FIX**: `Color.new()` was documented as a class method but was internally still an instance method. Ensure it is a
    class method.

## 3.3.1

-   **FIX**: Ray trace gamut mapping algorithm will better handle perceptual spaces like CAM16 and HCT which have
    atypical achromatic responses. This prevents unexpected cutoff close to white.
-   **FIX**: Fix some documentation examples regarding gamut mapping in HCT.

## 3.3

-   **NEW**: Extend the `Cylindrical` mixin class to expose `radial_name()` and `radial_index()` on the color space to
    return the default name or default index of the radial coordinate in polar color spaces. It also exposes
    `is_polar()` as a simple check to see if the space uses polar coordinates.
-   **NEW**: Euclidean distance algorithm will now handle cylindrical color spaces by converting the polar coordinates
    to rectangular coordinates in order to return sensible results.
-   **NEW**: Allow specifying number of colors to return for monochromatic harmony. When fewer are specified, allow them
    to be spaced further apart for better contrast.
-   **FIX**: Handle unexpected undefined values in Euclidean distance.

## 3.2

-   **NEW**: Add `zcam-jmh` color model.
-   **NEW**: Previously, color spaces such as `cam16-jmh`, `cam16-ucs`, `jzczhz`, etc. would handle achromatic values
    absolutely, based on XYZ with the specified white point which could result in values with non-zero chroma. Now they
    will be handled relative to the space, meaning colors will be considered achromatic when they are close to zero
    chroma. What is considered achromatic is affected by the adapting luminance and other environmental settings.
    This simplifies logic making it faster and also easier for users to subclass with their own environmental settings.
-   **NEW**: Normalize how color spaces with special viewing conditions are configured. Document configuring viewing
    conditions of color models where applicable.
-   **NEW**: Add new `space` parameter in `cam16` ∆E method to replace the now deprecate `model` parameter. `space` is
    more flexible as users can now create CAM16 UCS spaces with different lighting environments and specify them
    instead.
-   **NEW**: Remove previously deprecated CAM16 Jab implementation. Use `cam16-ucs` instead.
-   **NEW**: Interpolation will now gracefully handle a list of a single color causing the interpolation to just return
    the single color.
-   **NEW**: More helpful interpolation errors will raise for an empty list.
-   **NEW**: Generic ray trace gamut mapping now has a new `pspace` parameter that can be used to specify a perceptual
    space in either LCh-ish or Lab-ish form. `lch` parameter is now deprecated, but currently still present, but
    `pspace` will take priority if both are defined.
-   **NEW**: Rename `algebra.npow` to `algebra.spow` (signed power). `algebra.npow` is now deprecated and will be
    removed at some future time.
-   **FIX**: Don't force space to clamp negative XYZ when they are absolutizing them in some spaces.
-   **FIX**: Ensure ST2084 EOTF implements the `max` step as specified in the spec.

## 3.1.2

-   **ENHANCE**: Further improvements to both speed and accuracy of ray trace gamut mapping.
-   **FIX**: Handle gamut mapping HDR spaces via ray trace more sanely.

## 3.1.1

-   **ENHANCE**: Improved performance of ray tracing gamut mapping algorithm.
-   **FIX**: Fix corner cases for detecting ray trace hits on gamut.

## 3.1

-   **NEW**: Increase accuracy of the experimental ray tracing gamut mapping algorithm.
-   **NEW**: Add generic gamut mapping algorithm that employs ray tracing method that can be used with any LCh
    perceptual space.
-   **NEW**: Ray tracing gamut mapping algorithm parameter `traces` will no longer do anything as the approach no longer
    has variable passes after new accuracy enhancements.
-   **FIX**: Jzazbz bug was fixed that would result in a divide by zero failure.

## 3.0.1

-   **FIX**: Don't cache coercion of non-RGB space to RGB space in ray tracing gamut mapping algorithm as the underlying
    color object could change underneath.

## 3.0

-   **BREAK**: The CSS HDR spec now defines the polar spaces such as JzCzhz `color()` with hue channels that support
    traditional hue syntax instead of percentages. Updated all polar spaces that are represented in the `color()` format
    to support this change. This is likely low impact as using percentages for hues is fairly uncommon.
-   **BREAK**: Remove previously deprecated functions: `algebra.apply`, `algebra.no_nans`, `algebra.no_nan`,
    `algebra.is_nan`, `Labish.labish_names`, `Labish.labish_indexes`, `LChish.lchish_names`, and
    `LCHish.lchish_indexes`. These were mainly used internally, so breakage is likely low.
-   **NEW**: `jzazbz`, `jzczhz`, `ictcp`, `rec2100-pq`, and `rec2100-hlg` are now formally recognized, and by default
    serialized, without the `--` prefix as all the spaces are now part of the official HDR specification in CSS.
    Previously, the spec was unofficial. `--` prefixed names will still be recognized, but at some future time `--`
    support will be removed for these spaces. Additionally, these spaces are now registered by default.
-   **NEW**: ∆E methods `z` and `itp` are now registered by default as their associated color spaces are now registered
    by default as well.
-   **NEW**: Color space channel flags `FLG_PERCENT` and `FLG_OPT_PERCENT` are deprecated and no longer used. They are
    still present, but will be removed in the future.
-   **NEW**: Update CSS percentage input/output ranges for `jzazbz`, `jzczhz`, and `ictcp` to match the CSS HDR spec.
-   **NEW**: Ray tracing gamut mapping algorithms have been added: `oklch-raytrace` and `lch-raytrace`.
-   **NEW**: RGB spaces now expose a `linear()` function on the underlying class to specify if they have a linear
    equivalent.
-   **NEW**: Adjust inheritance order of RGB spaces. Previously, many inherited from `sRGB`, now they inherit from
    `sRGBLinear`.
-   **NEW**: Add `rec2100-linear`, essentially and alias for `rec2020-linear`, that is specified in the CSS HDR
    specification.
-   **FIX**: Ensure that when using discrete interpolation that spline based interpolations are truly discrete.

## 2.16

-   **NEW**: Gamut mapping plugins now must accept a `space` parameter and the color will not already be in the desired
    gamut color space. This change was specifically made in order to fix a bug with HCT gamut mapping.
-   **FIX**: Fix corner cases in HCT gamut mapping that would struggle with colors with high chroma and low lightness.

## 2.15.1

-   **FIX**: Small regression related to indirectly gamut mapping in another space other than its own.

## 2.15

-   **BREAK**: ∆E HCT used an extremely small JND by default to yield tonal palettes that were comparable to Google's
    Material. This was not inline with other gamut mapping function defaults. The default is now a more appropriate
    value of `2`. Users that relied on ∆E HCT to help generate tonal pallets with HCT should now use the `jnd` parameter
    to set the JND to `0.02` in order to generate tonal pallets more like Google.
-   **NEW**: `fit()` now accepts a `jnd` option to control the JND limit when gamut mapping with `lch-chroma`,
    `oklch-chroma`, and `hct-chroma`.
-   **NEW**: `to_string()` can now accept a dictionary of arguments to control gamut mapping via the `fit` argument.
-   **FIX**: Update `lch-chroma` epsilon to be consistent with other gamut mapping plugin conventions.

## 2.14.1

-   **FIX**: More precision for HCT conversion for better round trip conversions.

## 2.14

-   **NEW**: `normalize()` will now also normalize a cylindrical color model with negative chroma/saturation to its
    positive chroma/saturation form, assuming one exists.
-   **NEW**: Gamut clipping is performed on a cylindrical color's normalized form ensuring that a color which is in
    gamut but has a negative chroma/saturation will be mapped more correctly.
-   **NEW**: Do not clamp user input of lightness and chroma in various spaces. Clamping will only occur during
    conversion if the algorithm requires it.
-   **NEW**: Channels can be accessed by `get` and `set` using their numerical value (as a string input).
-   **NEW**: Color space plugins that specify the gamut space via `GAMUT_CHECK` must use that color space as a
    reference when gamut mapping or clipping by default.
-   **NEW**: New color space plugin attribute `CLIP_SPACE` added which will override the space specified by
    `GAMUT_CHECK` to force clipping in the origin space even if a gamut mapping space is defined. This is only used when
    it is advantageous to clip in the origin space, e.g. when faster and still practical.
-   **NEW**: Deprecate non-standard CAM16 (Jab) space. People should use the standard CAM16 JMh or the CAM16 UCS, SCD,
    or LCD Jab spaces. The non-standard Jab is still available via `coloraide.spaces.cam16.CAM16`, but it is no longer
    available in `coloraide.everything` and will be removed at a future time.
-   **NEW**: Add new channel aliases: `j` for `jz` in Jzazbz and JzCzhz. Also add `c` for `cz` and `h` for `hz` in
    JzCzhz.
-   **NEW**: HSL will now always return positive saturation for wide gamut colors via its conversion.
-   **FIX**: Fix a an issue with the CAM16 model's transformation that prevented good round trip with negative
    lightness.
-   **FIX**: Ensure that when `harmony` auto creates a cylindrical space from a rectangular space that it checks
    achromatic status in the original color space.
-   **FIX**: ∆E HCT should use colorfulness, not chroma, in the calculation.
-   **FIX**: Don't return scientific notation when serializing colors.
-   **FIX**: Small fix for Rec. 2100 PQ conversion algorithm.
-   **FIX**: The oRGB color space should be gamut mapped in `srgb` as it is a transform of the sRGB space.
-   **FIX**: Because Okhsl and Okhsv have a rough sRGB approximation and not precise, they are instead gamut mapped to
    their own gamut by default.
-   **FIX**: Much more accurate ICtCp matrices.
-   **FIX**: Fix typing of deeply nested arrays in `algebra`.
-   **FIX**: Fix issue with HCT undefined channel resolver.
-   **FIX**: Proper handling of negative lightness for DIN99o.
-   **FIX**: Circular mean should return positive values.

## 2.13.1

-   **FIX**: Minor typing regressions and fixes.

## 2.13

-   **NEW**: Performance related enhancements in high traffic calculations.
-   **NEW**: Use `matmul` instead of `dot` in calculations to not confuse math savvy people.
-   **FIX**: Some typing fixes/improvements.
-   **FIX**: Minor fixes to `algebra` library.

## 2.12

-   **NEW**: When serializing, `percent` can now take a sequence of booleans to indicate which channels are desired to
    be represented as a percentage, alpha included.
-   **NEW**: `color()` serializing now supports string output with `percent`.
-   **FIX**: When serializing, the alpha channel is no longer handled special with a minimum value of `5`. Precision is
    equally applied to all channels.

## 2.11

-   **NEW**: Add new `css-linear` interpolator that provides compatibility with the CSS specification. This deviates
    from the default linear interpolator in how undefined hues are resolved for interpolation, particularly noticeable
    with `longer` hue resolution.
-   **NEW**: Add new `INTERPOLATOR` class option to change the default interpolator that is used.

## 2.10

-   **NEW**: Declare official support for Python 3.12.
-   **NEW**: `Color.steps` and `Color.discrete` now accept `delta_e_args` to allow configuring the underlying distance
    algorithm when using the `delta_e` option.
-   **NEW**: CIE Lab, both D50 and D65, are now derived from a `CIELab` class. CIE LCh, both D50 and D65, are also
    now derived from a `CIELCh` class. This makes it easy to determine a CIE Lab or CIE LCh space from other Lab-like
    spaces.
-   **NEW**: ∆E^\*^~76~, ∆E^\*^~94~, ∆E^\*^~00~, and ∆E^\*^~cmc~ all accept a new parameter called `space` which allows
    the user to specify a registered Lab color space name (one that is derived from the `CIELab` class) to use as the
    distancing color space. This allows a user to use D50 Lab (or any other variant) for distancing if required.
-   **FIX**: For consistency, ∆E^\*^~94~ and ∆E^\*^~cmc~ now use Lab D65 by default just like ∆E^\*^~76~ and
    ∆E^\*^~00~. This fixes an issue where the docs indicated that they use D65, but in actuality they were using D50.

## 2.9.1.post1

-   **FIX**: Fix incorrect changelog mention of recent fix being for HSL instead of HWB.

## 2.9.1

-   **FIX**: Average should allow controlling `powerless` be disabled by default for backwards compatibility.
-   **FIX**: HWB should use the algorithm defined in CSS that allows for round tripping even in the negative lightness
    direction. Previously we were converting directly from HSV.

## 2.9

-   **NEW**: Add `HWBish` mixin class.
-   **NEW**: Deprecate `algebra.no_nan()`, `algebra.no_nans()`, and `algebra.is_nan()`.
-   **NEW**: When averaging in a cylindrical space, always treat achromatic hues as powerless for better results.
-   **NEW**: Add experimental support for CSS "powerless" hue handling and carrying-forward in interpolation, both
    disabled by default.
-   **FIX**: Fix RLAB conversion.
-   **FIX**: Fix clipping of hues.
-   **ENHANCE**: Tweaks to some matrix calculations.
-   **ENHANCE**: Various performance related tweaks.

## 2.8

-   **NEW**: Add Cubehelix color space.
-   **NEW**: When precision is set to `-1` for string output, double precision (`17`) will be assumed.
-   **ENHANCE**: More robust and generally better matrix inverse. Related inverse matrices have been regenerated for
    consistency.

## 2.7.2

-   **FIX**: More accurate easing logic.

## 2.7.1

-   **FIX**: Fix issue where `harmony` would convert some colors to cylindrical spaces and not properly consider order
    of channels.
-   **FIX**: XYB, while Lab like in its default configuration, has such a large disparity in the non-lightness
    components that the ranges for them should not be the same when using percentages.
-   **FIX**: Lab like space mixins should not try and order `a` and `b` like coordinates when calling `indexes()`, but
    should return them in there current order with lightness first. The meaning of these components can be different
    enough for a given color space to make normalizing their ordered configuration meaningless and alter inherit hue
    direction when processing for `harmony`.

## 2.7

-   **NEW**: Add new RYB color space.
-   **NEW**: Add `Regular` mixin class for normal, 3 channel color spaces (sRGB, CMY, RYB, etc.).
-   **NEW**: `harmony()` can now accept and transform `Labish` and `Regular` color spaces to cylindrical spaces.

## 2.6

-   **NEW**: Add `padding` parameter to limit color scales when interpolating.

## 2.5

-   **NEW**: Add new `discrete()` function that creates a discrete interpolation object.
-   **NEW**: Deprecate `coloraide.algebra.apply` function in favor of new vectorize functions.
-   **FIX**: Fix small typing issue.
-   **FIX**: Tweaks to Oklab 64 bit matrix precision.
-   **FIX**: Fix `prismatic` and `cmyk` achromatic check logic.
-   **FIX**: Ensure IPT uses the exact white point as documented in the paper.
-   **FIX**: Fix various corner cases of algebraic functions and implement some performance improvements.

## 2.4

-   **NEW**: Add Rec. 709 RGB color space.
-   **NEW**: Add the 1960 UCS color space.
-   **NEW**: Add correlated color temperature support with new `cct()` and `blackbody()` API.
-   **NEW**: Add support for Robertson 1968 and Ohno 2013 CCT plugins.
-   **NEW**: Add support for determining if a color is in the Pointer Gamut and provide a way to clamp a color to the
    gamut.
-   **NEW**: Include CMFS: CIE 1931 2 Degree Standard Observer, CIE 1964 10 Degree Standard Observer, CIE 2015 2 Degree
    Standard Observer, and CIE 2015 10 Degree Standard Observer.
-   **NEW**: Add `split_chromaticity()` method which will split a color into its chromaticity and luminance parts.
-   **NEW**: Add `chromaticity()` which will create a new color from a given set of chromaticity coordinates.
-   **NEW**: Relax `chromatic_adaptation()` type requirement of white point chromaticity inputs.
-   **NEW**: `luminance()`, `xy()`, and `uv()` all now accept an optional white point via the `white` parameter to
    control the white point in which the returned values are relative to. `luminance()` still defaults to D65 but will
    use the current color's white point, like `xy()` and `uv()` if `white` is set to `None`.
-   **NEW**: `white()` now accepts a positional parameter allowing it to output the white point of the current color
    as various chromaticity coordinates in addition to the default XYZ coordinates.
-   **FIX**: Fix case where deregistering all plugins with `*` was not deregistering `Filter` plugins.

## 2.3

-   **NEW** ACEScc will now resolve undefined color channels (non-alpha) with a non-zero default that represents black
    for consistency with other ACES color spaces.
-   **ENHANCE**: Streamline averaging algorithm to increase performance.
-   **FIX**: Ensure that HCT consistently clamps negative lightness and chroma to zero.

## 2.2.2

-   **FIX**: Improve HCT round trip conversion speed and improve conversion in some weak areas.

## 2.2.1

-   **FIX**: Averaging of a channel set with only undefined values should return an undefined value.
-   **FIX**: Averaging should be done in linear light by default for a sane default. Default is now `srgb-linear`.

## 2.2

-   **NEW**: Add XYB color space.
-   **ENHANCE**: More efficient averaging.
-   **FIX**: Fix issue where if all colors have the same channel undefined that a divide by zero can occur.

## 2.1

-   **NEW**: Add new color averaging method.
-   **FIX**: Interpolation should not modify any input colors.

## 2.0.2

-   **FIX**: Consistent normalization of HWB hue.
-   **FIX**: Consistent normalization of color in harmony monochromatic.

## 2.0.1

-   **FIX**:  Incorrect result when interpolating from a cylindrical space to a rectangular space and using `out_space`.

## 2.0

-   **BREAK**: `interpolate`, `steps`, `mix`, `filter`, `compose`, and `harmony` will no longer base the output color on
    the first input color. Colors will be evaluated in the specified color space and be output in that space unless
    `out_space` is used to specify a specific output color space. For migration, specify the desired `out_space` if the
    working `space` does not match the desired output.

-   **BREAK**: Achromatic and undefined color channel handling has been rewritten. Color space objects no longer utilize
    the `normalize()` or `achromatic_hue()` method and instead now use a new `is_achromatic()` and `resolve_channel()`
    methods.

-   **NEW**: Expose the new `Color.is_achromatic()` method to tell if colors, even non-cylindrical colors, are
    achromatic or reasonably close to achromatic.

-   **NEW**: Color channel definitions can specify a non-zero default for an undefined channel. Use `resolve_channel()`
    for more advanced handling.

-   **NEW**: CAM16, CAM16 UCS, CAM16 SCD, CAM15 LCD, CAM16 JMh, HCT, Jzazbz, JzCzhz, and IPT all currently require a
    dynamic approach to detect achromatic colors. Undefined LCh chroma and hue channels and Lab a and b channels can now
    resolve to non-zero values when undefined for better achromatic interpolation.

-   **NEW**: ACEScct will now resolve undefined color channels (non-alpha) with a non-zero default that represents black
    as zero is actually out of gamut for that space.

-   **NEW**: `filter`, `compose`, and `harmony` all now support the `out_space` parameter.

-   **NEW**: All `<space>ish` mixin classes now give access to normalized names and indexes as `names()` and `indexes()`
    opposed to `<space>ish_names()` etc. Old methods are still available but are deprecated.

-   **NEW**: All RGB, HSL, and HSV color spaces are now created with a respective `RGBish`, `HSLish`, and `HSVish` mixin
    class.

-   **NEW**: Separable blend modes will now be evaluated in whatever RGB-ish color space is provided.

-   **NEW**: `compose` will throw an error if a non-RGB-ish color space is provided.

-   **NEW**: `Color.normalize()` added a new `nans` parameter that when set to `False` will prevent achromatic hue
    normalization and will just force all channels to be defined.

-   **NEW**: `Color.coords()` and `Color.alpha()`, which used to be available during the alpha/beta period have been
    re-added. `coords()` accesses just the color channels (no alpha channel) while `alpha()` gets the alpha channel.

-   **NEW**: Coordinate access functions: `get()`, `set()`, `coords()`, and `alpha()` functions now have a `nans`
    parameter that when set to `False` will ensure the component(s) is returned as a real number instead of NaN. Set
    operations only apply this when passing the current value to a callback for relative modification.

-   **NEW**: A `norm` parameter is now added to `convert` and `update`. When set to `False`, it will prevent achromatic
    normalization of hues during conversion. If no conversion is needed, the color is returned as is.

-   **NEW**: ColorAide used to gamut map colors such as HSL, HSV, and HWB when interpolating into those spaces. This is
    no longer done. It is possible to gamut map wider gamuts with these color spaces, so it will be up to the user to
    apply gamut mapping when it is determined they need it.

-   **NEW**: `EXTENDED_RANGE` is no longer needed and is removed from current color space classes.

-   **NEW**: Improved accuracy for Oklab, OkLCh, Okhsl, and Okhsv.

-   **NEW**: New "continuous" interpolation method.

-   **FIX**: Fix aliases in IPT and IgPgTg.

-   **FIX**: Fix some conversion issues with CAM16 based color spaces that was caused due to bad achromatic handling.

## 1.8.2

-   **FIX**: Fix some exception messages.

## 1.8.1

-   **FIX**: Ensure Judd-Vos correction is applied to linear RGB to LMS conversion for CVD.
-   **FIX**: Fix outdated API information in docs.

## 1.8.0

-   **NEW**: Modern sRGB, HSL, and HWB should allow mixed percentage and numbers. HSL and HWB percentages in the `hsl()`
    and `hwb()` formats respectively will resolve to numbers in the range [0, 100]. These changes reflect the latest
    changes in the CSS Level 4 Color spec.
-   **NEW**: HSL and HWB can serialize to a modern syntax that does not use percentages, but the default still uses
    percentages.
-   **NEW**: Rework CSS parsing for better performance.
-   **FIX**: Handle some parsing corner cases that are handled by browsers, but not by ColorAide. For example,
    `color(srgb 1-0.5.4)` should parse as `color(srgb 1 -0.5 0.4)`.
-   **FIX**: Ensure that `COLOR_FORMAT` is respected.

## 1.7.1

-   **FIX**: Ensure CAM16 spaces mirrors positive and negative percentages for `a` and `b` components.
-   **FIX**: Since the CAM16 JMh model can not predict achromatic colors with negative lightness and, more importantly,
    negative lightness is not useful, limit the lower end of lightness in CAM16 spaces to zero.
-   **FIX**: When a CAM16 JMh (or HCT) color's chroma, when not discounting illuminance, has chroma drop below the
    actual ideal achromatic chroma threshold, just use the ideal chroma to ensure better conversion back to XYZ.
-   **FIX**: Jzazbz and JzCzhz model can never translate a color with a negative lightness, so just clamp negative
    lightness while in Jzazbz and JzCzhz.
-   **FIX**: Fix a math error in CAM16.
-   **FIX**: Fix CAM16 JMh M limit which was too low.
-   **FIX**: IPT was set to "bound" when it should have an unbounded gamut.
-   **FIX**: When both `comma` and `none` are enabled it could make undefined alpha values show up as `none` in legacy
    CSS format.
-   **FIX**: Sane handling of inverse lightness in DIN99o.

## 1.7

-   **NEW**: Add support for CAM16 Jab and JMh: `cam16` and `cam16-jmh` respectively.
-   **NEW**: Add support for CAM16 UCS (Jab forms): `cam16-ucs`, `cam16-scd`, and `cam16-lcd`.
-   **NEW**: Add support for the HCT color space (`hct`) which combines the colorfulness and hue from CAM16 JMh and the
    lightness from CIELab.
-   **NEW**: Gamut mapping classes derived from `fit_lch_chroma` can set `DE_OPTIONS` to pass ∆E parameters.
-   **NEW**: While rare, some cylindrical color spaces have an algorithm such that achromatic colors convert best with a
    very specific hue. Internally, this is now handled during conversions, but there can be reasons where knowing the
    hue can be useful such as plotting. Cylindrical spaces now expose a method called `achromatic_hue()` which will
    return this specific hue if needed.
-   **FIX**: Fix `rec2100-hlg` transform.
-   **FIX**: Some color transformation improvements.
-   **FIX**: Relax some achromatic detection logic for sRGB cylindrical models. Improves achromatic hue detection
    results when converting to and from various non-sRGB color spaces.

## 1.6

-   **NEW**: Add `rec2100-hlg` color space.
-   **BREAKING**: `rec2100pq` should have been named `rec2100-pq` for consistency. It has been renamed to `rec2100-pq`
    and serializes with the CSS ID of `--rec2100-pq`. This is likely to have little impact on most users.

## 1.5

-   **NEW**: Formally add support for Python 3.11.
-   **NEW**: Add support for custom domains when interpolating.
-   **NEW**: `set()` can now take a dictionary of channels and values and set multiple channels at once.
-   **NEW**: `get()` can now take a list of channels and will return a list of those channel values.
-   **ENHANCE**: Simplify some type annotation syntax.
-   **ENHANCE**: Some minor performance enhancements.
-   **FIX**: Fix OkLCh CSS parsing.

## 1.4

-   **NEW**: A color space can now declare its dynamic range. By default, spaces are assumed to be SDR, but can declare
    themselves as HDR, or something else. This allows ColorAide to make decisions based on a color's dynamic range.
-   **NEW**: Add channel aliases for IPT and IPT-like color spaces (IgPgTg and ICtCp): `intensity`, `protan`, and
    `tritan`.
-   **FIX**: The ICtCp and oRGB space would return the Lab-ish equivalents for `a` and `b` in reverse order if calling
    `Labish.labish_names`. This was not actually called anywhere in the code, but is now fixed for any future cases that
    may require calling it.
-   **FIX**: Undefined channels should be ignored when clipping a color.
-   **FIX**: Do not apply SDR shortcuts in gamut mapping when fitting in a non-SDR color gamut, such as HDR.

## 1.3

-   **ENHANCE**: Color vision deficiency filters can now be instantiated with different default methods for severe and
    anomalous cases.
-   **FIX**: Fix premultiplication handling when using `compose`.

## 1.2

-   **NEW**: Add new monotone interpolation method.
-   **ENHANCE**: Better extrapolation past end of spline.
-   **FIX**: Small speed up in natural spline calculation.
-   **FIX**: Fix import that should have been relative, not absolute.

## 1.1

-   **NEW**: Slight refactor of interpolation plugin so that common code does not need to be duplicated, and the
    `interpolate` method no longer needs to accept an `easing` parameter as the plugin class exposes a new `ease` method
    to automatically acquire the proper, specified easing function and apply it.
-   **NEW**: Functions built upon interpolation can now use a new `extrapolate` parameter to enable extrapolation if
    interpolation inputs exceed 0 - 1. `point` will be passed to `Interpolator.interpolate` un-clamped if `extrapolate`
    is enabled. If a particular interpolation plugin needs to do additional work to handle extrapolation, they can check
    `self.extrapolate` to know whether extrapolation is enabled.
-   **NEW**: Implement and provide the following easing functions as described in the CSS Easing Level 1 spec:
    `cubic_bezier`, `ease`, `ease_in`, `ease_out`, and `ease_in_out`. Also provide a simple `linear` easing function.
-   **New**: Add `natural` and `catrom` cubic spline options for interpolation. The `catrom` (Catmull-Rom) spline
    requires the plugin to be registered in order to use it.
-   **FIX**: Due to floating point math, B-spline could sometimes return an interpolation of fully opaque colors with an
    imperceptible amount of transparency. If alpha is very close (`#!py3 1e-6`) to being opaque, just round it to
    opaque.
-   **FIX**: An easing function's output should not be clamped, only the input, and that only **needs** to occur on the
    outer range of an entire interpolation.

## 1.0

/// success | Stable Release!
Checkout [migration guide](./releases/1.0.md) if you were an early adopter.
///

-   **NEW**: Bezier interpolation dropped for B-spline which provides much better interpolation.
-   **NEW**: All new interpolation methods now supports hue fix-ups: `shorter`, `longer`, `increasing`, `decreasing`,
    and `specified`.
-   **NEW**: Interpolation is now exposed as a plugin to allow for expansion.
-   **FIX**: Fixed an issue related to premultiplication and undefined alpha channels.

## 1.0rc1

/// warning | Plugin Refactor
For more flexibility there was one final rework of plugins. Registering requires all plugins to be instantiated
before being passed into `Color.register`, but this allows a user redefine some defaults of certain plugins.

`coloraide.ColorAll` was moved to `coloraide.everythng.ColorAll` to avoid allocating plugins when they are not
desired.

In the process, we also renamed a number of plugin classes for consistency and predictability, details found below.
///

-   **NEW**: Updated some class names for consistency and predictability. `XyY` --> `xyY`, `Din99o` --> `DIN99o`, `SRGB`
    --> `sRGB`, and `ORGB` --> `oRGB`.

    Lastly, `LCh` should be the default casing convention. This convention will be followed unless a spec mentions
    otherwise. Changes: `Lch` --> `LCh`, `LchD65` --> `LChD65`, `Oklch` --> `OkLCh`, `Lchuv` --> `LChuv`, `Lch99o` -->
    `LCh99o`, `LchChroma` --> `LChChroma`, `OklchChroma` --> `OkLChChroma`, and `Lchish` --> `LChish`.

-   **NEW**: Updated migration guide with recent plugin changes.
-   **NEW**: `coloraide.ColorAll` renamed and moved to `coloraide.everything.ColorAll`. This prevents unnecessary
    inclusion and allocation of objects that are not desired.
-   **NEW**: Default `Color` object now only registers `bradford` CAT by default, all others must be registered
    separately, or `coloraide.everything.Color` could be used.
-   **NEW**: All plugin classes must be instantiated when being registered. This allows some plugins to be instantiated
    with different defaults. This allows some plugins to be configured with different defaults.

    ```py
    # Before change:
    Color.register([Plugin1, Plugin2])

    # After change:
    Color.register([Plugin1(), Plugin2(optional_parm=True)])
    ```

-   **FIX**: Negative luminance is now clamped during contrast calculations.

## 1.0b3

-   **FIX**: Fixed the bad `CAT16` matrix for chromatic adaptation.
-   **FIX**: Small fix related to how `CAT` plugin classes are defined for better abstraction.
-   **FIX**: Restrict optional keywords in `Color.register()` and `Color.deregister()` to keyword _only_ parameters.

## 1.0b2

/// warning | Breaking Changes
1.0b2 only introduces one more last breaking change that was forgotten in 1.0b1.
///

-   **BREAK**: Remove `filters` parameter on new class instantiation.
-   **NEW**: Added new migration guide to the documentation to help early adopters move to the 1.0 release.
-   **NEW**: Added HPLuv space described in the HSLuv spec.
-   **NEW**: Added new color spaces: ACES 2065-1, ACEScg, ACEScc, and ACEScct.
-   **NEW**: Contrast is now exposed as a plugin to allow for future expansion of approaches. While there is currently
    only one approach, methods can be selected via the `method` attribute.
-   **NEW**: Add new `random` method for generating a random color for a given color space.

## 1.0b1

/// warning | Breaking Changes
1.0b1 introduces a number of breaking changes. As we are very close to releasing the first stable release, we've
taken opportunity to address any issues related to speed and usability. While this is unfortunate for early
adopters, we feel that in the long run that these changes will make ColorAide a better library. We've also added new
a new Bezier interpolation method and added many more color spaces!
///

-   **BREAK**: The `coloraide.Color` object now only registers a subset of the available color spaces and ∆E algorithms
    in order to create a lighter default color object. `coloraide.ColorAll` has been provided for a quick way to get
    access to all available color spaces and plugins. Generally, it is recommend to subclass `Color` and register just
    what is desired.

-   **BREAK**: Reworked interpolation:

    -   `interpolate` and `steps` functions are now `@classmethod`s. This alleviates the awkward handling of
        interpolating colors greater than 2. Before, the first color always had to be an instance and then the rest had
        to be fed into that instance, now the methods can be called from the base class or an instance with all the
        colors fed in via a list. Only the colors in the list will be evaluated during interpolation.
    -   `Piecewise` object has been removed.
    -   `stop` objects are used to wrap colors to apply a new color stop.
    -   easing functions can be supplied in the middle of two colors via the list input.
    -   `hint` function has been provided to simulate CSS color hinting. `hint` returns an easing function that modifies
        the midpoint to the specified point between two color stops.
    -   A new bezier interpolation method has been provided. When using `interpolate`, `steps`, or `mix` the
        interpolation style can be changed via the `method` parameter. `bezier` and `linear` are available with `linear`
        being the default.

-   **BREAK**: Dictionary input/output now matches the following format (where alpha is optional):

    ```py
    {"space": "name", "coords": [0, 0, 0], "alpha": 1}
    ```

    This allows for quicker processing and less complexity dealing with channel names and aliases.

-   **BREAK**: The CSS Level 4 Color spec has accepted our proposed changes to the gamut mapping algorithm. With this
    change, the `oklch-chroma` gamut mapping algorithm is now compliant with the CSS spec, and `css-color-4` is no
    longer needed. If you were experimenting with `css-color-4`, please use `oklch-chroma` instead. The algorithm is
    faster and does not have the color banding issue that `css-color-4` had, and it is now exactly the same as the CSS
    spec.

-   **BREAK**: New breaking change. Refactor of `Space` plugins. `Space` plugins are no longer instantiated which cuts
    down on overhead lending to better performance. `BOUNDS` and `CHANNEL_NAMES` attributes were combined into one
    attribute called `CHANNELS` which serves the same purpose as the former attributes. `Space` plugins also no longer
    need to define channel property accessors as those are handled through `CHANNELS` in a more generic way. This is a
    breaking change for any custom plugins.

    Additionally, the `Space` plugin's `null_adjust` method has been renamed as `normalize` matching its functionality
    and usage in regards to the `Color` object. It no longer accepts color coordinates and alpha channel coordinates
    separately, but will receive them as a single list and return them as such.

-   **BREAK**: `Color`'s `fit` and `clip` methods now perform the operation in place, modifying the current color
    directly. The `in_place` parameter has been removed. To create a new color when performing these actions, simply
    clone the color first: `#!py color.clone().clip()`.

-   **BREAK**: Remove deprecated dynamic properties which helps to increase speed by removing overhead on class property
    access.

-   **BREAK**: Remove deprecated dynamic properties which helps to increase speed by removing overhead on class property
    access. Use indexing instead: `color['red']` or `color[0]`.

-   **BREAK**: Remove deprecated `coords()` method. Use indexing and slices instead: `color[:-1]`.

-   **NEW**: Update `lch()`, `lab()`, `oklch()`, and `oklab()` to optionally support percentages for lightness, chroma,
    a, and b. Lightness is no longer enforced to be a percentage in the CSS syntax and these spaces will serialize as a
    number by default instead. Optionally, these forms can force a percentage output via the `to_string` method when
    using the `percentage` option. Percent ranges roughly correspond with the Display P3 gamut per the CSS
    specification.

    Additionally, CSS color spaces using the `color()` format as an input will translate using these same ranges if the
    channels are percentages. `hue` will also be respected and treated as 0 - 360 when using a percentage.

    Non-CSS color spaces will also respect their defined ranges when using percentages in the `color()` form.

-   **NEW**: Add `silent` option to `deregister` so that if a proper category is specified, and the plugin does not
    exit, the operation will not throw an error.

-   **NEW**: Add new color spaces: `display-p3-linear`, `a98-rgb-linear`, `rec2020-linear`, `prophoto-rgb-linear`, and
    `rec2100pq`, `hsi`, `rlab`, `hunter-lab`, `xyy`, `prismatic`, `orgb`, `cmy`, `cmyk`, `ipt`, and `igpgtg`.

-   **NEW**: Monochromatic color harmony must also be performed in a cylindrical color space to make achromatic
    detection easier. This means all color harmonies now must be performed under a cylindrical color space.

-   **NEW**: Use Lab D65 for ∆E 2000, ∆E 76, ∆E HyAB, Euclidean distance, and LCh D65 for LCh Chroma gamut mapping. Lab
    D65 is far more commonly used for the aforementioned ∆E methods. LCh Chroma gamut mapping, which uses ∆E 2000 needs
    to use the same D65 white point to avoid wasting conversion time.

-   **FIX**: Better handling of monochromatic harmonies that are near white or black.

-   **FIX**: Small fix to `steps` ∆E logic.

## 0.18.1

-   **FIX**: Fix issue where when generating steps with a `max_delta_e`, the ∆E was reduced too much causing additional,
    unnecessary steps along with longer processing time.

## 0.18.0

-   **NEW**: Allow dictionary input to use aliases in the dictionary.
-   **FIX**: If too many channels are given to a color space via raw data, ensure the operation fails.
-   **FIX**: Sync up achromatic logic of the Okhsl and Okhsv `normalize` function with the actual conversion algorithm.
-   **FIX**: Regression that caused `cat16` not to work due to a misnamed variable.

## 0.17.0

/// warning | Interpolations Are Now Premultiplied
ColorAide has moved to make premultiplication the default for interpolation methods such as `mix`, `steps`, and
`interpolate`. The aim is to provide more accurate interpolation when using transparent colors. In cases where
premultiplication is not desired, it can be disabled by setting it to `#!py3 False`. There are real reasons to do so
as it may be desirous to mimic an old implementation that has always used naive interpolation of transparent colors.

Additionally, in the past, premultiplication was not really documented as it had not been fully tested.
Premultiplication is now covered in the documentation.
///

-   **NEW**: All mixing/interpolation methods will use `#!py3 premultiply=True` by default.
-   **NEW**: Allow aliases in interpolation's progress mappings.
-   **FIX**: Fix premultiplication when alpha is undefined.
-   **FIX**: Fix some potential issues in some matrix math logic.
-   **FIX**: `#!py Piecewise()` object didn't default all the non-required parameters to `#!py None` as documented.

## 0.16.0

/// warning | Deprecations
In interest of speed, and due to the overhead inflicted on every class attribute access, we've decided to deprecate
dynamic properties. This includes dynamic color properties (e.g. `Color.red`) and dynamic ∆E methods (e.g.
`Color.delta_e_2000()`). As far as color channel coordinate access is concerned, we've reworked a faster more useful
approach. ∆E already has a suitable replacement and will be the only approach moving forward.

1.  Use of `delta_e_<method>` is deprecated. Users should use the already available `delta_e(color, method=name)`
    approach when using non-default ∆E methods.

2.  Color channel access has changed. Dynamic channel properties have been deprecated. Usage of `Color.coords()` has
    also been deprecated. All channels can now easily be accessed with indexing. `Color.get()` and `Color.set()`
    have not changed.

    -   You can index with numbers: `Color[0]`.
    -   You can index with channel names: `Color['red']`.
    -   You can slice to get specific color coordinates: `Color[:-1]`.
    -   You can get all coordinates: `Color[:]` or `list(Color)`.
    -   You can even iterate coordinates: `[c for c in Color]`.
    -   Indexing also supports assignment: `Color[0] = 1` or `Color[:3] = [1, 1, 1]`.

Please consider updating usage to utilize the suggested approaches. The aforementioned methods will be removed
sometime before the 1.0 release.
///

-   **NEW**: `Color` objects are now indexable and channels can be retrieved using either numbers or strings, e.g.,
    `#!py3 Color[0]` or `#!py3 Color['red']`. Slicing and assignments via slicing are also supported:
    `#!py3 Color1[:] = Color2[:]`.
-   **NEW**: `Color.coords()`, dynamic color properties, and dynamic ∆E methods are all deprecated.
-   **NEW**: Input method names for distancing, gamut mapping, compositing, and space methods are now case sensitive.
    There were inconsistencies in some places, so it was opted to make all case sensitive.
-   **NEW**: The ability to create color harmonies has been added via the new `harmony()` method. Also, the default
    color space used to calculate color harmonies can be overridden by the class property `HARMONY`.
-   **NEW**: Add new support for filters added via the `filter()` method. Filters include the W3C Filter Effects Level 1
    and color vision deficiency simulation.
-   **NEW**: Some performance enhancements in conversions.
-   **NEW**: Chromatic adaptation is now exposed as a plugin. New CAT plugins can be created externally and registered.
-   **FIX**: Okhsl and Okhsv handling of achromatic values during conversion.

## 0.15.1

- **FIX**: Fix an issue related to matching colors in a buffer at a given offset.

## 0.15.0

/// warning
No changes in the public API have changed, but type annotations have. If you were importing type annotations, you
will have to update them.

Also, if any undocumented math related methods were accessed (for plugins or otherwise) they've been moved to
`coloraide.algebra`
///

-   **NEW**: A number of performance improvements.
-   **NEW**: Regenerate all matrices with our own matrix tools so that there is consistency between precision of
    pre-generated matrices and on-the-fly matrix generation. Reduces some noise in a few color space transforms.
-   **NEW**: Changes to type annotations. `Mutable<type>`, where type is either `Matrix`, `Vector`, or `Array`, are
    simply known as `<type>`. Types previously specified as `<type>`, where type is either `Matrix`, `Vector`, or
    `Array`, are now known as `<type>Like`. The types are expected to be mutable lists, anything else is noted as
    "like".
-   **NEW**: All matrix and math utilities have been moved to `coloraide.algebra`.
-   **FIX**: Fix rare issue where precision adjustment could fail.
-   **FIX**: Fix matrix `divide` logic when dividing a number or vector by a matrix. There are no actual usage of these
    cases in the code but they were fixed in case they are used in the future.

## 0.14.1

- **FIX**: Fix bug related to parsing strings without full matching.

## 0.14.0

/// note
No changes should break existing color space plugins. Moved objects and references are still also available in old
locations, and new functionality is implemented in such a way as to not break existing plugins, but plugins should
be updated as sometime before the 1.0 release, such legacy access will be removed.
///

-   **NEW**: Faster parsing. Instead of parsing `color(space ...)` each time it is evaluated for a different color
    space, parse it generically and then associate it with a given registered color space. If a color spaces wishes to
    opt out of the `color(space ...)` input format, the space should set `COLOR_FORMAT` to `False`. This means there is
    no need to call `super.match()` when overriding `Color.match()` to ensure support for the `color(space ...)` format
    as it will be handled unless `COLOR_FORMAT` is turned off. `DEFAULT_MATCH` usage should also be discontinued as it
    now does nothing.
-   **NEW**: Other speed optimizations.
-   **NEW**: All CSS parsing and serialization is now contained in a single module at `coloraide.css`. This simplifies
    the current color space classes greatly when it comes to supporting CSS specific formats.
-   **NEW**: Move our white space mapping to the `cat` module as it makes more sense there.
-   **NEW**: `GamutBound`, `GamutUnbound`, and associated flags are now contained under `coloraide.gamut.bounds`.
-   **NEW**: `normalize` will also remove masked values to properly adjust the color.
-   **FIX**: Compositing and blending should not "fit" colors before applying, it is only specified that the range
    should be clamped at the end of blending.
-   **FIX**: Fix issue where a subclassed `Color()` object could not recognize the base class or other subclasses.

## 0.13.0

-   **NEW**: Add new `closest` method that takes a list of colors and returns the one that is closet to the calling
    color object.
-   **NEW**: CSS color syntax no longer allows for forgiving channels in `color()`. This means that when a channel other
    than alpha is omitted, we will no longer treat them as undefined. Instead, the color will simply fail to parse.
    Raw data channels also must specify all channels.
-   **NEW**: Clamp lower bounds of chroma at the channel level.
-   **NEW**: `coloraide.spaces.WHITES` is now a 2 deep dictionary containing both 2˚ and 10˚ observer variants of white
    points.
-   **NEW**: Color space plugins now specify `WHITE` as a tuple with the x and y chromaticity coordinates. This allows a
    space to specify unknown white points if desired.
-   **FIX**: Fix `longer` hue interpolation when `θ1 - θ2 = 0`. The spec is wrong in this case, and interpolation should
    still occur the long way around instead of keeping hue constant.
-   **FIX**: Reduce redundancy in some CSS parsing patterns.
-   **FIX**: Minor performance improvements.
-   **FIX**: Legacy `rgb()`, `rgba()`, `hsl()`, and `hsla()` comma separated forms in CSS do not support `none`, only
    the new space separated forms do.
-   **FIX**: Ensure `py.typed` is installed with package so that type annotations work properly.

## 0.12.0

-   **NEW**: Add a gamut mapping variant that matches the CSS Color Level 4 spec.
-   **FIX**: Fix precision rounding issue.

## 0.11.0

/// warning | Breaking Changes
1.  Prior to 0.11.0, if you specified a cylindrical space directly, ColorAide would normalize undefined hues the same
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
2.  If you relied on commas in CSS forms that did not support them, this behavior is no longer allowed. It was
    thought that CSS may consider allowing comma formats in formats like `hwb()`, etc., and it was considered, but
    ultimately the decision was to avoid adding such support. We've updated our input and output support to reflect
    this. Color spaces can always be subclassed and have this support added back, if desired, but will not be shipped
    as the default anymore.
3.  The D65 form of Luv and LChuv is now the only supported Luv based color spaces by default now. D50 Luv and LChuv
    have been dropped and `luv` and `lchuv` now refers to the D65 version. In most places, the D65 is the most common
    used white space as most monitors are calibrated for this white point. The only reason CIELab and CIELCh are D50
    by default is that CSS requires it. Anyone interested in using Luv with a different white point can easily
    subclass the current Luv and create a new plugin color space that uses the new white point.
4.  Renamed DIN99o LCh identifier to the short name of `lch99o`.
///

-   **NEW**: ColorAide now only ships with the D65 version Luv and LChuv as D65, in most places is the expected white
    space. Now, the identifier `luv` and `lchuv` will refer to the D65 version of the respective color spaces. D50
    variants are no longer available by default.
-   **NEW**: Add the HSLuv color space.
-   **NEW**: DIN99o LCh identifier was renamed from `din99o-lch` to `lch99o`. To use in CSS `color()` form, use
    `--lch99o`.
-   **NEW**: Refactor chroma reduction/MINDE logic to cut processing time in half. Gamut mapping results remain very
    similar.
-   **NEW**: Be more strict with CSS inputs and outputs. `hwb()`, `lab()`, `lch()`, `oklab()`, and `oklch()` no longer
    support comma string formats.
-   **NEW**: Officially drop Python 3.6 support.
-   **FIX**: Do not assume user defined, powerless hues as undefined. If they are defined by the user, they should be
    respected, even if they have no effect on the current color. This helps to ensure interpolations acts in an
    unsurprising way. If a user manually specifies the channel with `none`, then it will be considered undefined, or if
    the color goes through a conversion to a space that cannot pick an appropriate hue, they will also be undefined.

## 0.10.0

-   **NEW**: Switch back to using CIELCh for gamut mapping (`lch-chroma`). There are still some edge cases that make
    `oklch-chroma` less desirable.
-   **FIX**: Fix an issue where when attempting to generate steps some ∆E distance apart, the maximum step range was not
    respected and could result in large hangs.

## 0.9.0

/// warning | Breaking Changes
Custom gamut mapping plugins no longer return coordinates and require the method to update the passed in color.
///

-   **NEW**: Improved, faster gamut mapping algorithm.
-   **NEW**: FIT plugins (gamut mapping) no longer return coordinates but should modify the color passed in.
-   **NEW**: Expose default interpolation space as a class variable that can be controlled when creating a custom class
    via class inheritance.
-   **NEW**: Colors can now directly specify the ∆E method that is used when interpolating color steps and using
    `max_delta_e` via the new `delta_e` argument. If the `delta_e` parameter is omitted, the color object's default ∆E
    method will be used.
-   **NEW**: Oklab is now the default interpolation color space.
-   **NEW**: Interpolation will now avoid fitting colors that are out of gamut unless the color space cannot represent
    out of gamut colors. Currently, all of the RGB colors (`srgb`, `display-p3`, etc.) all support extended ranges, but
    the HSL, HWB, and HSV color models for `srgb` (including spaces such as `okhsl` and `okhsv`) do not support extended
    ranges and will still be gamut mapped.
-   **FIX**: Remove some incorrect code from the gamut mapping algorithm that would shortcut the mapping to reduce
    chroma to zero.

## 0.8.0

/// warning | Breaking Changes
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
///

-   **NEW**: Add the official CSS syntax `oklab()` and `oklch()` for the Oklab and OkLCh color spaces respectively.
-   **NEW**: Custom fit plugin's `fit` method now allows additional `kwargs` in its signature. The API will accept
    `kwargs` allowing a custom fit plugin to have configurable parameters. None of the current built-in plugins provide
    additional parameters, but this is provided in case it is found useful in the future.
-   **NEW**: XYZ D65 space will now be known as `xyz-d65`, not `xyz`. Per the CSS specification, we also ensure XYZ D65
    color space serializes as `xyz-d65` instead of the alias `xyz`. CSS input string format will still accept the `xyz`
    identifier as this is defined in the CSS specification as an alias for `xyz-d65`, but when serializing a color to a
    string, the `xyz-d65` will be used as the preferred form.
-   **NEW**: By default, gamut mapping is done with `oklch-chroma` which matches the current CSS specification. If
    desired, the old way (`lch-chroma`) can manually be specified or set as the default by subclassing `Color` and
    setting `FIT` to `lch-chroma`.
-   **FIX**: Ensure the `convert` method's `fit` parameter is typed appropriately and is documented correctly.

## 0.7.0

-   **NEW**: Formally expose `srgb-linear` as a valid color space.
-   **NEW**: Distance plugins and gamut mapping plugins now use `classmethod` instead of `staticmethod`. This allows for
    inheritance from other classes and the overriding of plugin options included as class members.
-   **NEW**: Tweak LCh chroma gamut mapping threshold.
-   **FIX**: Issue where it is possible, when generating steps, to cause a shift in midpoint of colors if exceeding the
    maximum steps. Ensure that no stops are injected if injecting a stop between every color would exceed the max steps.

## 0.6.0

-   **NEW**: Update spaces such that they provide a single conversion point which simplifies color space API and
    centralizes all conversion logic allowing us to pull chromatic adaptation out of spaces.
-   **NEW**: `color()` output format never uses percent when serializing, but will optionally accept percent as input.
-   **NEW**: Slight refactor of color space, delta E, and gamut mapping plugins. All now specify there name via the
    property `NAME` instead of methods `space()` for color spaces and `name()` for other plugins.
-   **NEW**: Restructure source structure by flattening out some directories and better organizing source files. This
    changes some import paths.
-   **NEW**: Color spaces do not specify `alpha` in `CHANNEL_NAMES` as the `alpha` name cannot be changed.
-   **NEW**: Color space objects do not need a constant to track number of color channels.

## 0.5.0

- **NEW**: Add type annotations and refactor code to better accommodate the type annotations. Public API not really
  affected, but a bit of the internals have changed.
- **FIX**: Fix issue where `compose`, if `backdrop` list is empty, would not respect `in_place` option.

## 0.4.0

-   **NEW**: Officially support Python 3.10.
-   **NEW**: Slightly more accurate Oklab matrix calculation.
-   **NEW**: Exported dictionary form can now be used as a normal color input in functions like `contrast`,
    `interpolate`, etc.
-   **NEW**: Color objects will accept a dictionary mapping when `alpha` is not specified. When this occurs, `alpha` is
    assumed to be `1`.
-   **FIX**: Fix an object compare issue.

## 0.3.0

/// warning | Breaking Changes
XYZ changes below will cause breakage as `xyz` now refers to XYZ with D65 instead of D50. Also, CSS identifiers
changed per the recent specification change.
///

-   **NEW**: When calling `dir()` on `Color()`, ensure dynamic methods are in the list.
-   **NEW**: `xyz` now refers to XYZ D65. CSS `#!css-color color()` function now specifies D65 color as either
    `#!css-color color(xyz x y z)` or `#!css-color color(xyz-d65 x y z)`. XYZ D50 is now specified as
    `#!css-color color(xyz-D50 x y z)`.
-   **NEW**: Add CIELuv and CIELCh~uv~ D65 variants.

## 0.2.0

-   **NEW**: Provide dedicated `clip` method. `clip` is still a specifiable method under the `fit` function. It is also
    a reserved name under `fit` and cannot be overridden via plugins or be removed.
-   **NEW**: Add more conversion shortcuts to OK family of color spaces.
-   **FIX**: Fix an issue where the shorter conversion path wasn't always taken as convert couldn't find to/from methods
    if the color space name had `-` in it.

## 0.1.0

First non-alpha prerelease. Notable changes from the last alpha listed below.

/// warning | Breaking Changes
There are some breaking changes if coming from the previous alpha releases. All sRGB cylindrical spaces' non-hue
data ranges are no longer scaled to 0 - 100, but use 0 - 1. Hue ranges have not changed.
///

-   **NEW**: By accepting HSL, HSV, and HWB as non-hue channels as 0-100, we do lose a little precision, so for 1.0, we
    are switching to accepting and returning raw data values between 0 - 1. We've kept hue between 0 - 360 as it is
    easier for users to deal with hues between 0 - 360. Doing this will also match the new color spaces Okhsl and Okhsv
    that need to be kept at 0 - 1 to get better rounding.
-   **NEW**: We do not currently restrict percentages anymore in `#!css-color color()` functions. There is no hard rules
    that we need to at this time and no currently specified spaces that do this in the CSS specification. This is
    relaxed for now until some future time when it becomes clear we must.
-   **NEW**: New `okhsl` and `okhsv` color space.
-   **NEW**: All color channels now accept the `none` keyword to specify an undefined channel. They can also optionally
    output CSS strings with the keyword.
-   **NEW**: Interpolation will return an undefined channel if both colors have that channel set to undefined.
-   **NEW**: Provide a way to dump a color object to a simple dictionary and have the `Color()` object accept that
    dictionary to recreate the color object.
-   **NEW**: Provide `cat16` chromatic adaptation.
-   **NEW**: Add `normalize` method to force channel normalization (evaluation of channels and setting undefined as
    appropriate).
-   **NEW**: Interpolated and composited colors will normalize undefined channels when returning a color.
-   **NEW**: Jzazbz now also has an alias for `az` and `bz` channels as `a` and `b` respectively.
-   **FIX**: Fix an attribute "get" issue where attributes that were not present on the `Color()` object appeared to be
    present when using `hasattr()`.
-   **FIX**: More accurate Oklab matrix.
