# Fit/Gamut Mapping

## Description

Fit plugins (or gamut mapping plugins) allow for mapping an out of gamut color to be within the current color space's
gamut. All default gamut mapping methods provided by ColorAide are provided via plugins.

## Plugin Class

Plugins are are created by subclassing `#!py3 coloraide.gamut.Fit`.

```py
class Fit(Plugin, metaclass=ABCMeta):
    """Fit plugin class."""
    """Fit plugin class."""

    NAME = ''

    @abstractmethod
    def fit(self, color: 'Color', **kwargs) -> None:
        """Get coordinates of the new gamut mapped color."""
```

Once registered, the plugin can then be used via `fit` (and in some places like `convert`) by passing its `NAME` via the
`method` parameter along with any additional key word arguments to override default behavior. The current `color` will
be gamut mapped accordingly.

```py
color.fit(method=NAME, **kwargs)
```

If you'd like the user to be able to set specific defaults, you can define an `__init__` method and manage defaults
accordingly. Defaults can be passed in when instantiating a new plugin.

```py
Color.register(Plugin(**kwargs))
```

/// warning | Reserved Name
`clip` is a special, reserved name and the associated plugin cannot be overridden. Another clip plugin can be
written, but it cannot override the original.
///
