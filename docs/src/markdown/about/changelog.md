# Changelog

## 1.7.1

- **FIX**: Ensure CAM16 spaces mirrors positive and negative percentages for `a` and `b` components.
- **FIX**: Since the CAM16 JMh model can not predict achromatic colors with negative lightness and, more importantly,
  negative lightness is not useful, limit the lower end of lightness in CAM16 spaces to zero.
- **FIX**: When a CAM16 JMh (or HCT) color's chroma, when not discounting illuminance, has chroma drop below the actual
  ideal achromatic chroma threshold, just use the ideal chroma to ensure better conversion back to XYZ.
- **FIX**: Jzazbz and JzCzhz model can never translate a color with a negative lightness, so just clamp negative
  lightness while in Jzazbz and JzCzhz.
- **FIX**: Fix a math error in CAM16.
- **FIX**: Fix CAM16 JMh M limit which was too low.
- **FIX**: IPT was set to "bound" when it should have an unbounded gamut.
- **FIX**: When both `comma` and `none` are enabled it could make undefined alpha values show up as `none` in legacy CSS
  format.
- **FIX**: Sane handling of inverse lightness in DIN99o.

## 1.7

- **NEW**: Add support for CAM16 Jab and JMh: `cam16` and `cam16-jmh` respectively.
- **NEW**: Add support for CAM16 UCS (Jab forms): `cam16-ucs`, `cam16-scd`, and `cam16-lcd`.
- **NEW**: Add support for the HCT color space (`hct`) which combines the colorfulness and hue from CAM16 JMh and the
  lightness from CIELab.
- **NEW**: Gamut mapping classes derived from `fit_lch_chroma` can set `DE_OPTIONS` to pass ∆E parameters.
- **NEW**: While rare, some cylindrical color spaces have an algorithm such that achromatic colors convert best with a
  very specific hue. Internally, this is now handled during conversions, but there can be reasons where knowing the hue
  can be useful such as plotting. Cylindrical spaces now expose a method called `achromatic_hue()` which will
  return this specific hue if needed.
- **FIX**: Fix `rec2100-hlg` transform.
- **FIX**: Some color transformation improvements.
- **FIX**: Relax some achromatic detection logic for sRGB cylindrical models. Improves achromatic hue detection results
  when converting to and from various non-sRGB color spaces.

## 1.6

- **NEW**: Add `rec2100-hlg` color space.
- **BREAKING**: `rec2100pq` should have been named `rec2100-pq` for consistency. It has been renamed to `rec2100-pq` and
  serializes with the CSS ID of `--rec2100-pq`. This is likely to have little impact on most users.

## 1.5

- **NEW**: Formally add support for Python 3.11.
- **NEW**: Add support for custom domains when interpolating.
- **NEW**: `set()` can now take a dictionary of channels and values and set multiple channels at once.
- **NEW**: `get()` can now take a list of channels and will return a list of those channel values.
- **ENHANCE**: Simplify some type annotation syntax.
- **ENHANCE**: Some minor performance enhancements.
- **FIX**: Fix OkLCh CSS parsing.

## 1.4

- **NEW**: A color space can now declare its dynamic range. By default, spaces are assumed to be SDR, but can declare
  themselves as HDR, or something else. This allows ColorAide to make decisions based on a color's dynamic range.
- **NEW**: Add channel aliases for IPT and IPT-like color spaces (IgPgTg and ICtCp): `intensity`, `protan`, and
  `tritan`.
- **FIX**: The ICtCp and oRGB space would return the Lab-ish equivalents for `a` and `b` in reverse order if calling
  `Labish.labish_names`. This was not actually called anywhere in the code, but is now fixed for any future cases that
  may require calling it.
- **FIX**: Undefined channels should be ignored when clipping a color.
- **FIX**: Do not apply SDR shortcuts in gamut mapping when fitting in a non-SDR color gamut, such as HDR.

## 1.3

- **ENHANCE**: Color vision deficiency filters can now be instantiated with different default methods for severe and
  anomalous cases.
- **FIX**: Fix premultiplication handling when using `compose`.

## 1.2

- **NEW**: Add new monotone interpolation method.
- **ENHANCE**: Better extrapolation past end of spline.
- **FIX**: Small speed up in natural spline calculation.
- **FIX**: Fix import that should have been relative, not absolute.

## 1.1

- **NEW**: Slight refactor of interpolation plugin so that common code does not need to be duplicated, and the
  `interpolate` method no longer needs to accept an `easing` parameter as the plugin class exposes a new `ease` method
  to automatically acquire the proper, specified easing function and apply it.
- **NEW**: Functions built upon interpolation can now use a new `extrapolate` parameter to enable extrapolation if
  interpolation inputs exceed 0 - 1. `point` will be passed to `Interpolator.interpolate` un-clamped if `extrapolate` is
  enabled. If a particular interpolation plugin needs to do additional work to handle extrapolation, they can check
  `self.extrapolate` to know whether extrapolation is enabled.
- **NEW**: Implement and provide the following easing functions as described in the CSS Easing Level 1 spec:
  `cubic_bezier`, `ease`, `ease_in`, `ease_out`, and `ease_in_out`. Also provide a simple `linear` easing function.
- **New**: Add `natural` and `catrom` cubic spline options for interpolation. The `catrom` (Catmull-Rom) spline requires
  the plugin to be registered in order to use it.
- **FIX**: Due to floating point math, B-spline could sometimes return an interpolation of fully opaque colors with an
  imperceptible amount of transparency. If alpha is very close (`#!py3 1e-6`) to being opaque, just round it to opaque.
- **FIX**: An easing function's output should not be clamped, only the input, and that only **needs** to occur on the
  the outer range of an entire interpolation.

## 1.0

!!! success "Stable Release!"
    Checkout [migration guide](./releases/1.0.md) if you were an early adopter.

- **NEW**: Bezier interpolation dropped for B-spline which provides much better interpolation.
- **NEW**: All new interpolation methods now supports hue fix-ups: `shorter`, `longer`, `increasing`, `decreasing`,
  and `specified`.
- **NEW**: Interpolation is now exposed as a plugin to allow for expansion.
- **FIX**: Fixed an issue related to premultiplication and undefined alpha channels.

## 1.0rc1

!!! warning "Plugin Refactor"
    For more flexibility there was one final rework of plugins. Registering requires all plugins to be instantiated
    before being passed into `Color.register`, but this allows a user redefine some defaults of certain plugins.

    `coloraide.ColorAll` was moved to `coloraide.everythng.ColorAll` to avoid allocating plugins when they are not
    desired.

    In the process, we also renamed a number of plugin classes for consistency and predictability, details found below.

- **NEW**: Updated some class names for consistency and predictability. `XyY` --> `xyY`, `Din99o` --> `DIN99o`, `SRGB`
  --> `sRGB`, and `ORGB` --> `oRGB`.

    Lastly, `LCh` should be the default casing convention. This convention will be followed unless a spec mentions
  otherwise. Changes: `Lch` --> `LCh`, `LchD65` --> `LChD65`, `Oklch` --> `OkLCh`, `Lchuv` --> `LChuv`, `Lch99o` -->
  `LCh99o`, `LchChroma` --> `LChChroma`, `OklchChroma` --> `OkLChChroma`, and `Lchish` --> `LChish`.

- **NEW**: Updated migration guide with recent plugin changes.
- **NEW**: `coloraide.ColorAll` renamed and moved to `coloraide.everything.ColorAll`. This prevents unnecessary
  inclusion and allocation of objects that are not desired.
- **NEW**: Default `Color` object now only registers `bradford` CAT by default, all others must be registered
  separately, or `coloraide.everything.Color` could be used.
- **NEW**: All plugin classes must be instantiated when being registered. This allows some plugins to be instantiated
  with different defaults. This allows some plugins to be configured with different defaults.

    ```py
    # Before change:
    Color.register([Plugin1, Plugin2])

    # After change:
    Color.register([Plugin1(), Plugin2(optional_parm=True)])
    ```

- **FIX**: Negative luminance is now clamped during contrast calculations.

## 1.0b3

- **FIX**: Fixed the bad `CAT16` matrix for chromatic adaptation.
- **FIX**: Small fix related to how `CAT` plugin classes are defined for better abstraction.
- **FIX**: Restrict optional keywords in `Color.register()` and `Color.deregister()` to keyword _only_ parameters.

## 1.0b2

!!! warning "Breaking Changes"
    1.0b2 only introduces one more last breaking change that was forgotten in 1.0b1.

- **BREAK**: Remove `filters` parameter on new class instantiation.
- **NEW**: Added new migration guide to the documentation to help early adopters move to the 1.0 release.
- **NEW**: Added HPLuv space described in the HSLuv spec.
- **NEW**: Added new color spaces: ACES 2065-1, ACEScg, ACEScc, and ACEScct.
- **NEW**: Contrast is now exposed as a plugin to allow for future expansion of approaches. While there is currently
  only one approach, methods can be selected via the `method` attribute.
- **NEW**: Add new `random` method for generating a random color for a given color space.

## 1.0b1

!!! warning "Breaking Changes"
    1.0b1 introduces a number of breaking changes. As we are very close to releasing the first stable release, we've
    taken opportunity to address any issues related to speed and usability. While this is unfortunate for early
    adopters, we feel that in the long run that these changes will make ColorAide a better library. We've also added new
    a new Bezier interpolation method and added many more color spaces!

- **BREAK**: The `coloraide.Color` object now only registers a subset of the available color spaces and ∆E algorithms in
  order to create a lighter default color object. `coloraide.ColorAll` has been provided for a quick way to get access
  to all available color spaces and plugins. Generally, it is recommend to subclass `Color` and register just what is
  desired.

- **BREAK**: Reworked interpolation:

    - `interpolate` and `steps` functions are now `@classmethod`s. This alleviates the awkward handling of interpolating
      colors greater than 2. Before, the first color always had to be an instance and then the rest had to be fed into
      that instance, now the the methods can be called from the base class or an instance with all the colors fed in
      via a list. Only the colors in the list will be evaluated during interpolation.
    - `Piecewise` object has been removed.
    - `stop` objects are used to wrap colors to apply a new color stop.
    - easing functions can be supplied in the middle of two colors via the list input.
    - `hint` function has been provided to simulate CSS color hinting. `hint` returns an easing function that modifies
      the midpoint to the specified point between two color stops.
    - A new bezier interpolation method has been provided. When using `interpolate`, `steps`, or `mix` the interpolation
      style can be changed via the `method` parameter. `bezier` and `linear` are available with `linear` being the
      default.

- **BREAK**: Dictionary input/output now matches the following format (where alpha is optional):

    ```py
    {"space": "name", "coords": [0, 0, 0], "alpha": 1}
    ```

    This allows for quicker processing and less complexity dealing with channel names and aliases.

- **BREAK**: The CSS Level 4 Color spec has accepted our proposed changes to the gamut mapping algorithm. With this
  change, the `oklch-chroma` gamut mapping algorithm is now compliant with the CSS spec, and `css-color-4` is no longer
  needed. If you were experimenting with `css-color-4`, please use `oklch-chroma` instead. The algorithm is faster and
  does not have the color banding issue that `css-color-4` had, and it is now exactly the same as the CSS spec.

- **BREAK**: New breaking change. Refactor of `Space` plugins. `Space` plugins are no longer instantiated which cuts
  down on overhead lending to better performance. `BOUNDS` and `CHANNEL_NAMES` attributes were combined into one
  attribute called `CHANNELS` which serves the same purpose as the former attributes. `Space` plugins also no longer
  need to define channel property accessors as those are handled through `CHANNELS` in a more generic way. This is a
  breaking change for any custom plugins.

    Additionally, the `Space` plugin's `null_adjust` method has been renamed as `normalize` matching its functionality
    and usage in regards to the `Color` object. It no longer accepts color coordinates and alpha channel coordinates
    separately, but will receive them as a single list and return them as such.

- **BREAK**: `Color`'s `fit` and `clip` methods now perform the operation in place, modifying the current color
  directly. The `in_place` parameter has been removed. To create a new color when performing these actions, simply clone
  the color first: `#!py color.clone().clip()`.

- **BREAK**: Remove deprecated dynamic properties which helps to increase speed by removing overhead on class property
  access.

- **BREAK**: Remove deprecated dynamic properties which helps to increase speed by removing overhead on class property
  access. Use indexing instead: `color['red']` or `color[0]`.

- **BREAK**: Remove deprecated `coords()` method. Use indexing and slices instead: `color[:-1]`.

- **NEW**: Update `lch()`, `lab()`, `oklch()`, and `oklab()` to optionally support percentages for lightness, chroma, a,
  and b. Lightness is no longer enforced to be a percentage in the CSS syntax and these spaces will serialize as a
  number by default instead. Optionally, these forms can force a percentage output via the `to_string` method when using
  the `percentage` option. Percent ranges roughly correspond with the Display P3 gamut per the CSS specification.

    Additionally, CSS color spaces using the `color()` format as an input will translate using these same ranges if the
    channels are percentages. `hue` will also be respected and treated as 0 - 360 when using a percentage.

    Non-CSS color spaces will also respect their defined ranges when using percentages in the `color()` form.

- **NEW**: Add `silent` option to `deregister` so that if a proper category is specified, and the plugin does not exit,
  the operation will not throw an error.

- **NEW**: Add new color spaces: `display-p3-linear`, `a98-rgb-linear`, `rec2020-linear`, `prophoto-rgb-linear`, and
  `rec2100pq`, `hsi`, `rlab`, `hunter-lab`, `xyy`, `prismatic`, `orgb`, `cmy`, `cmyk`, `ipt`, and `igpgtg`.

- **NEW**: Monochromatic color harmony must also be performed in a cylindrical color space to make achromatic detection
  easier. This means all color harmonies now must be performed under a cylindrical color space.

- **NEW**: Use Lab D65 for ∆E 2000, ∆E 76, ∆E HyAB, Euclidean distance, and LCh D65 for LCh Chroma gamut mapping. Lab
  D65 is far more commonly used for the aforementioned ∆E methods. LCh Chroma gamut mapping, which uses ∆E 2000 needs to
  use the same D65 white point to avoid wasting conversion time.

- **FIX**: Better handling of monochromatic harmonies that are near white or black.

- **FIX**: Small fix to `steps` ∆E logic.

## 0.18.1

- **FIX**: Fix issue where when generating steps with a `max_delta_e`, the ∆E was reduced too much causing additional,
  unnecessary steps along with longer processing time.

## 0.18.0

- **NEW**: Allow dictionary input to use aliases in the dictionary.
- **FIX**: If too many channels are given to a color space via raw data, ensure the operation fails.
- **FIX**: Sync up achromatic logic of the Okhsl and Okhsv `normalize` function with the actual conversion algorithm.
- **FIX**: Regression that caused `cat16` not to work due to a misnamed variable.

## 0.17.0

!!! warning "Interpolations Are Now Premultiplied"
    ColorAide has moved to make premultiplication the default for interpolation methods such as `mix`, `steps`, and
    `interpolate`. The aim is to provide more accurate interpolation when using transparent colors. In cases where
    premultiplication is not desired, it can be disabled by setting it to `#!py3 False`. There are real reasons to do so
    as it may be desirous to mimic an old implementation that has always used naive interpolation of transparent colors.

    Additionally, in the past, premultiplication was not really documented as it had not been fully tested.
    Premultiplication is now covered in the documentation.

- **NEW**: All mixing/interpolation methods will use `#!py3 premultiply=True` by default.
- **NEW**: Allow aliases in interpolation's progress mappings.
- **FIX**: Fix premultiplication when alpha is undefined.
- **FIX**: Fix some potential issues in some matrix math logic.
- **FIX**: `#!py Piecewise()` object didn't default all the non-required parameters to `#!py None` as documented.

## 0.16.0

!!! warning "Deprecations"
    In interest of speed, and due to the overhead inflicted on every class attribute access, we've decided to deprecate
    dynamic properties. This includes dynamic color properties (e.g. `Color.red`) and dynamic ∆E methods (e.g.
    `Color.delta_e_2000()`). As far as color channel coordinate access is concerned, we've reworked a faster more useful
    approach. ∆E already has a suitable replacement and will be the only approach moving forward.

    1. Use of `delta_e_<method>` is deprecated. Users should use the already available `delta_e(color, method=name)`
       approach when using non-default ∆E methods.

    2. Color channel access has changed. Dynamic channel properties have been deprecated. Usage of `Color.coords()` has
       also been deprecated. All channels can now easily be accessed with indexing. `Color.get()` and `Color.set()`
       have not changed.

        - You can index with numbers: `Color[0]`.
        - You can index with channel names: `Color['red']`.
        - You can slice to get specific color coordinates: `Color[:-1]`.
        - You can get all coordinates: `Color[:]` or `list(Color)`.
        - You can even iterate coordinates: `[c for c in Color]`.
        - Indexing also supports assignment: `Color[0] = 1` or `Color[:3] = [1, 1, 1]`.

    Please consider updating usage to utilize the suggested approaches. The aforementioned methods will be removed
    sometime before the 1.0 release.

- **NEW**: `Color` objects are now indexable and channels can be retrieved using either numbers or strings, e.g.,
  `#!py3 Color[0]` or `#!py3 Color['red']`. Slicing and assignments via slicing are also supported:
  `#!py3 Color1[:] = Color2[:]`.
- **NEW**: `Color.coords()`, dynamic color properties, and dynamic ∆E methods are all deprecated.
- **NEW**: Input method names for distancing, gamut mapping, compositing, and space methods are now case sensitive.
  There were inconsistencies in some places, so it was opted to make all case sensitive.
- **NEW**: The ability to create color harmonies has been added via the new `harmony()` method. Also, the default color
  space used to calculate color harmonies can be overridden by the class property `HARMONY`.
- **NEW**: Add new support for filters added via the `filter()` method. Filters include the W3C Filter Effects Level 1
  and color vision deficiency simulation.
- **NEW**: Some performance enhancements in conversions.
- **NEW**: Chromatic adaptation is now exposed as a plugin. New CAT plugins can be created externally and registered.
- **FIX**: Okhsl and Okhsv handling of achromatic values during conversion.

## 0.15.1

- **FIX**: Fix an issue related to matching colors in a buffer at a given offset.

## 0.15.0

!!! warning
    No changes in the public API have changed, but type annotations have. If you were importing type annotations, you
    will have to update them.

    Also, if any undocumented math related methods were accessed (for plugins or otherwise) they've been moved to
    `coloraide.algebra`

- **NEW**: A number of performance improvements.
- **NEW**: Regenerate all matrices with our own matrix tools so that there is consistency between precision of
  pre-generated matrices and on-the-fly matrix generation. Reduces some noise in a few color space transforms.
- **NEW**: Changes to type annotations. `Mutable<type>`, where type is either `Matrix`, `Vector`, or `Array`, are simply
  known as `<type>`. Types previously specified as `<type>`, where type is either `Matrix`, `Vector`, or `Array`, are
  now known as `<type>Like`. The types are expected to be mutable lists, anything else is noted as "like".
- **NEW**: All matrix and math utilities have been moved to `coloraide.algebra`.
- **FIX**: Fix rare issue where precision adjustment could fail.
- **FIX**: Fix matrix `divide` logic when dividing a number or vector by a matrix. There are no actual usage of these
  cases in the code but they were fixed in case they are used in the future.

## 0.14.1

- **FIX**: Fix bug related to parsing strings without full matching.

## 0.14.0

!!! note
    No changes should break existing color space plugins. Moved objects and references are still also available in old
    locations, and new functionality is implemented in such a way as to not break existing plugins, but plugins should
    be updated as sometime before the 1.0 release, such legacy access will be removed.

- **NEW**: Faster parsing. Instead of parsing `color(space ...)` each time it is evaluated for a different color space,
  parse it generically and then associate it with a given registered color space. If a color spaces wishes to opt out of
  the `color(space ...)` input format, the space should set `COLOR_FORMAT` to `False`. This means there is no need to
  call `super.match()` when overriding `Color.match()` to ensure support for the `color(space ...)` format as it will be
  handled unless `COLOR_FORMAT` is turned off. `DEFAULT_MATCH` usage should also be discontinued as it now does nothing.
- **NEW**: Other speed optimizations.
- **NEW**: All CSS parsing and serialization is now contained in a single module at `coloraide.css`. This simplifies
  the current color space classes greatly when it comes to supporting CSS specific formats.
- **NEW**: Move our white space mapping to the `cat` module as it makes more sense there.
- **NEW**: `GamutBound`, `GamutUnbound`, and associated flags are now contained under `coloraide.gamut.bounds`.
- **NEW**: `normalize` will also remove masked values to properly adjust the color.
- **FIX**: Compositing and blending should not "fit" colors before applying, it is only specified that the range should
  be clamped at the end of blending.
- **FIX**: Fix issue where a subclassed `Color()` object could not recognize the base class or other subclasses.

## 0.13.0

- **NEW**: Add new `closest` method that takes a list of colors and returns the one that is closet to the calling color
  object.
- **NEW**: CSS color syntax no longer allows for forgiving channels in `color()`. This means that when a channel other
  than alpha is omitted, we will no longer treat them as undefined. Instead, the color will simply fail to parse.
  Raw data channels also must specify all channels.
- **NEW**: Clamp lower bounds of chroma at the channel level.
- **NEW**: `coloraide.spaces.WHITES` is now a 2 deep dictionary containing both 2˚ and 10˚ observer variants of white
  points.
- **NEW**: Color space plugins now specify `WHITE` as a tuple with the x and y chromaticity coordinates. This allows a
  space to specify unknown white points if desired.
- **FIX**: Fix `longer` hue interpolation when `θ1 - θ2 = 0`. The spec is wrong in this case, and interpolation should
  still occur the long way around instead of keeping hue constant.
- **FIX**: Reduce redundancy in some CSS parsing patterns.
- **FIX**: Minor performance improvements.
- **FIX**: Legacy `rgb()`, `rgba()`, `hsl()`, and `hsla()` comma separated forms in CSS do not support `none`, only the
  new space separated forms do.
- **FIX**: Ensure `py.typed` is installed with package so that type annotations work properly.

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
    3. The D65 form of Luv and LChuv is now the only supported Luv based color spaces by default now. D50 Luv and LChuv
       have been dropped and `luv` and `lchuv` now refers to the D65 version. In most places, the D65 is the most common
       used white space as most monitors are calibrated for this white point. The only reason CIELab and CIELCh are D50
       by default is that CSS requires it. Anyone interested in using Luv with a different white point can easily
       subclass the current Luv and create a new plugin color space that uses the new white point.
    4. Renamed DIN99o LCh identifier to the short name of `lch99o`.

- **NEW**: ColorAide now only ships with the D65 version Luv and LChuv as D65, in most places is the expected white
  space. Now, the identifier `luv` and `lchuv` will refer to the D65 version of the respective color spaces. D50
  variants are no longer available by default.
- **NEW**: Add the HSLuv color space.
- **NEW**: DIN99o LCh identifier was renamed from `din99o-lch` to `lch99o`. To use in CSS `color()` form, use
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

- **NEW**: Switch back to using CIELCh for gamut mapping (`lch-chroma`). There are still some edge cases that make
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

- **NEW**: Add the official CSS syntax `oklab()` and `oklch()` for the Oklab and OkLCh color spaces respectively.
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
- **NEW**: Tweak LCh chroma gamut mapping threshold.
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
- **NEW**: Add CIELuv and CIELCh~uv~ D65 variants.

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
