# ACEScc

/// failure | The ACEScc color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `acescc`

**White Point:** D60

**Coordinates:**

Name | Range^\*^
---- | -----
`r`  | [-0.0729,\ 1.468]
`g`  | [-0.0729,\ 1.468]
`b`  | [-0.0729,\ 1.468]

^\*^ Ranges are approximate and have been rounded.
////

ACEScc is a color space based on the API primaries and is primarily used for color grading. It is a logarithmic color
space, unlike ACEScg, and maps black at 0 and white at 1.

_[Learn about ACEScc](https://docs.acescentral.com/specifications/acescc/)_

///

## Channel Aliases

Channels | Aliases
-------- | -------
`r`      | `red`
`g`      | `green`
`b`      | `blue`

## Input/Output

ACEScc is not supported via the CSS spec and the parser input and string output only supports the
`#!css-color color()` function format using the custom name `#!css-color --acescc`:

```css-color
color(--acescc r g b / a)  // Color function
```

When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("acescc", [1, 0, 0], 1)
```

The string representation of the color object and the default string output will be in the
`#!css-color color(--acescc r g b / a)` form.

```py play
Color('acescc', [0.51451, 0.33604, 0.23515])
Color('acescc', [0.53009, 0.48237, 0.32561]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.acescc import ACEScc

class Color(Base): ...

Color.register(ACEScc())
```
