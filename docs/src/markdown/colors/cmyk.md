# CMYK

!!! failure "The CMYK color space is not registered in `Color` by default"

<div class="info-container" markdown>
!!! info inline end "Properties"

    **Name:** `cmyk`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `c`  | [0, 1]
    `m`  | [0, 1]
    `y`  | [0, 1]
    `k`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

The CMYK color model is a just like [CMY](./cmy.md) except that it adds an additional channel `k` to control blackness.

The CMYK color space, as ColorAide Extras has chosen to implement it, is directly calculated from the sRGB color space,
and as such, is based off the sRGB primaries.

[Learn more](https://en.wikipedia.org/wiki/CMY_color_model).
</div>

## Channel Aliases

Channels | Aliases
-------- | -------
`c`      | `cyan`
`m`      | `magenta`
`y`      | `yellow`
`k`      | `black`

## Input/Output

CMY is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --cmyk`:

```css-color
color(--cmyk c m y k / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--cmyk c m y k / a)` form.

```playground
Color("cmyk", [0, 1, 1, 0])
Color("cmyk", [0, 0.35294, 1, 0]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.cmyk import CMYK

class Color(Base): ...

Color.register(CMYK())
```
