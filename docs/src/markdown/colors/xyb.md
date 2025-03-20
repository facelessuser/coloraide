# XYB

/// failure | The XYB color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `xyb`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range^\*^
---- | -----
`x`  | [-0.05, 0.05]
`y`  | [0.0, 0.845]
`b`  | [-0.45, 0.45]

^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs.
////

![XYB](../images/xyb-3d.png)
//// figure-caption
The sRGB gamut represented within the XYB color space.
////

XYB is a color space that was designed for use with the JPEG XL Image Coding System. It is an LMS-based color model
inspired by the human visual system, facilitating perceptually uniform quantization. It uses a gamma of 3 for
computationally efficient decoding.

//// tip | Chroma/Luma Adjustments
Per the creator, the default subtracts the Y component from the B component which makes Y function as lightness and X
and B will function similar to Lab 'a' and 'b' components. When X=Y=0, the color is achromatic.

You may find other implementations may not do this and store the colors without this operation. It may be that in real
world use it is not stored in this way. If desired, you can add Y to B to get the color exactly as specified in the
white paper.

While in this configuration the color operates in a Lab-like way, but the scaling of X and B is quite different not
making it practical to convert this to a LCh-like space for reasonable hue values. To do so, you would need to scale X
to a similar order of magnitude compared to B (maybe a factor of 10).
////

[Learn more](https://ds.jpeg.org/whitepapers/jpeg-xl-whitepaper.pdf).
///

## Channel Aliases

Channels | Aliases
-------- | -------
`x`      |
`y`      |
`b`      |

**Inputs**

The XYB space is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --xyb`:

```css-color
color(--xyb x y b / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--xyb x y b / a)` form.

```py play
Color("xyb", [0.0281, 0.48819, -0.01653])
Color("xyb", [0.01132, 0.64596, -0.1149]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.xyb import XYB

class Color(Base): ...

Color.register(XYB())
```
