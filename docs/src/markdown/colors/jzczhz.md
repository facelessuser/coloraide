# JzCzhz

/// failure | The JzCzhz color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `jzczhz`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range
---- | -----
`jz` | [0, 1]
`cz` | [0, 0.5]
`hz` | [0, 360)

^\*^ Space is not bound to the range but is specified to enclose the full range of an HDR BT.2020 gamut and is used
to define percentage inputs/outputs.
////

//// html | figure
![JzCzhz](../images/jzczhz-3d.png)

///// html | figcaption
The sRGB gamut represented within the JzCzhz color space.
/////
////

JzCzhz is the cylindrical form of [Jzazbz](./jzazbz.md).

_[Learn about JzCzhz](https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272)_
///

## Channel Aliases

Channels | Aliases
-------- | -------
`jz`     | `lightness`, `j`
`cz`     | `chroma`, `c`
`hz`     | `hue`, `h`

## Input/Output

/// warning | CSS Support
This color space is present the [Color HDR draft][css-color-hdr-1], but is not yet published in an official spec. If
this goes into an official, published spec, the ID and/or format is likely to change depending on the final decision on
format. We will likely keep the current format as a fallback for backward compatibility for some time.
///

As JzCzhz is not currently supported in the official CSS spec, only a draft, so the parsed input and string output
formats use the `#!css-color color()` function format using the custom name `#!css-color --jzczhz`:

```css-color
color(--jzczhz jz cz hz / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("jzczhz", [0, 0, 0], 1)
```

The string representation of the color object and the default string output use the
`#!css-color color(--jzczhz jz cz hz / a)` form.

```py play
Color("jzczhz", [0.13438, 0.16252, 43.502])
Color("jzczhz", [0.16937, 0.12698, 75.776]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.jzczhz import JzCzhz

class Color(Base): ...

Color.register(JzCzhz())
```
