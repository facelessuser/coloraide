# ACEScct

!!! failure "The ACEScc color space is not registered in `Color` by default"

<div class="info-container" markdown>
!!! info inline end "Properties"

    **Name:** `acescct`

    **White Point:** D60

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [-0.3584,\ 1.468]
    `g`  | [-0.3584,\ 1.468]
    `b`  | [-0.3584,\ 1.468]

    ^\*^ Ranges are approximate and rounded to 3 decimal places.

ACEScct is very similar to [ACEScc](./acescc.md) except that it adds a "toe" or a gamma curve in the dark region of the
color space. This encoding is more appropriate for legacy color correction operators.

_[Learn about ACEScct](https://docs.acescentral.com/specifications/acescct/)_

</div>

## Channel Aliases

Channels | Aliases
-------- | -------
`r`      | `red`
`g`      | `green`
`b`      | `blue`

## Inputs/Output

ACEScct is not supported via the CSS spec and the parser input and string output only supports the
`#!css-color color()` function format using the custom name `#!css-color --acescct`:

```css-color
color(--acescct r g b / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("acescct", [1, 0, 0], 1)
```

The string representation of the color object and the default string output will be in the
`#!css-color color(--acescct r g b / a)` form.

```playground
Color("acescct", [0.51451, 0.33604, 0.23515])
Color("acescct", [0.53009, 0.48237, 0.32561]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.acescct import ACEScct

class Color(Base): ...

Color.register(ACEScct())
```
