# CAM16 UCS

/// failure | The CAM16 UCS color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `cam16-ucs`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range^\*^
---- | -----
`j`  | [0, 100]
`a`  | [-50, 50]
`b`  | [-50, 50]

^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
relation to the Display P3 color space.
////

![CAM16 UCS](../images/cam16-ucs-3d.png)
//// figure-caption
The sRGB gamut represented within the CAM16 UCS color space.
////

The CAM16 UCS space takes the [CAM16](./cam16.md) model and applies an additional nonlinear transformation to lightness
and colorfulness so that a color difference metric ΔE can be based more closely on Euclidean distance. The `cam16-ucd`
color space in ColorAide is based off CAM16 (Jab) which uses M (colorfulness) to derive the a and b values. There are
also [SCD](./cam16_scd.md) and [LCD](./cam16_lcd.md) variants which optimize the spaces for "small" and "large" color
distancing respectively.

[Learn more](https://www.researchgate.net/publication/318152296_Comprehensive_color_solutions_CAM16_CAT16_and_CAM16-UCS).
///

## Viewing Conditions

CAM16 UCS uses the same environment setup for viewing conditions as [CAM16 JMh](./cam16.md), so check out the
related documentation if creating a CAM16 UCS variant is desired.

## Channel Aliases

Channels | Aliases
-------- | -------
`j`      | `lightness`
`a`      |
`b`      |

## Input/Output

The CAM16 UCS space is not currently supported in the CSS spec, the parsed input and string output formats use
the `#!css-color color()` function format using the custom name `#!css-color --cam16-ucs`:

```css-color
color(--cam16-ucs j a b / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--cam16-ucs j a b / a)` form.

```py play
Color("cam16-ucs", [59.178, 40.82, 21.153], 1)
Color("cam16-ucs", [78.364, 9.6945, 28.629], 1).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.cam16_ucs import CAM16UCS

class Color(Base): ...

Color.register(CAM16UCS())
```
