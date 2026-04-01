# Helmgen

> [!failure] The Helmgen color space is not registered in `Color` by default

/// html | div.info-container
> [!info | inline | end] Properties
> **Name:** `helmgen`
>
> **White Point:** D65 / 2˚ (Variant from ASTM-E308)
>
> **Coordinates:**
>
> Name | Range^\*^
> ---- | -----
> `l`  | [0, ~0.9287]
> `a`  | [-0.4, 0.4]
> `b`  | [-0.4, 0.4]
>
> ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs.

![Helmgen](../images/helmgen-3d.png)
//// figure-caption
The sRGB gamut represented within the Helmgen color space.
////

Helmlab is a family of purpose-built color spaces: MetricSpace (72-parameter enriched pipeline for perceptual distance)
and GenSpace (generation-optimized pipeline for gradients and palettes). MetricSpace achieves STRESS 23.30 on COMBVD
(3,813 color pairs) - a 20.1% improvement over CIEDE2000. GenSpace + arc-length reparameterization produces perfectly
uniform gradients (CV ≈ 0% on any color pair).

Helmgen is the GenSpace and is specifically used for interpolation, palettes, etc. It is the general purpose color space
of the Helmlab family.

[Learn more](https://arxiv.org/abs/2602.23010).
///

## Channel Aliases

Channels | Aliases
-------- | -------
`l`      | `lightness`
`a`      |
`b`      |

**Inputs**

The Helmlab space is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --helmgen`:

```css-color
color(--helmgen l a b / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--helmgen l a b / a)` form.

```py play
Color("helmgen", [0.56358, 0.28763, 0.18093])
Color("helmgen", [0.75771, 0.07633, 0.24769]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.helmgen import Helmgen

class Color(Base): ...

Color.register(Helmgen())
```
