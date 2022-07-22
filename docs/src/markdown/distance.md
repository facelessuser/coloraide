# Color Distance and Delta E

The difference or distance between two colors allows for a quantified analysis of how far apart two colors are from one
another. This metric is of particular interest in the field of color science, but it has practical applications in
color libraries working with colors.

Usually, color distance is applied to near perceptual uniform color spaces in order to obtain a metric regarding a
color's visual, perceptual distance from another color. This can be useful in gamut mapping or even determining that
colors are close enough or far enough away from each other.

## Color Distance

ColorAide provides a simple euclidean color distance function. By default, it evaluates the distance in the CIELab color
space, but it can be configured to evaluate in any color space, such as Oklab, etc. It may be less useful in some color
spaces compared to others. Some spaces may not be well suited, such as cylindrical spaces. Some spaces might not be as
very perceptually uniform as others requiring more complex algorithms.

```playground
Color("red").distance("blue", space="srgb")
Color("red").distance("blue", space="lab")
```

## Delta E

The `delta_e` function gives access to various ∆E implementations, which are just different algorithms to calculate
distance. Some are simply Euclidean distance withing a certain color space, some are far more complex.

If no `method` is specified, the default implementation is ∆E^\*^~ab~ (CIE76) which uses a simple Euclidean distancing
algorithm on the CIELab color space. It is fast, but not as accurate as later iterations of the algorithm as CIELab is
not actually as perceptually uniform as it was thought when CIELab was originally developed.

```playground
Color("red").delta_e("blue")
```

When `method` is set, the specified ∆E algorithm will be used instead. For instance, below we use ∆E~00~ which is a
more complex algorithm that accounts for the CIELab's weakness in perceptually uniformity. It does come at the cost of
being a little slower.

```playground
Color("red").delta_e("blue", method="2000")
```

!!! warning "Distancing and Symmetry"
    It should be noted that not all distancing algorithms are symmetrical. Some are order dependent.

Below are all the supported ∆E methods that are included in the default `coloraide.Color` object. Follow relevant links
to read the specs and find out more about a given ∆E method.

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | ----------
[∆E^\*^~ab~][de76]\ (CIE76)              | :octicons-check-16:   | `76`            |
[∆E^\*^~cmc~][decmc]\ (CMC\ l:c\ (1984)) | :octicons-check-16:   | `cmc`           | `l=2, c=1`
[∆E^\*^~94~][de94]\ (CIE94)              | :octicons-x-16:       | `94`            | `kl=1, k1=0.045, k2=0.015`
[∆E^\*^~00~][de2000]\ (CIEDE2000)        | :octicons-check-16:   | `2000`          | `kl=1, kc=1, kh=1`
[∆E~HyAB~][dehyab]\ (HyAB)               | :octicons-check-16:   | `hyab`          | `space="lab-d65"`
∆E~ok~                                   | :octicons-check-16:   | `ok`            | `scalar=1`

The following are also available, but they must be manually registered by creating a
[custom class](./color.md#custom-color-classes), or can be accessed by use `coloraide.everything.ColorAll` instead of
`coloraide.Color`. The associated color space must be registered as well.

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | --------------------
[∆E~itp~][deitp]\ (ICtCp)                | :octicons-check-16:   | `itp`           | `scalar=720`
[∆E~z~][dez]\ (Jzazbz)                   | :octicons-check-16:   | `jz`            |
[∆E~99o~][de99o]\ (DIN99o)               | :octicons-check-16:   | `99o`           |

## Finding Closest Color

ColorAide implements a simple way to find the closest color, given a list of colors, to another color. The method is
called `closest` and takes a list of colors that are to be compared to the calling color object. The first color with
the smallest distance between the calling color object and itself will be considered the nearest/closest color.

Consider the following example. Here we provide a list of colors to compare against `#!color red`. After comparing all
the colors, the closest ends up being `#!color maroon`.

```playground
Color('red').closest(['pink', 'yellow', 'green', 'blue', 'purple', 'maroon'])
```

The default distancing method is used if one is not supplied, but others can be used:

```playground
Color('red').closest(['pink', 'yellow', 'green', 'blue', 'purple', 'maroon'], method='2000')
```
