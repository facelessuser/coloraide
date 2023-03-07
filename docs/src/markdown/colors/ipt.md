# IPT

/// failure | The IPT color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `ipt`

**White Point:** D65

**Coordinates:**

Name | Range^\*^
---- | -----
`i`  | [0, 1]
`p`  | [-1, 1]
`t`  | [-1, 1]

^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs.
////

//// html | figure
![IPT](../images/ipt-3d.png)

///// html | figcaption
The sRGB gamut represented within the IPT color space.
/////
////

Ebner and Fairchild addressed the issue of non-constant lines of hue in their color space dubbed IPT. The IPT color
space converts D65-adapted XYZ data (XD65, YD65, ZD65) to long-medium-short cone response data (LMS) using an adapted
form of the Hunt-Pointer-Estevez matrix (M~HPE~(D65)).

The IPT color appearance model excels at providing a formulation for hue where a constant hue value equals a constant
perceived hue independent of the values of lightness and chroma (which is the general ideal for any color appearance
model, but hard to achieve). It is therefore well-suited for gamut mapping implementations.

[Learn more](https://www.researchgate.net/publication/21677980_Development_and_Testing_of_a_Color_Space_IPT_with_Improved_Hue_Uniformity.).
///

## Channel Aliases

Channels | Aliases
-------- | -------
`i`      | `intensity`
`p`      | `protan`
`t`      | `tritan`

**Inputs**

The IPT space is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --ipt`:

```css-color
color(--ipt i p t / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--ipt i p t / a)` form.

```py play
Color("ipt", [0.45616, 0.62086, 0.44282])
Color("ipt", [0.64877, 0.189, 0.5303]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.ipt import IPT

class Color(Base): ...

Color.register(IPT())
```
