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
color and `sample` is the secondary provided color: `#!py3 Color('color').delta_e('sample', method='NAME')`. The return
value should be a float indicating the distance.

Additional plugin specific options can be provided via new keyword arguments.

## Fit/Gamut Mapping

Fit plugins (or gamut mapping plugins) allow for mapping an out of gamut color to be within the current color space's
gamut. All default gamut mapping methods provided by ColorAide are provided via plugins.

### Plugin Class

Plugins are are created by suclassing `#!py3 coloraide.gamut.Fit`.

```py
class Fit(ABCMeta):
    """Fit plugin class."""

    NAME = ''

    @classmethod
    @abstractmethod
    def fit(cls, color: 'Color', **kwargs) -> MutableVector:
        """Get coordinates of the new gamut mapped color."""
```

The plugin should provide a unique `NAME` and the fitting/mapping logic under `#!py3 fit()`. The return should be a list
of coordinates for the provided color object's space.

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
    eventually to XYZ D65. Non D65 XYZ color spaces should all have `xyz-d65` as their base. Chromatic adaptation should
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
determines when a `hue` is undefined. At key points, the function `null_adjust` is executed to normalize the channels
and set `hue` to an undefined value when appropriate. In the case of such color spaces, it may be necessary to define
`null_adjust` as well. Below is an example from HSL that sets `hue` to undefined when `saturation` is `#!py3 0`.

```py
    @classmethod
    def null_adjust(cls, coords: MutableVector, alpha: float) -> Tuple[MutableVector, float]:
        """On color update."""

        if coords[1] == 0:
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

Mix-in classes are mainly available so that a color space can be inspected to see if it falls into a specific type of
generic color space type to allow for some generic handling of the color. For instance, you may not care specifically
what color space you are dealing with, but you may want to extract the hue from all cylindrical spaces, or grab the
lightness (or lightness equivalent) from all Lab-ish color spaces. The mix-in classes provide methods mainly to extract
expected channels on color spaces that may use different names for similar channels in the specified generic category
or determine the index of a specific channel types. Occasionally, these methods may need to be overridden for a color
space.

Below, we can see that both `jzazbz` identify as Lab-ish spaces. If we just care about accessing the equivalent of Lab
lightness on these spaces, we can simply can generically access them with the following logic.

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

By default, all color spaces are defined using the generic `#!css-color color(space ...)` format. The `DEFAULT_MATCH` is
specifically used so that a color can retain this match behavior and specify additional matching via `MATCH`.

`MATCH` can be used to define an assortment of color match formats. Simply define a compiled regular expression pattern
for `MATCH` and add your logic to the `#!py3 match()` method. If it is desired to also allow
`#!css-color color(space ...)` matching, you can call the base match with `#!py3 super().match()`.

For instance, let's consider the default sRGB space. Out of the box, ColorAide provides CSS input formats such as hex
color codes, named colors, and `#!css-color rgb()` formats in addition to the default `#!css-color color(space ...)`
format. To do this, it simply provides the additional input formats as a regular expression pattern assigned to `MATCH`
and overrides `match()`.  As we still support the `#!css-color color(space ...)` input, we also call into the base
space's `#!py3 match()`.

While we won't go into the specific parsing logic, the general top-level logic can be seen below. Notice that a number
of useful pattern expressions are found in `#!py3 coloraide.parse` which we reuse in our CSS pattern via
`#!py3 parse.COLOR_PARTS`. Also, notice that `#!py3 match()` is expected to return two things: a tuple containing the
color channel coordinates and alpha and the end position (`#!py3 ([r, g, b], a), end`). If the match fails, it simply
returns `#!py3 None`.


```py
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
    ) -> Optional[Tuple[Tuple[MutableVector, float], Optional[int]]]:
        """Match a CSS color string."""

        channels, end = super().match(string, start, fullmatch)
        if channels is not None:
            return channels, end
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

Additional output formats are specified by overriding the `#!py3 to_string()` function. We ensure that it accepts all
the default parameters (though we do not have to use them if a specific output format does not require them) and specify
any additional keyword arguments to enable our new formats.

Just like with inputs, we call the base `#!py3 to_string()` method if we wish to output the
`#!css-color color(space ...)` format or we can omit it.

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

        options = kwargs
        if options.get("color"):
            return super().to_string(parent, alpha=alpha, precision=precision, fit=fit, none=none, **kwargs)

        a = util.no_nan(self.alpha) if not none else self.alpha
        alpha = alpha is not False and (alpha is True or a < 1.0 or util.is_nan(a))
        compress = options.get("compress", False)

        # Handle hex and color names
        value = ''
        if options.get("hex") or options.get("names"):
            h = self._get_hex(parent, upper=options.get("upper", False), alpha=alpha, fit=fit)
            if options.get("hex"):
                value = h
                if compress:
                    m = RE_COMPRESS.match(value)
                    if m:
                        value = m.expand(r"#\1\2\3\4") if alpha else m.expand(r"#\1\2\3")
            if options.get("names"):
                length = len(h) - 1
                index = int(length / 4)
                if length in (8, 4) and h[-index:].lower() == ("f" * index):
                    h = h[:-index]
                n = color_names.hex2name(h)
                if n is not None:
                    value = n

        # Handle normal RGB function format.
        if not value:
            percent = options.get("percent", False)
            comma = options.get("comma", False)
            factor = 100.0 if percent else 255.0

            method = None if not isinstance(fit, str) else fit
            coords = parent.fit(method=method).coords() if fit else self.coords()
            if not none:
                coords = util.no_nans(coords)

            fmt = util.fmt_percent if percent else util.fmt_float
            if alpha:
                template = "rgba({}, {}, {}, {})" if comma else "rgb({} {} {} / {})"
                value = template.format(
                    fmt(coords[0] * factor, precision),
                    fmt(coords[1] * factor, precision),
                    fmt(coords[2] * factor, precision),
                    util.fmt_float(a, max(util.DEF_PREC, precision))
                )
            else:
                template = "rgb({}, {}, {})" if comma else "rgb({} {} {})"
                value = template.format(
                    fmt(coords[0] * factor, precision),
                    fmt(coords[1] * factor, precision),
                    fmt(coords[2] * factor, precision),
                )

        return value
```

As all ColorAide color spaces are defined as plugins, there should be ample examples to help someone start writing a new
color space.
