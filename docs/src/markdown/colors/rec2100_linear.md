# Linear REC. 2020

/// success | The Linear Rec. 2100 color space is registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `rec2100-linear`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range^\*^
---- | -----
`r`  | [0, 1]
`g`  | [0, 1]
`b`  | [0, 1]

^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.
////

//// html | figure
![Rec. 2120](../images/rec2020.png)

///// html | figcaption
CIE 1931 xy Chromaticity -- Rec. 2020 Chromaticities (the same as Rec. 2100)
/////
////

The Linear Rec. 2100 space is the same as [Linear Rec. 2100](./rec2020_linear.md) and is essentially an alias required
by the CSS HDR specification.

_[Learn about REC.2020](https://en.wikipedia.org/wiki/Rec._2020)_

///

## Channel Aliases:**

Channels | Aliases
-------- | -------
`r`      | `red`
`g`      | `green`
`b`      | `blue`

## Input/Output

Parsed input and string output formats support all valid CSS forms:

```css-color
color(rec2020-linear r g b / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("rec2020-linear", [0, 0, 0], 1)
```

The string representation of the color object and the default string output will be in the
`#!css-color color(rec2020-linear r g b / a)` form.

```py play
Color("rec2100-linear", [0.6274, 0.0691, 0.01639])
Color("rec2100-linear", [0.7513, 0.41509, 0.04951]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.rec2100_linear import Rec2100Linear

class Color(Base): ...

Color.register(Rec2100Linear())
```
