# CCT

## Description

CCT plugins allow you to calculate a color from a CCT and ∆~uv~ or calculate a CCT and ∆~uv~ from a color.

## Plugin Class

```py
class CCT(Plugin, metaclass=ABCMeta):
    """Delta E plugin class."""

    NAME = ''

    @abstractmethod
    def to_cct(self, color: Color, **kwargs: Any) -> Vector:
        """Calculate a color's CCT."""

    @abstractmethod
    def from_cct(
        self,
        color: type[Color],
        space: str,
        kelvin: float,
        duv: float,
        scale: bool,
        scale_space: str | None,
        **kwargs: Any
    ) -> Color:
        """Calculate a color that satisfies the CCT."""
```

Once registered, the plugin can then be used via the `cct()` or `blackbody()` methods by passing its `NAME` via the
`method` parameter.

```py
Color('orange').cct(method=NAME, **kwargs)
Color.blackbody(space, kelvin, duv, method=NAME, **kwargs)
```

If you'd like the user to configure the plugin on registration, you can define an `__init__` method. To register the
plugin, just the `register()` method.

```py
Color.register(Plugin(**kwargs))
```
