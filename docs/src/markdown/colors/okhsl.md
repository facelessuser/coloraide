# Okhsl

/// failure | The Okhsl color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `okhsl`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range
---- | -----
`h`  | [0, 360)
`s`  | [0, 1]
`l`  | [0, 1]
////

//// html | figure
![Okhsl 3D](../images/okhsl-3d.png)

///// html | figcaption
Okhsl color space in 3D
/////
////

Okhsl was created by Björn Ottosson and is a transform of the [Oklab](./oklab.md) color space that approximates the sRGB
gamut perceptually in an HSL color model. The aim was to create a color space that was better suited for being used in
color pickers than the current HSL.

_[Learn about Okhsv](https://bottosson.github.io/posts/colorpicker/)_
///

## Channel Aliases

Channels    | Aliases
----------- | -------
`h`         | `hue`
`s`         | `saturation`
`l`         | `lightness`

## Input/Output

Okhsl is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --okhsl`:

```css-color
color(--okhsl h s l / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("okhsl", [0, 0, 0], 1)
```

The string representation of the color object and the default string output use the
`#!css-color color(--okhsl h s l / a)` form.

```py play
Color("okhsl", [29.234, 1, 0.56808], 1)
Color("okhsl", [70.67, 1, 0.75883], 1).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.okhsl import Okhsl

class Color(Base): ...

Color.register(Okhsl())
```
