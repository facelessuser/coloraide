# Color Distance and Delta E

## Color Distance

ColorAide provides a simple euclidean color distance function. By default, it evaluates the distance in the CIELAB color
space, but it can be configured to evaluate in any color space, such as Oklab, etc. It may be less useful in some color
spaces compared to others. Some spaces may not be well suited, such as cylindrical spaces. Some spaces might not be
very perceptually uniform.

```playground
Color("red").distance("blue", space="srgb")
Color("red").distance("blue", space="lab")
```

## Delta E

The `delta_e` function gives access to various ∆E implementations.

```playground
Color("red").delta_e("blue")
Color("red").delta_e("blue", method="2000")
```

The general `delta_e` function can be used to specify any supported ∆E method. Optional parameters can be passed in if
desired. See table below for supported methods, names, and parameters. Follow relevant links to read the specs or find
our more about a given ∆E method.

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

∆E methods are also accessible via methods `delta_e_<name>`, where `<name>` is a name from the above table.

```playground
Color("red").delta_e_jz("blue")
Color("red").delta_e_hyab("blue")
```

If no name is specified, the default implementation is ∆E^\*^~ab~ (CIE76). Originally, when the CIELAB color space was
created, it was thought that it was more perceptually uniform than it actually was. At first, the distance algorithm was
a simple euclidean implementation (∆E^\*^ 1976), but over time it has been tweaked to make corrections to account for
the fact that it is not perfectly uniform. This gave rise to all of the various ∆E^\*^ methods above. There are areas
and industries that still use many of these for different reasons.

Additionally, there are other implementations that use different color spaces, such as ∆E~itp~ which uses ICtCp or ∆E~z~
which uses Jzazbz.

Also, there are some general methods such as ∆E~HyAB~. HyAB is designed to work with Lab-ish colors (CIELAB, CIELUV,
DIN99o, etc.).
