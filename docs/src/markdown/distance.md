# Color Distance and Delta E

The difference or distance between two colors allows for a quantified analysis of how far apart two colors are from one
another. This metric is of particular interest in the field of color science, but it has practical applications in
color libraries working with colors.

Usually, color distance is applied to near perceptual uniform color spaces in order to obtain a metric regarding a
color's visual, perceptual distance from another color. This can be useful in gamut mapping or even determining that
colors are close enough or far enough away from each other.

## Color Distance

ColorAide provides a simple euclidean color distance function. By default, it evaluates the distance in the CIELAB color
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
algorithm on the CIELAB color space. It is fast, but not as accurate as later iterations of the algorithm as CIELAB is
not actually as perceptually uniform as it was thought when CIELAB was originally developed.

```playground
Color("red").delta_e("blue")
```

When `method` is set, the specified ∆E algorithm will be used instead. For instance, below we use ∆E~00~ which is a
more complex algorithm that accounts for the CIELAB's weakness in perceptually uniformity. It does come at the cost of
being a little slower.

```playground
Color("red").delta_e("blue", method="2000")
```

Below are all the supported ∆E methods. Follow relevant links to read the specs and find out more about a given ∆E
method.

Delta\ E                                 | Name            | Parameters
---------------------------------------- | --------------- | --------------------
[∆E^\*^~ab~][de76]\ (CIE76)              | `76`            |
[∆E^\*^~cmc~][decmc]\ (CMC\ l:c\ (1984)) | `cmc`           | `l=2, c=1`
[∆E^\*^~94~][de94]\ (CIE94)              | `94`            | `kl=1, k1=0.045, k2=0.015`
[∆E^\*^~00~ ][de2000]\ (CIEDE2000)       | `2000`          | `kl=1, kc=1, kh=1`
[∆E~itp~][deitp]\ (ICtCp)                | `itp`           | `scalar=720`
[∆E~z~][dez]\ (Jzazbz)                   | `jz`            |
[∆E~99o~][de99o]\ (DIN99o)               | `99o`           |
[∆E~HyAB~][dehyab]\ (HyAB)               | `hyab`          | `space="lab"`
∆E~ok~                                   | `ok`            | `scalar=1`

∆E methods are also accessible via methods `delta_e_<name>`, where `<name>` is a name from the above table.

```playground
Color("red").delta_e_jz("blue")
Color("red").delta_e_hyab("blue")
```
