# ICtCp

/// success | The ICtCp color space is registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `ictcp`

**White Point:** D65 / 2˚

**Coordinates:**

Name       | Range^\*^
---------- | ---------
`i`        | [0, 1]
`ct`       | [-0.5, 0.5]
`cp`       | [-0.5, 0.5]

^\*^ Space is not bound to the above, defined range but represents a practical range for HDR color spaces.
////

![ICtCp](../images/ictcp-3d.png)
//// figure-caption
The sRGB gamut represented within the ICtCp color space.
////

ICtCp is a color space format with better perceptual uniformity than [CIELab](./lab.md) and is used as a part of the
color image pipeline in video and digital photography systems for high dynamic range (HDR) and wide color gamut (WCG)
imagery. It was developed by Dolby Laboratories from the IPT color space by Ebner and Fairchild. It was designed with
the intention to replace YCbCr.

_[Learn about ICtCp](https://en.wikipedia.org/wiki/ICtCp)_
///

## Channel Aliases

Channels | Aliases
-------- | -------
`i`      | `intensity`
`ct`     | `tritan`
`cp`     | `protan`

## Input/Output

Parsed input and string output formats support all valid CSS forms in addition to allowing the `#!css-color color()`
function format as well using the custom name `#!css-color --ictcp`.

```css-color
ictcp(i ct cp / a)          // ICtCp function
color(--ictcp i ct cp / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("ictcp", [0, 0, 0], 1)
```

The string representation of the color object will always default to the `#!css-color color(--ictcp i ct cp / a)`
form, but the default string output will be the `#!css-color ictcp(i ct cp / a)` form.

```py play
Color("ictcp", [0.42788, -0.1157, 0.27873])
Color("ictcp", [0.50498, -0.20797, 0.11073]).to_string()
Color("ictcp", [0.56983, -0.25169, 0.03788]).to_string(percent=True)
Color("ictcp", [0.39138, -0.24061, -0.04423]).to_string(color=True)
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.ictcp.css import ICtCp

class Color(Base): ...

Color.register(ICtCp())
```
