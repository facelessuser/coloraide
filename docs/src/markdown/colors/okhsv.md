# Okhsv

!!! failure "The Okhsv color space is not registered in `Color` by default"

<div class="info-container" markdown>
!!! info inline end "Properties"

    **Name:** `okhsv`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `h`  | [0, 360)
    `s`  | [0, 1]
    `v`  | [0, 1]

<figure markdown>

![Okhsv 3D](../images/okhsv-3d.png)

<figcaption markdown>
Okhsv color space in 3D
</figcaption>
</figure>

Okhsv is a color space created by Björn Ottosson. It is based off his early work and leverages the [Oklab](./oklab.md) color
space. The aim was to create a color space that was better suited for being used in color pickers than the current HSV.

_[Learn about Okhsv](https://bottosson.github.io/posts/colorpicker/)_
</div>

??? abstract "ColorAide Details"

## Channel Aliases

Channels    | Aliases
----------- | -------
`h`         | `hue`
`s`         | `saturation`
`v`         | `value`

## Input/Output

Okhsv is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --okhsv`:

```css-color
color(--okhsv h s l / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("okhsv", [0, 0, 0], 1)
```

The string representation of the color object and the default string output use the
`#!css-color color(--okhsv h s l / a)` form.

```playground
Color("okhsv", [29.234, 1, 1])
Color("okhsv", [70.67, 1, 1]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.okhsv import Okhsv

class Color(Base): ...

Color.register(Okhsv())
```
