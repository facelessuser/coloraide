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
        extrapolate: bool = False,
        domain: Optional[List[float]] = None,
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

    def setup(self) --> None:
        """Setup."""

    @abstractmethod
    def interpolate(
        self,
        point: float,
        index: int,
    ) -> Vector:
        """Interpolate."""
```

`Interpolator.interpolate` expects an `index` (1 - n) indicating which pair of color stops a given `point` refers to. It
is possible that `point` could exceed the normal range, in which case `index` will still refer to to either the minimum
or maximum color stop pair, whichever the point exceeds.

`point` is usually a value between 0 - 1, where 0 would be the color stop to the left, and 1 would be the color stop to
the right. If `point` exceeds the range of 0 and 1, it can be assumed that the request is on the far left or far right
of all color stops, and could be beyond the absolute range of the entire color interpolation chain.

By default, extrapolation is disabled between all colors in an interpolation chain, and any `point` that exceeds the
range of 0 - 1, after easing functions are applied, will be clamped. If `extrapolate` is set to `$!py True`, the points
will not be clamped between any colors, in which case, it is an easing functions responsibility to ensure a value
between 0 or 1 if extreme values are not desired.

Additionally, an optional `Interpolator.setup` method is provided to allow for any additional setup required.
Premultiplication is usually done in `setup` ahead of time. Resolution of undefined values can be recalculated here
as well as it is usually needed so that premultiplication can be done on coordinates that contain undefined values.
With that said, such calculations can also be deferred and handled on the fly if desired.

Check out the source code to see some example plugins.
