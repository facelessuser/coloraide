# Chromatic Adaptation

## Description

CAT plugins chromatically adapt a given XYZ coordinate from its current reference white point to a new desired white
point. This is useful during conversion when one color space is converted to another color space that uses a difference
reference white.

## Plugin Class

Plugins are are created by subclassing `#!py3 coloraide.cat.CAT`.

```py
class CAT(Plugin, metaclass=ABCMeta):
    """Chromatic adaptation."""

    NAME = ""

    @abstractmethod
    def adapt(self, w1: Tuple[float, float], w2: Tuple[float, float], xyz: VectorLike) -> Vector:
        """Adapt a given XYZ color using the provided white points."""
```

Once registered, the plugin can then be used via `chromatic_adaptation` by passing its `NAME` via the the `method`
along two white points (as XYZ values): `w1` as the current white point and `w2` as the target white point.

It should be noted that `chromatic_adaptation` is not usually directly used by the user, so a more likely approach is
to override the `DELTA_E` parameter of a subclassed `Color` object to specify the plugin as the default for chromatic
adaptation.

## Von Kries CAT

Currently, ColorAide only ships with Von Kries based adaptation methods. If it is desired to create a Von Kries based
plugin, it is recommended to subclass the `VonKries` class which is based on `CAT`. When subclassing a `VonKries` based
CAT, the `NAME` and a `MATRIX` must be provided. The general calculations related to the source and target white point,
will automatically be calculated and an appropriate matrix and inverted matrix will be returned to perform the
adaptation without any additional logic.

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
