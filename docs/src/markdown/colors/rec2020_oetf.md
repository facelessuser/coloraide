# REC. 2020 (OETF)

/// failure | The Rec. 2020 (OETF) color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `rec2020-oetf`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range^\*^
---- | -----
`r`  | [0, 1]
`g`  | [0, 1]
`b`  | [0, 1]

^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.
////

![Rec. 2020](../images/rec2020.png)
//// figure-caption
CIE 1931 xy Chromaticity -- Rec. 2020 Chromaticities
////

ITU-R Recommendation BT.2020, more commonly known by the abbreviations Rec. 2020 or BT.2020, defines various aspects of
ultra-high-definition television (UHDTV) with standard dynamic range (SDR) and wide color gamut (WCG), including picture
resolutions, frame rates with progressive scan, bit depths, color primaries, RGB and luma-chroma color representations,
chroma subsamplings, and an opto-electronic transfer function. The color is used in 4k and 8k UHDTV.

This is a scene-referred variant that uses the OETF specified in the BT.2020 spec.

_[Learn about REC.2020](https://en.wikipedia.org/wiki/Rec._2020)_

///

## Channel Aliases

Channels | Aliases
-------- | -------
`r`      | `red`
`g`      | `green`
`b`      | `blue`

## Input/Output

Rec. 709 is not supported via the CSS spec and the parser input and string output only supports the
`#!css-color color()` function format using the custom name `#!css-color --rec2020-oetf`:

```css-color
color(--rec2020-oetf r g b / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("--rec2020-oetf", [0, 0, 0], 1)
```

The string representation of the color object and the default string output will be in the
`#!css-color color(rec2020 r g b / a)` form.

```py play
Color("rec2020-oetf", [0.79198, 0.23098, 0.07376])
Color("rec2020-oetf", [0.86727, 0.64078, 0.18496]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.rec2020_oetf import Rec2020OETF

class Color(Base): ...

Color.register(Rec2020OETF())
```
