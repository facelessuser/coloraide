# Color Distance and Delta E

## Color Distance

ColorAide provides a simple euclidean color distance function. By default, it evaluates the distance in the Lab color
space, but it can be configured to evaluate in any color space. It may be less useful in some color spaces compared to
others:

```color
Color("red").distance("blue", space="srgb")
Color("red").distance("blue", space="lab")
```

## Delta E

The `delta_e` function gives access to various delta E implementations.

```color
Color("red").delta_e("blue")
Color("red").delta_e("blue", method="2000")
```

The default implementation is Delta E 1976. Originally, when the Lab color space was created, it was thought that it was
more perceptually uniform than it actually was. At first, the distance algorithm was a simple euclidean implementation
(Delta E 1976), but over time it has been tweaked to make corrections to account for the fact that it is not perfectly
uniform.

There are areas and industries that still use many of these for different reasons.

ColorAide implements the following delta E methods:

Name             | Parameter\ Name | Weighted\ Parameters
---------------- | --------------- | --------------------
CIE76            | `76`            |
CMC\ l:c\ (1984) | `cmc`           | `l=2, c=1`
CIE94            | `94`            | `kl=1, k1=0.045, k2=0.015`
CIEDE2000        | `2000`          | `kl=1, kc=1, kh=1`
