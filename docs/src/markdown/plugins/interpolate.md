# Interpolation

## Description

Interpolation plugins allow for interpolation between one or more colors. All interpolation in ColorAide is provided via
plugins.

## Plugin Class

Plugins are are created by subclassing `#!py3 coloraide.interpolate.Interpolate`.

```py
class Interpolate(Plugin, metaclass=ABCMeta):
    """Interpolation plugin."""

    NAME = ""

    @abstractmethod
    def interpolator(
        self,
        coordinates: List[Vector],
        channel_names: Sequence[str],
        create: Type['Color'],
        easings: List[Optional[Callable[..., float]]],
        stops: Dict[int, float],
        space: str,
        out_space: str,
        progress: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
        premultiplied: bool,
        **kwargs: Any
    ) -> Interpolator:
        """Get the interpolator object."""
```

Once registered, the plugin can then be used via `interpolate`, `steps`, or `mix` by passing its `NAME` via the `method`
parameter along with any additional key word arguments to override default behavior. An `Interpolator` object will be
returned which allows for interpolating between the given list of `colors`.

```py
color.interpolate(colors, method=NAME)
```

In general, the `Interpolate` plugin is mainly a wrapper to ensure the interpolation setup uses an appropriate
`Interpolator` object which does the actual work. An interpolation plugin should derive their `Interpolator` class from
`coloraide.interpolate.Interpolator`. While we won't show all the methods of the class, we will show the one function
that must be defined.

```py
class Interpolator(metaclass=ABCMeta):
    """Interpolator."""

    @abstractmethod
    def interpolate(
        self,
        easing: Optional[Union[Mapping[str, Callable[..., float]], Callable[..., float]]],
        point: float,
        index: int,
    ) -> Vector:
        """Interpolate."""
```

`Interpolator.interpolate` expects an optional `easing` method that can be either a callback, or a dictionary of
easing functions for specific color channels. Additionally, it accepts a user defined `point` indicating where between
the colors the user is requesting the new color and the `index`, within the list of colors to be interpolated,
of the color to the right of the `point`. The function should return the interpolated coordinates for the color.

Check out the source code to see some example plugins.
