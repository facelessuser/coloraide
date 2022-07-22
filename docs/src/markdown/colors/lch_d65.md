# LCh D65

!!! success "The LCh D65 color space is registered in `Color` by default"

<div class="info-container" markdown>
!!! info inline end "Properties"

    **Name:** `lch-d65`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 100]
    `c`  | [0, 160]
    `h`  | [0, 360)

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown>

![CIELCh D65 3D](../images/lch-d65-3d.png)

<figcaption markdown>
The sRGB gamut represented within the CIELCh D65 color space.
</figcaption>
</figure>

CIELCh D65 is the same as [CIELCh](./lch.md) except it uses a D65 white point.

_[Learn about CIELCh](https://en.wikipedia.org/wiki/CIELab_color_space#Cylindrical_representation:_CIELCh_or_CIEHLC)_
</div>

## Channel Aliases

Channels | Aliases
-------- | -------
`l`      | `lightness`
`c`      | `chroma`
`h`      | `hue`

## Input/Output

As a D65 variant of CIELCh is not currently supported in the CSS spec, the parsed input and string output
formats use the `#!css-color color()` function format using the custom name `#!css-color --lch-d65`:

```css-color
color(--lch-d65 l c h / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("lch-d65", [0, 0, 0], 1)
```

The string representation of the color object and the default string output use the
`#!css-color color(--lch-d65 l c h / a)` form.

```playground
Color("lch-d65", [53.237, 104.55, 40])
Color("lch-d65", [74.934, 82.499, 73.14]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.lch_d65 import LChD65

class Color(Base): ...

Color.register(LChD65())
```
