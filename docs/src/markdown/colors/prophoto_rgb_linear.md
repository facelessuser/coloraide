# Linear ProPhoto

/// success | The Linear ProPhoto color space is registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `prophoto-rgb-linear`

**White Point:** D50

**Coordinates:**

Name | Range^\*^
---- | -----
`r`  | [0, 1]
`g`  | [0, 1]
`b`  | [0, 1]

^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.
////

//// html | figure
![ProPhoto RGB](../images/prophoto-rgb.png)

///// html | figcaption
CIE 1931 xy Chromaticity -- ProPhoto RGB Chromaticities
/////
////

The Linear ProPhoto space is the same as [ProPhoto](./prophoto_rgb.md) *except* that the transfer function is linear-light
(there is no gamma-encoding).

_[Learn about ProPhoto](https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space)_
///

## Channel Aliases

Channels | Aliases
-------- | -------
`r`      | `red`
`g`      | `green`
`b`      | `blue`

## Input/Output

Linear ProPhoto is not supported via the CSS spec and the parser input and string output only supports the
`#!css-color color()` function format using the custom name `#!css-color --prophoto-rgb-linear`:

```css-color
color(--prophoto-rgb-linear r g b / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("prophoto-rgb-linear", [0, 0, 0], 1)
```

The string representation of the color object and the default string output will be in the
`#!css-color color(--prophoto-rgb-linear r g b / a)` form.

```py play
Color("prophoto-rgb-linear", [0.52928, 0.09837, 0.01688])
Color("prophoto-rgb-linear", [0.6535, 0.42702, 0.06115]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.prophoto_rgb_linear import ProPhotoRGBLinear

class Color(Base): ...

Color.register(ProPhotoRGBLinear())
```
