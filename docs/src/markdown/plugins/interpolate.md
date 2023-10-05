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
        easings: List[Callable[..., float] | None],
        stops: Dict[int, float],
        space: str,
        out_space: str,
        progress: Union[Mapping[str, Callable[..., float]], Callable[..., float]] | None,
        premultiplied: bool,
        extrapolate: bool = False,
        domain: List[float] | None = None,
        hue: str = 'shorter',
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
`coloraide.interpolate.Interpolator`. While we won't show all the methods of the class, we will show the two functions
that must be defined.

```py
class Interpolator(metaclass=ABCMeta):
    """Interpolator."""

    @abstractmethod
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

`__init__` usually shouldn't be changed as it handles the general initialization for all interpolations. It could be
extended with `super()` to set some class specific initialization flags for specific features, but generally,
interpolation specific setup logic should be done in `Interpolator.setup()`. This is often used to restructure data
points to a more agreeable format for a given interpolation method, precalculate premultiplication, or normalize
undefined values when required. There are cases where ColorAide may update data points and re-call `setup()` directly.
As an example. `setup()` can be recalled when a continuous interpolation is converted to a discretized one.

`Interpolator.interpolate` is where the actual interpolation takes place. It expects an `index` from [1, n], the index
referencing the second color out of the two colors to be interpolated. `point`, usually between [0, 1], represents the
point on the interpolation line between the two colors under evaluation.

While `point` is usually a value between [0, 1], where 0 would be the color stop to the left, and 1 would be the color
stop to the right, if `point` exceeds the range of [0, 1], it can be assumed that the request is on the far left or far
right of all color stops and could be beyond the absolute range of the entire color interpolation chain.

By default, extrapolation is disabled between all colors in an interpolation chain, and any `point` that exceeds the
range of [0, 1], before easing functions are applied, will be clamped. If `extrapolate` is set to `$!py True`, the
points will not be clamped between any colors, in which case, it is an easing functions responsibility to ensure a value
between 0 or 1 if extreme values are not desired.

Check out the source code to see some example plugins.
