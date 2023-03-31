# Color Space

## Description

All color spaces supported by ColorAide are specified via color space plugins. These `Space` objects specify color
channel properties, gamut bounds, input matching/parsing logic, string output logic, conversion to and from a specified
base color, etc.

Color space plugins are a little more complex compared to [Delta E](./delta_e.md), [Fit](./fit.md), and other plugins.

## Plugin Class

In general, a color space plugin is created by subclassing from `#!py3 coloraide.spaces.Space`. When defining a color
space, there are a couple things that must be defined. Using XYZ as an example, we will go over them.

````py
from coloraide import cat
from coloraide.channels import Channel


class XYZD65(Space):
    """XYZ D65 class."""

    # A base color though which a color is converted through.
    # XYZ is our absolute base, so it doesn't have a real base,
    # but something like HSL might have a base color of `srgb`.
    BASE = "xyz-d65"

    # The name of the color space.
    NAME = "xyz-d65"

    # One or more accepted identifiers that are allowed for the `color(space ...)` format.
    # For this this specific color space, both `color(xyz x y z / a)` and `color(xyz-d65 x y z / a)` are accepted.
    # As `xyz` is listed first, `xyz` is the default used when printing in this format.
    SERIALIZE = ("xyz-d65", "xyz")

    # Specify channel attributes, bounds, etc. of the non-alpha color channels.
    # Each channel is defined via a `Channel` object
    #
    #```
    #class Channel(str):
    #    """Channel."""
    #
    #    def __new__(
    #        cls,
    #        name: str,
    #        low: float,
    #        high: float,
    #        bound: bool = False,
    #        flags: int = 0,
    #        limit: Tuple[float | None, float | None] = (None, None),
    #        nans: float = 0.0
    #    ) -> 'Channel':
    #```
    #
    # - `name`: The name of the channel.
    # - `low`: Lower limit of the channel, for unbound channels, the value will be arbitrary.
    # - `high`: Upper limit of the channel, for unbound channels, the value will be arbitrary.
    # - `bound`: Whether the channel enforces the gamut range.
    # - `limit`: Optional upper and lower limit. Used to define a hard limit for the channel that is clamped
    #            when the channel is set. This differs from gamut boundaries which can be exceeded until gamut
    #            mapping occurs. For instance, `chroma` often enforces no values below zero as these values
    #            do not naturally occur, not even with normal out of gamut colors. So, we could clamp the lower
    #            bound: `(0, None)`.
    # - `flags`: Flags used to provide additional context for the channel.
    # - `nans`: Default value to use for a given channel when it is undefined. More advanced handling can be
    #           done by overriding `resolve_channel()` on the color space object.
    #
    # The following flags are supported:
    # - FLG_ANGLE: denotes that channel is a angle or degree value.
    # - FLG_PERCENT: denotes the value is considered a percent input. This is usually used in named CSS functions
    #                like `hsl()` which require string inputs for saturation and lightness to always be in a
    #                percentage format. The CSS `color()` function ignores this flags as no channels are always
    #                required to be percentages. Percentage range will be determined by `high` and `low`.
    # - FLG_OPT_PERCENT: denotes the value can optionally be considered as a percent.
    #                    This is also only used for CSS string input and output. CSS `oklab()`, `lab()`, `oklch()`,
    #                    `lch()`, and `srgb()` allow for channels to be provided as percentages or normal
    #                    numbers in certain cases. This tells the parser and serializer which channels allow this.
    #                    Percentage range will be determined by `high` and `low`.
    # - FLG_MIRROR_PERCENT: The channel, when importing or exporting to a percent should mirror the percentage
    #                       for negative values. This is used mainly in Lab and Lab like spaces which have `a`
    #                       `b` channels that allow for both negative and positive values. If set, `high` and `low`
    #                       should fulfill `abs(low) == high`.
    CHANNELS = (
        Channel("x", 0.0, 1.0),
        Channel("y", 0.0, 1.0),
        Channel("z", 0.0, 1.0)
    )

    # A dictionary containing a mapping of aliases to `name` attribute of `CHANNELS` found above.
    CHANNEL_ALIASES = {}

    # If you'd like this color space to parse as and export a `color(space ...)` format.
    # If set to `False` the space will not recognize the color format as an input.
    # This only affects input matching. To override output of the color format, you will also
    # need to override the `to_string` method.
    COLOR_FORMAT = True

    # Specify the white point that the color space uses
    # White point should be a `tuple` containing the x and y chromaticity points.
    # Some basic ones are provided in the `cat` module for both 2 degree and 10 degree observer.
    WHITE = cat.WHITES['2deg']['D65']

    # If `GAMUT_CHECK` is set to a color space name, the provided color space will be used to verify the an "in gamut"
    # check in addition to the current color space's channel ranges. This is often used with color spaces such as:
    # HSL, HSV, and HWB where `GAMUT_CHECK` will be set to `srgb`.
    #
    # Gamut checking:
    #   The specified color space will be checked first followed by the original. Assuming the parent color space fits,
    #   the original should fit as well, but there are some cases when a parent color space that is slightly out of
    #   gamut, when evaluated with a threshold, may appear to be in gamut enough, but when checking the original color
    #   space, the values can be greatly out of specification (looking at you HSL).
    GAMUT_CHECK = None

    # What is the color space's dynamic range
    DYNAMIC_RANGE = 'sdr'

    ############################
    # To and from conversion functions that transform the color to and from the `BASE` color.
    ############################
    def to_base(self, coords: Vector) -> Vector:
        """
        To XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords

    def from_base(self, coords: Vector) -> Vector:
        """
        From XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords
````

Once registered, colors can be created using the `NAME` via normal instantiation methods or conversions:

```py
Color(NAME, [...])
Color(red).convert(NAME)
```

By default, assuming `COLOR_FORMAT` is `#!py3 True`, color strings will be parsed in the following format, where
`SERIALIZE` is one one of the IDs specified via the `SERIALIZE` plugin property.

```py
Color('color(SERIALIZE ...)')
```

## Plugin Defaults

It is important to note that color space plugins are often not isolated. They are convert to from some `BASE` color
and may be a `BASE` color for some other color space. Essentially, color spaces are chained together via the `BASE`
property to ensure proper conversion to and from the color space. Because of this, it is not advisable to have any
configurable defaults that would fundamentally change how the color coordinates are calculated, as such a change could
affect not only the targeted color space, but other color spaces up and down the color conversion change.

If configuration of a color space's fundamental calculations of coordinates is desired, it is recommended that the
given `Space` plugin gets subclassed and provided a new `NAME`, along with `SERIALIZE` IDs that do not conflict with
other spaces. Such changes would include changing a white point, changing viewing conditions, and even changing the
algorithm for color space conversion.

Defaults can be provided and configured via an `__init__` method, but it is strongly recommended that only superficial
things are controlled by such options, like controlling recognized input/output string formats.

Additionally, if provided an `__init__`, it is required that `super().__init__()` also gets called.

## Chromatic Adaptation

Chromatic adaptation is usually applied to a color when it is passing from one XYZ color space to another XYZ color
space that has a different white point. In ColorAide, any time XYZ D65 is either the target or origin color, and the
other color space has a different white point, the XYZ coordinates, will either be adapted to XYZ D65 or XYZ (new white
point) respectively. This all happens without The `Space` plugin needing to do anything additional.

White points are specified via the `WHITE` property, and should contain a tuple of `xy` coordinates of the white point.

## Achromatic Rules

A given color space can define its rules for determining whether a color is achromatic. If one is not defined, the
color will be convert to XYZ D65 and its achromatic method will be used. In order to have reasonably fast checks, it is
better to evaluate the achromatic state without converting to another color. In order to define achromatic rules, simply
override `is_achromatic()`. For instance, LCh is achromatic when chroma is very close to zero:

```py
    def is_achromatic(self, coords: Vector) -> bool | None:
        """Check if color is achromatic."""

        return coords[1] < ACHROMATIC_THRESHOLD
```

## Resolve Undefined Values

By default, undefined color channels are resolved as `0`, but there are color spaces where zero just does not work well
for a given channel. Such color spaces can choose a different default for undefined values. Generally, `0` is
encouraged, but if zero is fundamentally a bad value for a color space and/or can decrease accuracy of colors, a
different default can be specified when defining a channel on the color space via the `nans` parameter.

```py
class ACEScct(sRGB):
    """The ACEScct color class."""

    BASE = "acescg"
    NAME = "acescct"
    SERIALIZE = ("--acescct",)
    WHITE = (0.32168, 0.33767)
    CHANNELS = (
        Channel("r", CCT_MIN, CCT_MAX, bound=True, nans=CCT_MIN),
        Channel("g", CCT_MIN, CCT_MAX, bound=True, nans=CCT_MIN),
        Channel("b", CCT_MIN, CCT_MAX, bound=True, nans=CCT_MIN)
    )
```

If the channel requires more advanced handling, you can override `resolve_channel()` on the color space itself:

```py
    def resolve_channel(self, index: int, coords: Vector) -> float:
        """Resove channels."""

        if index in (1, 2):
            if not math.isnan(coords[index]):
                return coords[index]

            return self.ACHROMATIC.get_ideal_ab(coords[0])[index - 1]

        value = coords[index]
        return self.channels[index].nans if math.isnan(value) else value
```

## Mix-ins

ColorAide provides some various mixins for some common color space types. It should be noted that all cylindrical type
color mixins are derived from `Cylindrical`.

/// tab | Cylindrical
```py
class Cylindrical:
    """Cylindrical space."""

    def hue_name(self) -> str:
        """Hue channel name."""

        return "h"

    def hue_index(self) -> int:
        """Get hue index."""

        return cast('Space', self).get_channel_index(self.hue_name())
```
///

/// tab | RGBish
```py
class RGBish:
    """RGB-ish space."""

    def names(self) -> tuple[str, ...]:
        """Return RGB-ish names in order R G B."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of RGB-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]
```
///


/// tab | HSLish
```py
class HSLish(Cylindrical):
    """HSL-ish space."""

    def names(self) -> tuple[str, ...]:
        """Return HSL-ish names in order H S L."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of HSL-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]
```
///

/// tab | HSVish
```py
class HSVish(Cylindrical):
    """HSV-ish space."""

    def names(self) -> tuple[str, ...]:
        """Return HSV-ish names in order H S V."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of HSV-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]
```
///

/// tab | Labish
```py
class Labish:
    """Lab-ish color spaces."""

    def names(self) -> tuple[str, ...]:
        """Return Lab-ish names in the order L a b."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of the Lab-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]
```
///

/// tab | LChish
```py
class LChish(Cylindrical):
    """LCh-ish color spaces."""

    def names(self) -> tuple[str, ...]:
        """Return LCh-ish names in the order L c h."""

        return self.channels[:-1]

    def indexes(self) -> list[int]:
        """Return the index of the Lab-ish channels."""

        return [self.get_channel_index(name) for name in self.names()]
```
///

Mix-in classes are mainly available so that a color space can be inspected to see if it falls into a specific generic
color space type in order to allow for some generic handling of the color. For instance, you may not care specifically
what color space you are dealing with, but you may want to extract the hue from all cylindrical spaces, or grab the
lightness (or lightness equivalent) from all Lab-ish color spaces.

The mix-in classes provide methods mainly to extract expected channels on color spaces that may use different names for
similar channels or to determine the index of a specific channel type. Occasionally, these methods may need to be
overridden for a color space.

Below, we can see that both `jzazbz` and `ictcp` identify as Lab-ish spaces. If we just care about accessing the
equivalent of Lab lightness on these spaces, we can simply can access them with the following logic.

```py play
from coloraide.spaces import Labish
srgb = Color('red')
jzazbz = srgb.convert('jzazbz')
ictcp = srgb.convert('ictcp')

for c in (srgb, jzazbz, ictcp):
    if isinstance(c._space, Labish):
        print('color: ', c)
        l = c._space.names()[0]
        print('channel: ', l)
        print('value: ', c.get(l))
```

## Adding New Input/Output Formats

One common thing that may be desired is altering an existing color space to accept and output a specialized format.
While using hex color codes or `#!css-color rgb()` formats are fairly common, there are many places were other forms
are used to represent colors. It may be beneficial for a user working with colors in some more obscure form to repurpose
a color space to handle different input/output formats.

The base of every color space is defined to accept and output the `#!css-color color(space ...)` format. As this is a
common input form across all color spaces, it is handled generically for all spaces in one action for performance
reasons. Iterating each color space to perform the same match with a different color spaces name is obviously slower.
A color can opt out of this input format by simply setting `COLOR_FORMAT` to `#!py3 False`. This only disables input
parsing. In order to disable this format during serialization the color space's `#py3 to_string()` method would need to
be overridden.

New, per color space matching logic can be achieved by simply by overriding the `#!py3 match()` method. If it is desired
to also accept the `#!css-color color(space ...)` format, just keep the `COLOR_FORMAT` flag enabled; otherwise, disable
it.

As an example, let's consider the default sRGB space. We wanted to add additional CSS formats in addition to the
`#!css-color color(space ...)` format. While we won't go into the specific parsing logic, the general top-level logic
can be seen below.

We simply override the `#!py3 match()` method and call into our CSS parser. The parser will handle the appropriate
syntax for our color spaces. It is not configured to process the `#!css-color color(space ...)` format as that is
already handled more efficiently when with `COLOR_FORMAT` enabled. Also, notice that `#!py3 match()` is expected to
return two things: a tuple containing the color channel coordinates and the alpha value, and the end position
(`#!py3 ([r, g, b], a), end`). If the match fails, it simply returns `#!py3 None`.


```py
from coloraide.spaces import srgb as base
from coloraide.css import parse


class sRGB(base.sRGB):
    """sRGB class."""

    # This color class should opt into the generic `color(space ...)` input format.
    # This is `True` by default, but shown for demonstration purposes.
    COLOR_FORMAT: True

    # If the color format above is not found, continue with our custom match to handle all other formats.
    def match(
        self,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> Tuple[Tuple[Vector, float], int] | None:
        """Match a CSS color string."""

        return parse.parse_css(self, string, start, fullmatch)
```

Additionally, we control the output formats by overriding the `#!py3 to_string()` function. We ensure that it accepts
all the parameters we need, in our case we accept the common parameters and later check for our special inputs in
`kwargs`.


```py
    def to_string(
        self,
        parent: 'Color',
        *,
        alpha: bool | None = None,
        precision: int | None = None,
        fit: Union[bool, str] = True,
        none: bool = False,
        color: bool = False,
        hex: bool = False,
        names: bool = False,
        comma: bool = False,
        upper: bool = False,
        percent: bool = False,
        compress: bool = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS."""

        return serialize.serialize_css(
            parent,
            func='rgb',
            alpha=alpha,
            precision=precision,
            fit=fit,
            none=none,
            color=color,
            hexa=hex,
            name=names,
            legacy=comma,
            upper=upper,
            percent=percent,
            compress=compress,
            scale=255
        )
```

As all ColorAide color spaces are defined as plugins, there should be ample examples to help someone start writing a new
color space.
