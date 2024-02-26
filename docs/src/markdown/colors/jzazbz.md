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
`az` | [-0.5, 0.5]
`bz` | [-0.5, 0.5]

^\*^ Space is not bound to the defined range above but represents a practical range for HDR color spaces. CSS uses a
range of `jz` = [0, 1], `az` = [-1, 1] and `bz` = [1, 1] for percentage input and output.
////

//// html | figure
![Jzazbz](../images/jzazbz-3d.png)

///// html | figcaption
The sRGB gamut represented within the Jzazbz color space.
/////
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

Parsed input and string output formats support all valid CSS forms:

```css-color
color(jzazbz jz az bz / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("jzazbz", [0, 0, 0], 1)
```

The string representation of the color object and the default string output use the
`#!css-color color(jzazbz jz az bz / a)` form.

```py play
Color("jzazbz", [0.13438, 0.11789, 0.11188])
Color("jzazbz", [0.16937, 0.0312, 0.12308]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.jzazbz import Jzazbz

class Color(Base): ...

Color.register(Jzazbz())
```
