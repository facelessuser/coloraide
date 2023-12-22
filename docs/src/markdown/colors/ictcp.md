# ICtCp

/// failure | The ICtCp color space is not registered in `Color` by default
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

^\*^ Space is not bound to the range but is specified to enclose the full range of an HDR BT.2020 gamut and is used
to define percentage inputs/outputs.
////

//// html | figure
![ICtCp](../images/ictcp-3d.png)

///// html | figcaption
The sRGB gamut represented within the ICtCp color space.
/////
////

ICtCp is a color space format with better perceptual uniformity than [CIELab](#cielab) and is used as a part of the
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

/// warning | CSS Support
This color space is present the [Color HDR draft][css-color-hdr-1], but is not yet published in an official spec. If
this goes into an official, published spec, the ID and/or format is likely to change depending on the final decision on
format. We will likely keep the current format as a fallback for backward compatibility for some time.
///

As ICtCp is not currently supported in the official CSS spec, only a draft, so the parsed input and string output
formats use the `#!css-color color()` function format using the custom name `#!css-color --ictcp`:

```css-color
color(--ictcp i ct cp / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("ictcp", [0, 0, 0], 1)
```

The string representation of the color object and the default string output use the
`#!css-color color(--ictcp i ct cp / a)` form.

```py play
Color("ictcp", [0.42785, -0.11574, 0.2788])
Color("ictcp", [0.50497, -0.20797, 0.11077]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.ictcp import ICtCp

class Color(Base): ...

Color.register(ICtCp())
```
