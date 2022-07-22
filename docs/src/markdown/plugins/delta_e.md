# Delta E

## Description

∆E plugins allow for getting color differences with different methods. ColorAide provides a number of methods by default
which are documented under [Color Distance and Delta E](../distance.md). All of the default ∆E methods are provided as
plugins, and users can create their own as well.

## Plugin Class

∆E plugins are subclassed from `#!py3 coloraide.distance.DeltaE`.

```py
class DeltaE(Plugin, metaclass=ABCMeta):
    """Delta E plugin class."""

    NAME = ''

    @abstractmethod
    def distance(self, color: 'Color', sample: 'Color', **kwargs: Any) -> float:
        """Get distance between color and sample."""
```

Once registered, the plugin can then be used via `delta_e` by passing its `NAME` via the `method` parameter along with
any additional key word arguments to override default behavior. The return will be a float indicating the distance.

```py
color.delta_e(sample, method=NAME, **kwargs)
```

If you'd like the user to be able to set specific defaults, you can define an `__init__` method and manage defaults
accordingly. Defaults can be passed in when instantiating a new plugin.

```py
Color.register(Plugin(**kwargs))
```
