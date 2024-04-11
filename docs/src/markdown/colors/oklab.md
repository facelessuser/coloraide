# Oklab

/// success | The Oklab color space is registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `oklab`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range^\*^
---- | ---------
`l`  | [0, 1]
`a`  | [-0.4, 0.4]
`b`  | [-0.4, 0.4]

^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
relation to the Display P3 color space.
////

//// html | figure
![Oklab](../images/oklab-3d.png)

///// html | figcaption
The sRGB gamut represented within the Oklab color space.
/////
////


A perceptual color space that models the opponent color signals which the eye sends to the brain - lightness v. darkness, or "brightness" (L), red v. green (a), and yellow v. blue-violet (b). It is called the Oklab color space, because it is an OK Lab color space.

_[Learn about Oklab](https://bottosson.github.io/posts/oklab/)_
///

## Channel Aliases

Channels | Aliases
-------- | -------
`l`      | `lightness`
`a`      |
`b`      |

## Input/Output

Oklab was introduce in [CSS colors level 4](https://drafts.csswg.org/css-color/#ok-lab).  I can be parsed via the
`#!css-color oklch()` function format, with relative Oklch colors being introduced in [CSS colors level 5](https://drafts.csswg.org/css-color-5/#relative-Oklab):

```css-color
oklab(l a b / a)          // Oklab function
oklab(from <color> l a b / a)          // Oklab relative color function
color(--oklab l a b / a)  // Color function with custom color space
```

When using `oklab` as a custom color space when manually creating a color via raw data or specifying a color space as a parameter in a function, the color
space name is always used:

```py
Color("oklab", [0, 0, 0], 1)
```

When using this custom color space, the string representation of the color object will always default to the `#!css-color color(--oklab l a b / a)`
form, but the default string output will be the `#!css-color oklab(l a b / a)` form.

```py play
Color("oklab", [0.62796, 0.22486, 0.12585])
Color("oklab", [0.79269, 0.05661, 0.16138]).to_string()
Color("oklab", [0.96798, -0.07137, 0.19857]).to_string(percent=True)
Color("oklab", [0.51975, -0.1403, 0.10768]).to_string(color=True)
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.oklab import Oklab

class Color(Base): ...

Color.register(Oklab())
```
