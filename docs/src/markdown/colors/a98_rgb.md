# A98 RGB

/// success | The A98 RGB color space is registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `a98-rgb`

**White Point:** D65

**Coordinates:**

Name | Range^\*^
---- | -----
`r`  | [0, 1]
`g`  | [0, 1]
`b`  | [0, 1]

^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.
////

//// html | figure
![A98 RGB](../images/a98-rgb.png)

///// html | figcaption
CIE 1931 xy Chromaticity -- Adobe(r) RGB 1998 Chromaticities
/////
////

The Adobe(r) RGB (1998) color space or opRGB is a color space developed by Adobe Systems(r), Inc. in 1998. It was
designed to encompass most of the colors achievable on CMYK color printers, but by using [RGB](./srgb.md) primary colors
on a device such as a computer display. The Adobe(r) RGB (1998) color space encompasses roughly 50% of the visible
colors specified by the [CIELab](./lab.md) color space - improving upon the gamut of the [sRGB](./srgb.md) color space,
primarily in cyan-green hues.

A98 RGB is an Adobe(r) 98 Compatible color space.

_[Learn about A98 RGB](https://en.wikipedia.org/wiki/Adobe_RGB_color_space)_
///

## Channel Aliases

Channels | Aliases
-------- | -------
`r`      | `red`
`g`      | `green`
`b`      | `blue`

## Input/Output

Parsed input and string output formats support all valid CSS forms:

```css-color
color(a98-rgb r g b / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("a98-rgb", [0, 0, 0], 1)
```

The string representation of the color object and the default string output will be in the
`#!css-color color(a98-rgb r g b / a)` form.

```py play
Color('a98-rgb', [0.85859, 0, 0])
Color('a98-rgb', [0.91489, 0.64117, 0.15031]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.a98_rgb import A98RGB

class Color(Base): ...

Color.register(A98RGB())
```
