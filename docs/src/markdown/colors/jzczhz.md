# JzCzhz

/// success | The JzCzhz color space is registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `jzczhz`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range
---- | -----
`jz` | [0, 1]
`cz` | [0, 0.26]
`hz` | [0, 360)

^\*^ Space is not bound to the defined range above but represents a practical range for HDR color spaces. CSS uses a
range of `jz` = [0, 1] and `cz` = [0, 1] for percentage input and output.
////

![JzCzhz](../images/jzczhz-3d.png)
//// figure-caption
The sRGB gamut represented within the JzCzhz color space.
////

JzCzhz is the cylindrical form of [Jzazbz](./jzazbz.md).

_[Learn about JzCzhz](https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272)_
///

## Channel Aliases

Channels | Aliases
-------- | -------
`jz`     | `lightness`, `j`
`cz`     | `chroma`, `c`
`hz`     | `hue`, `h`

## Input/Output

Parsed input and string output formats support all valid CSS forms in addition to allowing the `#!css-color color()`
function format as well using the custom name `#!css-color --jzczhz`.

```css-color
jzczhz(jz cz hz / a)          // Jzazbz function
color(--jzczhz jz cz hz / a)  // Color function
```

The string representation of the color object will always default to the `#!css-color color(--jzczhz jz cz hz / a)`
form, but the default string output will be the `#!css-color jzczhz(jz cz hz / a)` form.

```py play
Color("jzczhz", [0.13438, 0.16252, 43.502])
Color("jzczhz", [0.16937, 0.12698, 75.776]).to_string()
Color("jzczhz", [0.2096, 0.1378, 102]).to_string(percent=True)
Color("jzczhz", [0.09203, 0.10932, 132.99]).to_string(color=True)
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.jzczhz.css import JzCzhz

class Color(Base): ...

Color.register(JzCzhz())
```
