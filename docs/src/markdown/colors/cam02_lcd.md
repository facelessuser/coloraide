# CAM02 LCD

/// failure | The CAM02 LCD color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `cam02-lcd`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range^\*^
---- | -----
`j`  | [0, 100]
`a`  | [-75, 75]
`b`  | [-75, 75]

^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
relation to the Display P3 color space.
////

![CAM02 LCD](../images/cam02-lcd-3d.png)
//// figure-caption
The sRGB gamut represented within the CAM02 LCD color space.
////

This is the LCD variant of the CAM02 UCS color space and is optimized for "large" color distancing. See
[CAM02 UCS](./cam02_ucs.md) for more info.

[Learn more](https://www.researchgate.net/publication/221501922_The_CIECAM02_color_appearance_model).
///

## Viewing Conditions

CAM02 LCD uses the same environment setup for viewing conditions as [CAM02 JMh](./cam02.md), so check out the
related documentation if creating a CAM02 LCD variant is desired.

## Channel Aliases

Channels | Aliases
-------- | -------
`j`      | `lightness`
`a`      |
`b`      |

## Input/Output

The CAM02 LCD space is not currently supported in the CSS spec, the parsed input and string output formats use
the `#!css-color color()` function format using the custom name `#!css-color --cam02-lcd`:

```css-color
color(--cam02-lcd j a b / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--cam02-lcd j a b / a)` form.

```py play
Color("cam02-lcd", [60.054, 56.72, 35.659], 1)
Color("cam02-lcd", [79.041, 13.11, 41.225], 1).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.cam02_ucs import CAM02LCD

class Color(Base): ...

Color.register(CAM02LCD())
```
