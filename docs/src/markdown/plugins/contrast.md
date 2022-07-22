# Contrast

## Description

Contrast returns a numerical value that is meant to determine how much visual contrast exists between two colors. While
the current default is agnostic to ordering of the colors, some algorithms can be sensitive to order.

## Plugin Class

```py
class ColorContrast(Plugin, metaclass=ABCMeta):
    """Color contrast plugin class."""

    NAME = ''

    @abstractmethod
    def contrast(self, color1: 'Color', color2: 'Color', **kwargs: Any) -> float:
        """Get the contrast of the two provided colors."""

```

Once registered, the plugin can then be used via `contrast` by passing its `NAME` via the `method` parameter along with
a secondary color (`color2`) representing the background color. The calling color (`color1`) will be considered the
text color. Any additional key word arguments can be specified to override default behavior. The "contrast" will be
returned as a float.

```py
color1.contrast(color2, method=NAME, **kwargs)
```

If you'd like the user to be able to set specific defaults, you can define an `__init__` method and manage defaults
accordingly. Defaults can be passed in when instantiating a new plugin.

```py
Color.register(Plugin(**kwargs))
```
