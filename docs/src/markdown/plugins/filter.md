# Filters

## Description

Filter plugins allow you to apply a filter to a given color, altering its appearance.

## Plugin Class

```py
class Filter(Plugin, metaclass=ABCMeta):
    """Filter plugin."""

    NAME = ""
    DEFAULT_SPACE = 'srgb-linear'
    ALLOWED_SPACES = ('srgb-linear', 'srgb')

    @abstractmethod
    def filter(self, color: 'Color', amount: Optional[float], **kwargs: Any) -> None:
        """Filter the given color."""
```

Once registered, the plugin can then be used via `filter` by passing its `NAME` via the `method` parameter along with
the `amount` specifying to what magnitude the filter is applied. Any additional key word arguments also be specified to
allow for overriding default behaviors. The current `color` will then be altered by the filter.

`DEFAULT_SPACE` describes the default color space under which the filter is applied, while `ALLOWED_SPACES` defines
optional, allowed spaces that can be specified. Color space conversion is handled before passing the color to the
plugin.

```py
color.filter(NAME, amount, **kwargs)
```

If you'd like the user to be able to set specific defaults, you can define an `__init__` method and manage defaults
accordingly. Defaults can be passed in when instantiating a new plugin.

```py
Color.register(Plugin(**kwargs))
```
