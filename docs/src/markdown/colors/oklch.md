# OkLCh

/// success | The OkLCh color space is registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `oklch`

**White Point:** D65 / 2˚ / 2˚

**Coordinates:**

Name | Range^\*^
---- | ---------
`l`  | [0, 1]
`c`  | [0, 0.4]
`h`  | [0, 360)

^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
relation to the Display P3 color space.
////

//// html | figure
![OkLCh](../images/oklch-3d.png)

///// html | figcaption
The sRGB gamut represented within the OkLCh color space.
/////
////


OkLCh is the cylindrical form of [Oklab](./oklab.md).

_[Learn about OkLCh](https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl)_
///

## Channel Aliases

Channels | Aliases
-------- | -------
`l`      | `lightness`
`c`      | `chroma`
`h`      | `hue`

## Input/Output

Oklch was introduce in [CSS colors level 4](https://drafts.csswg.org/css-color/#ok-lab). I can be parsed via the
`#!css-color oklch()` function format, with relative Oklch colors being introduced in [CSS colors level 5](https://drafts.csswg.org/css-color-5/#relative-Oklch):

```css-color
oklch(l c h / a)          // OkLCh function
oklch(from <color> l c h / a) // OkLCh function for relative colors
color(--oklab l a b / a)  // Color function
```

When using the custom color space `--oklab`, the string representation of the color object will always default to the `#!css-color color(--oklch l c h / a)`
form, but the default string output will be the `#!css-color oklch(l a b / a)` form.

```py play
Color("oklch", [0.62796, 0.25768, 29.234])
Color("oklch", [0.79269, 0.17103, 70.67]).to_string()
Color("oklch", [0.96798, 0.21101, 109.77]).to_string(percent=True)
Color("oklch", [0.51975, 0.17686, 142.5]).to_string(color=True)
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.oklch import OkLCh

class Color(Base): ...

Color.register(OkLCh())
```
