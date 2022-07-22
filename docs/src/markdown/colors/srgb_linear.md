# Linear sRGB

!!! success "The Linear sRGB color space is registered in `Color` by default"

<div class="info-container" markdown>
!!! info inline end "Properties"

    **Name:** `srgb-linear`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

<figure markdown>

![sRGB](../images/srgb.png)

<figcaption markdown>
CIE 1931 xy Chromaticity -- sRGB Chromaticities
</figcaption>
</figure>

The sRGB Linear space is the same as [sRGB](./srgb.md) *except* that the transfer function is linear-light (there is no
gamma-encoding).

_[Learn about sRGB](https://en.wikipedia.org/wiki/SRGB)_
</div>

## Channel Aliases

Channels | Aliases
-------- | -------
`r`      | `red`
`g`      | `green`
`b`      | `blue`

## Inputs/Output

Parsed input and string output formats support all valid CSS forms:

```css-color
color(srgb-linear r g b / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("srgb-linear", [0, 0, 0], 1)
```

The string representation of the color object and the default string output will be in the
`#!css-color color(srgb-linear r g b / a)` form.

```playground
Color("srgb", [1, 0, 0])
Color("srgb", [1, 0.37626, 0]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.srgb_linear import sRGBLinear

class Color(Base): ...

Color.register(sRGB())
```
