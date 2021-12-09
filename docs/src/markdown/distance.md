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

If no `method` is specified, the default implementation is ∆E^\*^~ab~ (CIE76) which uses a simple Euclidean distancing
algorithm on the CIELAB color space. It is fast, but not as accurate as some algorithms as CIELAB is not actually as
perceptually uniform as it was thought when CIELAB was developed. ∆E~00~ is actually a much better ∆E method for CIELAB,
but it is slower.

```playground
Color("red").delta_e("blue")
```

When `method` is set, the specified ∆E algorithm will be used instead. For instance, below we use ∆E~00~ which is a
more complex, slower algorithm that accounts for the color spaces weakness in perceptually uniformity.

```playground
Color("red").delta_e("blue", method="2000")
```

Below are all the supported ∆E methods. Follow relevant links to read the specs or find our more about a given ∆E
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
