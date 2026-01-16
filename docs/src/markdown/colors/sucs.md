# sUCS

> [!failure] The sUCS color space is not registered in `Color` by default

/// html | div.info-container
> [!info | inline | end] Properties
> **Name:** `sucs`
>
> **White Point:** D65 / 2˚
>
> **Coordinates:**
>
> Name | Range^\*^
> ---- | -----
> `jz`  | [0, 100]
> `mz`  | [0, 65]
> `hz`  | [0, 360)
>
> ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
> relation to the Display P3 color space.

![sUCS](../images/sucs-3d.png)
//// figure-caption
The sRGB gamut represented within the sUCS color space.
////

The sUCS (simple Uniform Color Space) is a new uniform color space developed as the base on which [sCAM](./scam_jmh.md)
(simple Color Apperance Model) was built upon. The structure of sUCS is based on the structure of [IPT](./ipt.md) and
[CAM16-UCS](./cam16-ucs.md) for their hue linearity, and space uniformity, respectively.

[Learn more](https://opg.optica.org/oe/fulltext.cfm?uri=oe-29-4-6036&id=447640).
///

## Channel Aliases

Channels | Aliases
-------- | -------
`i`      | `intensity`
`c`      | `chroma`
`h`      | `hue`

## Input/Output

The sUCS space is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --sucs`:

```css-color
color(--sucs i c h / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--sucs i c h / a)` form.

```py play
Color("sucs", [54.706, 55.669, 29.937], 1)
Color("sucs", [74.256, 44.701, 67.919], 1).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.sucs import sUCS

class Color(Base): ...

Color.register(sUCS())
```
