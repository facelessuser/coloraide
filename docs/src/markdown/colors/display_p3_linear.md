# Linear Display P3

/// success | The Linear Display P3 color space is registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `display-p3-linear`

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
![Display P3](../images/display-p3.png)

///// html | figcaption
CIE 1931 xy Chromaticity -- Display P3 Chromaticities
/////
////

The Linear Display P3 space is the same as [Display P3](./display_p3.md) *except* that the transfer function is linear-light
(there is no gamma-encoding).

_[Learn about Display P3](https://www.color.org/chardata/rgb/DisplayP3.xalter)_
///

## Channel Aliases

Channels | Aliases
-------- | -------
`r`      | `red`
`g`      | `green`
`b`      | `blue`

## Input/Output

Linear Display P3 is not supported via the CSS spec and the parser input and string output only supports the
`#!css-color color()` function format using the custom name `#!css-color --display-p3-linear`:

```css-color
color(--display-p3-linear r g b / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("display-p3-linear", [0, 0, 0], 1)
```

The string representation of the color object and the default string output will be in the
`#!css-color color(--display-p3-linear r g b / a)` form.

```py play
Color("display-p3-linear", [0.82246, 0.03319, 0.01708])
Color("display-p3-linear", [0.88926, 0.39697, 0.04432]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.display_p3_linear import DisplayP3

class Color(Base): ...

Color.register(DisplayP3Linear())
```
