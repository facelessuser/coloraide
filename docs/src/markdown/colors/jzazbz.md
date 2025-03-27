# Jzazbz

/// success | The Jzazbz color space is registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `jzazbz`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range^\*^
---- | ---------
`jz` | [0, 1]
`az` | [-0.21, 0.21]
`bz` | [-0.21, 0.21]

^\*^ Space is not bound to the defined range above but represents a practical range for HDR color spaces. CSS uses a
range of `jz` = [0, 1], `az` = [-1, 1] and `bz` = [1, 1] for percentage input and output.
////

![Jzazbz](../images/jzazbz-3d.png)
//// figure-caption
The sRGB gamut represented within the Jzazbz color space.
////

Jzazbz is a a color space designed for perceptual uniformity in high dynamic range (HDR) and wide color gamut (WCG)
applications. Conceptually it is similar to [CIELab](./lab.md), but claims the following improvements:

- Perceptual color difference is predicted by Euclidean distance.
- Perceptually uniform: MacAdam ellipses of just-noticeable-difference (JND) are more circular, and closer to the same
  sizes.
- Hue linearity: changing saturation or lightness has less shift in hue.

_[Learn about Jzazbz](https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272)_
///

## Channel Aliases

Channels | Aliases
-------- | -------
`jz`     | `lightness`, `j`
`az`     | `a`
`bz`     | `b`

## Input/Output

Parsed input and string output formats support all valid CSS forms in addition to allowing the `#!css-color color()`
function format as well using the custom name `#!css-color --jzazbz`.

```css-color
jzazbz(jz az bz / a)          // Jzazbz function
color(--jzazbz jz az bz / a)  // Color function
```

The string representation of the color object will always default to the `#!css-color color(--jzazbz jz az bz / a)`
form, but the default string output will be the `#!css-color jzazbz(jz az bz / a)` form.

```py play
Color("jzazbz", [0.13438, 0.11789, 0.11188])
Color("jzazbz", [0.16937, 0.0312, 0.12308]).to_string()
Color("jzazbz", [0.2096, -0.02864, 0.13479]).to_string(percent=True)
Color("jzazbz", [0.09203, -0.07454, 0.07996]).to_string(color=True)
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.jzazbz.css import Jzazbz

class Color(Base): ...

Color.register(Jzazbz())
```
