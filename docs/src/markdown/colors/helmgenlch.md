# Helmgenlch

> [!failure] The Helmgenlch color space is not registered in `Color` by default

/// html | div.info-container
> [!info | inline | end] Properties
> **Name:** `helmgenlch`
>
> **White Point:** D65 / 2˚ (Variant from ASTM-E308)
>
> **Coordinates:**
>
> Name | Range^\*^
> ---- | -----
> `l`  | [0, 1.0]
> `c`  | [0, 0.65]
> `h`  | [0, 360]
>
> ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs.

![Helmgenlch](../images/helmgenlch-3d.png)
//// figure-caption
The sRGB gamut represented within the Helmgenlch color space.
////

Helmlab is a family of purpose-built color spaces, two to be exact. The first is the Helmlab Metric space which is
designed for perceptual distance measurements, claiming STRESS 23.30 on COMBVD - 20% better than CIEDE2000. The second
is the Helmgen space which is designed for gradient and palette generation (60-8 vs Oklab on ColorBench's 83 metrics,
360/360/360 gamut cusps, zero monotonicity violations).

Helmgenlch is the polar form of Helmgen and is the generation-optimized space and is specifically used for
interpolation, palettes, etc. It is the general purpose color space of the Helmlab family.

[Learn more](https://arxiv.org/abs/2602.23010).
///

## Channel Aliases

Channels | Aliases
-------- | -------
`l`      | `lightness`
`c`      | `chroma`
`hue`    | `hue`

**Inputs**

The Helmlab space is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --helmgenlch`:

```css-color
color(--helmgenlch l a b / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--helmgenlch l a b / a)` form.

```py play
Color("helmgenlch", [0.56321, 0.34823, 32.189])
Color("helmgenlch", [0.75752, 0.26718, 72.88]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.helmgenlch import Helmgenlch

class Color(Base): ...

Color.register(Helmgenlch())
```
