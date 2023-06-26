# xyY

/// failure | The xyY color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `xyy`

**White Point:** D65

**Coordinates:**

Name | Range^\*^
---- | -----
`x`  | [0, 1]
`y`  | [0, 1]
`Y`  | [0, 1]

^\*^ Space is not bound to the range and is used to define percentage inputs/outputs.
////

//// html | figure
![xyY](../images/xyy-3d.png)

///// html | figcaption
The sRGB gamut represented within the xyY color space.
/////
////

A derivative of the CIE 1931 XYZ space, the CIE xyY color space, is often used as a way to graphically present the
chromaticity of colors.

/// tip
The color space, as implemented, is relative to the D65 white point, meaning it is created from XYZ D65. If colors are
needed relative to different white points, the color space can be subclassed. If proper chromaticity coordinates are
desired for a given color, you can checkout the [API for chromaticity coordinates](../chromaticity.md).
///

[Learn more](https://en.wikipedia.org/wiki/CIE_1931_color_space#CIE_xy_chromaticity_diagram_and_the_CIE_xyY_color_space).
///

## Channel Aliases

Channels | Aliases
-------- | -------
`x`      |
`y`      |
`Y`      |

## Input/Output

The xyY space is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --xyy`:

```css-color
color(--xyy x y Y / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--xyy x y Y / a)` form.

```py play
Color("xyy", [0.64, 0.33, 0.21264])
Color("xyy", [0.50047, 0.4408, 0.48173]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.xyy import xyY

class Color(Base): ...

Color.register(xyY())
```
