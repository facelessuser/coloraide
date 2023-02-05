# REC. 2100 HLG

!!! failure "The Rec. 2100 HLG is not registered in `Color` by default"

<div class="info-container" markdown>
!!! info inline end "Properties"

    **Name:** `rec2100-hlg`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

<figure markdown>

![Rec. 2020](../images/rec2020.png)

<figcaption markdown>
CIE 1931 xy Chromaticity -- Rec. 2100 Chromaticities (Same as Rec. 2020)

</figcaption>
</figure>

BT.2100, more commonly known by the abbreviations Rec. 2100 or BT.2100, introduced high-dynamic-range television
(HDR-TV) by recommending the use of the perceptual quantizer (PQ) or hybrid log–gamma (HLG) transfer functions instead
of the traditional "gamma" previously used for SDR-TV. Rec. 2100 HLG specifically uses the hybrid log-gamma transfer
function.

The actual gamut of Rec. 2100 uses the same wide color gamut of Rec. 2020, but the color space itself supports an HDR
range.

_[Learn about REC.2100](https://en.wikipedia.org/wiki/Rec._2100)_

</div>

## Channel Aliases

Channels | Aliases
-------- | -------
`r`      | `red`
`g`      | `green`
`b`      | `blue`

## Input/Output

Rec. 2100 HLG is not supported via the CSS spec and the parser input and string output only supports the
`#!css-color color()` function format using the custom name `#!css-color --rec2100-hlg`:

```css-color
color(--rec2100-hlg r g b / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("rec2100-hlg", [0, 0, 0], 1)
```

The string representation of the color object and the default string output will be in the
`#!css-color color(--rec2100-hlg r g b / a)` form.

```playground
Color("rec2100-hlg", [0.65587, 0.23436, 0.11415], 1)
Color("rec2100-hlg", [0.69294, 0.56608, 0.19838], 1).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.rec2100_hlg import Rec2100HLG

class Color(Base): ...

Color.register(Rec2100HLG())
```
