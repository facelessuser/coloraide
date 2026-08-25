---
icon: lucide/scaling
---
# Contrast

## Description

Gamut provides an interface for _special_ gamuts. These gamuts aren't specific to a color space, but usually some
calculated limit. These are often awkward to easily convert to or work directly in. As an example, the Visible Spectrum
is treated as one of these _special_ gamuts in ColorAide.

The Gamut plugin mainly provides two functions: to check if a color is within a _special_ gamut and to force a color
into that _special_ gamut. The logic to check and gamut map the color is often specific to the the _special_ gamut.

## Plugin Class

```py
class Gamut(Plugin, metaclass=ABCMeta):
    """Gamut plugin class."""

    NAME = ""

    @abstractmethod
    def in_gamut(self, color: Color, tolerance: float, **kwargs: Any) -> bool:
        """Check if in gamut."""

    @abstractmethod
    def fit(self, color: Color, **kwargs: Any) -> None:
        """Check if in gamut."""
```

Once registered, the plugin can then be used via `in_gamut()` by passing its `NAME` as if it were a color space along
with an optional `tolerance` and gamut specific options.

```py
color.in_gamut(NAME, tolerance=0, **kwargs)
```

Additionally the plugin is used via the `fit()` method and allows passing `NAME` as if it were a color space. Any other
specified options, are passed to the the plugin.

```py
color.fit(NAME, **kwargs)
```
