# ColorAide Plugins

ColorAide implements extendable portions of the `Color` object as plugins. This makes adding things such as new ∆E
methods or even new color spaces quite easy. Currently, ColorAide implements the following areas as plugins:

- [∆E methods](#delta-e)
- [Gamut mapping](#fitgamut-mapping)
- [Chromatic adaptation](#chromatic-adaptation)
- [Color spaces](#color-spaces)

## Delta E

∆E plugins allow for getting color differences with different methods. ColorAide provides a number of methods by default
which are documented under [Color Distance and Delta E](../distance.md). All of the default ∆E methods are provided as
plugins, and users can create their own as well.

### Plugin Class

∆E plugins are subclassed from `#!py3 coloraide.distance.DeltaE`.

```py
class DeltaE(Plugin, metaclass=ABCMeta):
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
class Fit(Plugin, metaclass=ABCMeta):
    """Fit plugin class."""
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

## Chromatic Adaptation

CAT plugins chromatically adapt a given XYZ coordinate from its current reference white point to a new desired white
point. This is useful during conversion when one color space is converted to another color space that uses a difference
reference white.

### Plugin Class

Plugins are are created by subclassing `#!py3 coloraide.cat.CAT`.

```py
class CAT(Plugin, metaclass=ABCMeta):
    """Chromatic adaptation."""

    NAME = ""

    @classmethod
    @abstractmethod
    def adapt(cls, w1: Tuple[float, float], w2: Tuple[float, float], xyz: VectorLike) -> Vector:
        """Adapt a given XYZ color using the provided white points."""
```

The plugin should provide a `NAME` with the adaptation logic under `#!py3 adapt()`.

Currently, ColorAide only ships with Von Kries based adaptation methods. If it is desired to create a Von Kries based
plugin, it is recommended to subclass the `VonKries` class which is based on `CAT`. When subclassing a `VonKries` based
cat, `NAME` and a `MATRIX` must be provided. The inverted matrix will be automatically calculated based on the white
points.

```py
class Bradford(VonKries):
    """
    Bradford CAT.

    http://brucelindbloom.com/Eqn_ChromAdapt.html
    https://hrcak.srce.hr/file/95370
    """

    NAME = "bradford"

    MATRIX = [
        [0.8951000, 0.2664000, -0.1614000],
        [-0.7502000, 1.7135000, 0.0367000],
        [0.0389000, -0.0685000, 1.0296000]
    ]
```

## Filters

Filter plugins allow you to apply a filter to a given color.

### Plugin Class

```py
class Filter(Plugin, metaclass=ABCMeta):
    """Filter plugin."""

    NAME = ""
    DEFAULT_SPACE = 'srgb-linear'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    @classmethod
    @abstractmethod
    def filter(color: 'Color', amount: Optional[float], **kwargs: Any) -> None:
        """Filter the given color."""
```

The plugin should provide a `NAME` with the filter logic under `filter`. The provided color will be modified directly.

A suitable `DEFAULT_SPACE` should also be provided. Additionally, `ALLOWED_SPACES` should be set with a finite number of
specific color spaces in which manipulation is allowed.

A plugin may accept `kwargs` for additional parameters.

All of ColorAide's default filters use the sRGB Linear color space as their default. It is usually better to manipulate
colors in a non-gamma encoded color space such as sRGB Linear, but their may be some existing filters out their
specifically designed for other color spaces such as the gamma encoded sRGB space. The provided W3C Filter Effects that
ship with ColorAide also support sRGB as the specification allows them for legacy purposes.

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
from coloraide import cat
from coloraide.gamut import bounds


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

    # If you'd like this color space to parse as a `color(space ...)` format.
    # If set to `False` the space will not recognize the color format as an input.
    # To override output of the color format, you will also need to override the `to_string` method.
    COLOR_FORMAT = True

    # Specify the white point that the color space uses
    # White point should be a `tuple` containing the x and y chromaticity points.
    WHITE = cat.WHITES['2deg']['D65']

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
        bounds.GamutUnbound(0.0, 1.0),
        bounds.GamutUnbound(0.0, 1.0),
        bounds.GamutUnbound(0.0, 1.0)
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
    def to_base(cls, coords: Vector) -> Vector:
        """
        To XYZ (no change).

        Any needed chromatic adaptation is handled in the parent Color object.
        """

        return coords

    @classmethod
    def from_base(cls, coords: Vector) -> Vector:
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
    def null_adjust(cls, coords: Vector, alpha: float) -> Tuple[Vector, float]:
        """On color update."""

        coords = util.no_nans(coords)
        if coords[1] == 0 or coords[2] in (0, 1):
            coords[0] = util.NaN

        return coords, util.no_nan(alpha)
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


class SRGB(base.SRGB):
    """SRGB class."""

    # This color class should opt into the generic `color(space ...)` format.
    # This is `True` by default, but shown for demonstration purposes.
    COLOR_FORMAT: True

    @classmethod
    def match(
        cls,
        string: str,
        start: int = 0,
        fullmatch: bool = True
    ) -> Optional[Tuple[Tuple[Vector, float], int]]:
        """Match a CSS color string."""

        return parse.parse_css(cls, string, start, fullmatch)
```

Additionally, we control the output formats by overriding the `#!py3 to_string()` function. We ensure that it accepts
all the parameters we need, in our case we accept the common parameters and later check for our special inputs in
`kwargs`.


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

        return serialize.serialize_css(
            parent,
            func='rgb',
            alpha=alpha,
            precision=precision,
            fit=fit,
            none=none,
            color=kwargs.get('color', False),
            hexa=kwargs.get('hex', False),
            name=kwargs.get('names', False),
            legacy=kwargs.get('comma', False),
            upper=kwargs.get('upper', False),
            percent=kwargs.get('percent', False),
            compress=kwargs.get('compress', False),
            scale=255
        )
```

As all ColorAide color spaces are defined as plugins, there should be ample examples to help someone start writing a new
color space.
