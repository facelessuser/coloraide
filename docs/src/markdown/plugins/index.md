# ColorAide Plugins

ColorAide implements extendable portions of the `Color` object as plugins. This makes adding things such as new ∆E
methods or even new color spaces quite easy. Currently, ColorAide implements the following areas as plugins:

- [∆E methods](#delta-e)
- [Gamut mapping](#fitgamut-mapping)
- [Color spaces](#color-spaces)

## Delta E

∆E plugins allow for getting color differences with different methods. ColorAide provides a number of methods by default
which are documented under [Color Distance and Delta E](../distance.md). All of the default ∆E methods are provided as
plugins, and users can create their own as well.

### Plugin Class

∆E plugins are subclassed from `#!py3 coloraide.distance.DeltaE`.

```py
class DeltaE(ABCMeta):
    """Delta E plugin class."""

    NAME = ''

    @classmethod
    @abstractmethod
    def distance(cls, color: 'Color', sample: 'Color', **kwargs: Any) -> float:
        """Get distance between color and sample."""
```

The plugin should provide a unique `NAME` and the distancing logic under `#!py3 distance()` where `color` is the current
color and `sample` is the secondary, provided color: `#!py3 Color('color').delta_e('sample', method='NAME')`. The return
value should be a float indicating the distance.

Additional plugin specific options can be provided via new keyword arguments.

## Fit/Gamut Mapping

Fit plugins (or gamut mapping plugins) allow for mapping an out of gamut color to be within the current color space's
gamut. All default gamut mapping methods provided by ColorAide are provided via plugins.

### Plugin Class

Plugins are are created by subclassing `#!py3 coloraide.gamut.Fit`.

```py
class Fit(ABCMeta):
    """Fit plugin class."""

    NAME = ''

    @classmethod
    @abstractmethod
    def fit(cls, color: 'Color', **kwargs) -> None:
        """Get coordinates of the new gamut mapped color."""
```

The plugin should provide a unique `NAME` and the fitting/mapping logic under `#!py3 fit()`. The method does not return
anything and should modify the `color` directly to be in gamut.

!!! warning "Reserved Name"
    `clip` is a special, reserved name and the associated plugin cannot be overridden. Another clip plugin can be
    written, but it cannot override the original.

## Color Space

All color spaces supported by ColorAide are specified via color space plugins. These `Space` objects specify color
channel properties, gamut bounds, input matching/parsing logic, string output logic, conversion to and from a specified
base color, etc.

Color space plugins are a little more complex compared to [Delta E](#delta-e) and [Fit](#fitgamut-mapping) plugins.

### Plugin Class

In general, a color space plugin is created by subclassing from `#!py3 coloraide.spaces.Space`. When defining a color
space, there are a couple things that must be defined. Using XYZ as an example, we will go over them.

!!! tip "Chromatic Adaptation"
    Color spaces do **not** perform chromatic adaptation. That is handled by the `Color` object. Color spaces should
    never change the white point, but simply provide the appropriate `BASE` linkage so that the color can resolve
    eventually to XYZ D65. Other XYZ color spaces should all have `xyz-d65` as their base. Chromatic adaptation should
    automatically occur on transitions between two XYZ spaces with different white points white points, e.g., `xyz-d65`
    to `xyz-d50`.

```py
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

    # Channel names for non-alpha channels listed in order of how they are stored.
    CHANNEL_NAMES = ("x", "y", "z")

    # A dictionary containing a mapping of aliases to `CHANNEL_NAMES` found above.
    CHANNEL_ALIASES = {}

    # `DEFAULT_MATCH` is the pattern for matching colors in the `color(space ...)` format.
    # Simply import `RE_DEFAULT_MATCH` from `color.spaces` and join all serialized names with `|`
    # and specify how many color channels to accept.
    DEFAULT_MATCH = re.compile(RE_DEFAULT_MATCH.format(color_space='|'.join(SERIALIZE), channels=3))

    # Specify the white point that the color space uses
    WHITE = "D65"

    # Specify the bounds of the non-alpha color channels.
    # Each channel is specified with either a `GamutBound` or `GamutUnbound` object.
    # "Bound" channels can be out of gamut and the actual minimum and maximum values
    # have significant. "Unbound" channels have values that are more informational purposes
    # and may be suggested ranges.
    #
    # Flags can also be provided: GamutBound(0.0, 360.0, FLG_ANGLE).
    # - FLG_ANGLE: denotes that channel is a angle or degree value.
    # - FLG_PERCENT: denotes the value is considered a percent.
    #                Channels with this expect the value to be between 0 - 100
    # - FLG_OPT_PERCENT: denotes the value can optionally be considered as a percent.
    #                    Channels with this are expected to be between 0 - 1.
    #
    # NOTE: Behavior of percent flags may change depending on how CSS Level 4 plans to handle non rectangular
    #       colors in the `color(space ...)` format (if they handle them at all).
    BOUNDS = (
        GamutUnbound(0.0, 1.0),
        GamutUnbound(0.0, 1.0),
        GamutUnbound(0.0, 1.0)
    )

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
    # When set to `True`, this denotes that the color space has the ability to represent out of gamut in colors in an
    # extended range. When interpolation is done, if colors are interpolated in a smaller gamut than the colors being
    # interpolated, the colors will usually be gamut mapped, but if the interpolation space happens to support extended
    # ranges, then the colors will not be gamut mapped even if their gamut is larger than the target interpolation
    # space.
    EXTENDED_RANGE = False

    ############################
    # Getters and setters for non-alpha properties
    ############################
    @property
    def x(self) -> float:
        """X channel."""

        return self._coords[0]

    @x.setter
    def x(self, value: float) -> None:
        """Shift the X."""

        self._coords[0] = self._handle_input(value)

    @property
    def y(self) -> float:
        """Y channel."""

        return self._coords[1]

    @y.setter
    def y(self, value: float) -> None:
        """Set Y."""

        self._coords[1] = self._handle_input(value)

    @property
    def z(self) -> float:
        """Z channel."""

        return self._coords[2]

    @z.setter
    def z(self, value: float) -> None:
        """Set Z channel."""

        self._coords[2] = self._handle_input(value)

    ############################
    # To and from conversion functions that transform the color to and from the `BASE` color.
    ############################
    @classmethod
    def to_base(cls, coords: MutableVector) -> MutableVector:
        """
        To XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords

    @classmethod
    def from_base(cls, coords: MutableVector) -> MutableVector:
        """
        From XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords
```

In addition to the above methods, some color spaces, such as cylindrical spaces, have some additional logic that
determines when a `hue` is undefined. This function provides access to this logic in case `normalize` is called from the
the `Color` object. In the case of such color spaces, it may be necessary to define
`null_adjust` as well. Below is an example from HSL that sets `hue` to undefined when `saturation` is `#!py3 0` or
`lightness` is equal to `#!py3 0` or `#!py3 1`.

```py
    @classmethod
    def null_adjust(cls, coords: MutableVector, alpha: float) -> Tuple[MutableVector, float]:
        """On color update."""

        if coords[1] == 0 or coords[2] in (0, 1):
            coords[0] = util.NaN

        return coords, alpha
```

### Mix-ins

If the color is a cylindrical space, Lab-ish space, or Lch-ish space, you can additionally add in the respective
mix-in class: `Cylindrical`, `Labish`, or `Lchish`. It should be noted that `Lchish` is subclassed from `Cylindrical`.

=== "Cylindrical"

    ```py
    class Cylindrical:
        """Cylindrical space."""

        @classmethod
        def hue_name(cls) -> str:
            """Hue channel name."""

            return "h"

        @classmethod
        def hue_index(cls) -> int:
            """Get hue index."""

            return cast(Type['Space'], cls).CHANNEL_NAMES.index(cls.hue_name())
    ```

=== "Labish"

    ```py
    class Labish:
        """Lab-ish color spaces."""

        @classmethod
        def labish_names(cls) -> Tuple[str, ...]:
            """Return Lab-ish names in the order L a b."""

            return cast(Type['Space'], cls).CHANNEL_NAMES[:3]

        @classmethod
        def labish_indexes(cls) -> List[int]:
            """Return the index of the Lab-ish channels."""

            names = cls.labish_names()
            return [cast(Type['Space'], cls).CHANNEL_NAMES.index(name) for name in names]
    ```

=== "Lchish"

    ```py
    class Lchish(Cylindrical):
        """Lch-ish color spaces."""

        @classmethod
        def lchish_names(cls) -> Tuple[str, ...]:
            """Return Lch-ish names in the order L c h."""

            return cast(Type['Space'], cls).CHANNEL_NAMES[:3]

        @classmethod
        def lchish_indexes(cls) -> List[int]:
            """Return the index of the Lab-ish channels."""

            names = cls.lchish_names()
            return [cast(Type['Space'], cls).CHANNEL_NAMES.index(name) for name in names]
    ```

Mix-in classes are mainly available so that a color space can be inspected to see if it falls into a specific generic
color space type in order to allow for some generic handling of the color. For instance, you may not care specifically
what color space you are dealing with, but you may want to extract the hue from all cylindrical spaces, or grab the
lightness (or lightness equivalent) from all Lab-ish color spaces.

The mix-in classes provide methods mainly to extract expected channels on color spaces that may use different names for
similar channels or to determine the index of a specific channel type. Occasionally, these methods may need to be
overridden for a color space.

Below, we can see that both `jzazbz` and `ictcp` identify as Lab-ish spaces. If we just care about accessing the
equivalent of Lab lightness on these spaces, we can simply can access them with the following logic.

```playground
from coloraide.spaces import Labish
srgb = Color('red')
jzazbz = srgb.convert('jzazbz')
ictcp = srgb.convert('ictcp')

for c in (srgb, jzazbz, ictcp):
    if isinstance(c._space, Labish):
        print('color: ', c)
        l = c._space.labish_names()[0]
        print('channel: ', l)
        print('value: ', c.get(l))
```

It should be noted that just because a color space identifies in a specific, generic category, it doesn't mean it is
precisely that thing. For instance, the color space CIELAB is clearly a Lab-ish space, or more precisely, it is a Lab
color space. Oklab, DIN99o, and others are very much Lab spaces as well. ICtCp, on the other hand, is very Lab *like* as
its `Ct` and `Cp` channels control redness/greenness and blueness/yellowness, but the `I` channel represents intensity,
not lightness which is similar but not precisely the same thing.

### Adding New Input/Output Formats

One common thing that may be desired is altering an existing color space to accept and output a specialized format.
While using hex color codes or `#!css-color rgb()` formats are fairly common, there are many places were other forms
are used to represent colors. It may be beneficial to a user working with colors in some more obscure form to repurpose
a color space to handle different input/output formats.

The base of every color space is defined to accept and output the `#!css-color color(space ...)` format. To add
additional CSS forms on top, we usually subclass the base and override the `#!py3 match()` and `#!py3 to_string()`,
calling into `#!py3 super().match()` and `#!py3 super().to_string()` only when we'd like to match or output this the
`#!css-color color(space ...)` format.

For instance, let's consider the default sRGB space, which can be used as an example on how to create a specialized,
non-CSS sRGB input/output. While we won't go into the specific parsing logic, the general top-level logic can be seen
below.

We opt to use a regular expression pattern to match the `rgb()`, hex color codes, and color name formats. We then
override `#!py3 match()` and call into the base match function to try and find the `#!css-color color(space ...)`
format. If we don't get a match, we run our own custom parsing logic. Also, notice that `#!py3 match()` is expected to
return two things: a tuple containing the color channel coordinates and alpha and the end position
(`#!py3 ([r, g, b], a), end`). If the match fails, it simply returns `#!py3 None`.


```py
from .. import srgb as base


class SRGB(base.SRGB):
    """SRGB class."""

    MATCH = re.compile(r'''(?xi)
        (?:
            # RGB syntax
            \brgba?\(\s*
            (?:
                # Space separated format
                (?:
                    # Float form
                    (?:{float}{space}){{2}}{float} |
                    # Percent form
                    (?:{percent}{space}){{2}}{percent}
                )({slash}(?:{percent}|{float}))? |
                # Comma separated format
                (?:
                    # Float form
                    (?:{float}{comma}){{2}}{float} |
                    # Percent form
                    (?:{percent}{comma}){{2}}{percent}
                )({comma}(?:{percent}|{float}))?
            )
            \s*\) |
            # Hex syntax
            \#(?:{hex}{{6}}(?:{hex}{{2}})?|{hex}{{3}}(?:{hex})?)\b |
            # Names
            \b(?<!\#)[a-z]{{3,}}(?!\()\b
        )
        '''.format(**parse.COLOR_PARTS))

    @classmethod
    def match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> Optional[Tuple[Tuple[MutableVector, float], int]]:
        """Match a CSS color string."""

        # Handle default `color(space...)` support
        match = super().match(string, start, fullmatch)
        if match is not None:
            return match

        # Handle `rgb(a)`, hex, and color names
        m = cls.MATCH.match(string, start)
        if m is not None and (not fullmatch or m.end(0) == len(string)):
            string = string[m.start(0):m.end(0)].lower()
            if not string.startswith(('#', 'rgb')):
                value = color_names.name2hex(string)
                if value is not None:
                    return cls.split_channels(value), m.end(0)
            else:
                return cls.split_channels(string), m.end(0)

        return None
```

Additionally, we control the output formats by overriding the `#!py3 to_string()` function. We ensure that it accepts
all the parameters we need, in our case we accept the common parameters and later check for our special inputs in
`kwargs`.

Just like with inputs, we call the base `#!py3 to_string()` method if we wish to output the
`#!css-color color(space ...)` format and then continue on with our own logic.

```py
    def to_string(
        self,
        parent: 'Color',
        *,
        alpha: Optional[bool] = None,
        precision: Optional[int] = None,
        fit: Union[bool, str] = True,
        none: bool = False,
        **kwargs: Any
    ) -> str:
        """Convert to CSS."""

        if precision is None:
            precision = parent.PRECISION

        # Handle default `color(space...)` format.
        options = kwargs
        if options.get("color"):
            return super().to_string(parent, alpha=alpha, precision=precision, fit=fit, none=none, **kwargs)

        # Additional logic here
        ...

        return value
```

As all ColorAide color spaces are defined as plugins, there should be ample examples to help someone start writing a new
color space.
