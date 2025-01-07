# RLAB

/// failure | The RLAB color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `rlab`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range
---- | -----
`l`  | [0, 100]
`a`  | [-125, 125]
`b`  | [-125, 125]

^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
relation to the Display P3 color space.
////

![RLAB](../images/rlab-3d.png)
//// figure-caption
The sRGB gamut represented within the RLAB color space.
////

The RLAB color-appearance space was developed by Fairchild and Berns for cross-media color reproduction applications in
which images are reproduced with differing white points, luminance levels, and/or surrounds.

ColorAide provides RLAB by default with average surround, and discounting set to "hard copy" (or full discounting of the
illuminant). It is also configured to use an absolute adapting luminance of 318 cd/m2.

[Learn more](https://scholarworks.rit.edu/cgi/viewcontent.cgi?article=1153&context=article).
///

## Viewing Conditions

RLAB can be configured with different viewing environments. An RLAB color space will also have an associated environment
object. This environment object determines the viewing conditions. Colors will appear different based on the viewing
conditions.

Viewing\ Conditions    | Description
---------------------- | -----------
`white`                | This is the white point and should be the same as defined in the color class. This is provided as (x, y) chromaticity coordinates.
`adapting_luminance`   | The luminance of the adapting field (often known as `La`). The units are in cd/m2.
`surround`             | A description of the peripheral area. Use "dark" for a movie theater, "dim" for e.g. viewing a bright television in a dimly lit room, or "average" for surface colors.
`discounting`          | Degree of discounting of the illuminant. A string of either "hard-copy", "projected-transparency", or "soft-copy". Hard copy indicates full discount, or the eye is assumed to be fully adapted to the illuminant. Projected transparency performs 50% discount.

ColorAide must provide some defaults, so the RLAB space has a default set of viewing conditions that uses a D65 white
point, an adapting luminance of 1000 lux or a value of ~318.31 cd/m^2^, an "average" surround, and sets discounting to
"hard-copy". These are the same settings that were demonstrated in the original paper.

These settings do not have to be used, and a new RLAB variant with different viewing conditions can be created. When
doing this, the space should be derived from the default RLAB space.

```py play
from coloraide import Color as Base
from coloraide.spaces.rlab import RLAB, Environment
from coloraide.cat import WHITES
from coloraide import util
import math

class CustomRLAB(RLAB):
    NAME = "rlab-custom"
    SERIALIZE = ("--rlab-custom",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(
        white=WHITE,
        adapting_luminance=64 / math.pi * 0.2,
        surround='average',
        discounting="soft-copy"
    )

class Color(Base): ...

Color.register([RLAB(), CustomRLAB()])

Color('white').convert('rlab')
Color('white').convert('rlab-custom')
```

/// note
If a `discounting` of anything other than "hard-copy" is used, you will notice the achromatic response to cause colors
like white to not have value of zero chroma. This is because the eye is not fully adapted, and colors appear different
with this context. This is not a bug, just the way viewing conditions can affect model.
///

## Channel Aliases

Channels | Aliases
-------- | -------
`l`      | `lightness`
`a`      |
`b`      |

## Input/Output

The RLAB space is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --rlab`:

```css-color
color(--rlab l a b / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--rlab l a b / a)` form.

```py play
Color("rlab", [51.012, 79.742, 57.26])
Color("rlab", [72.793, 25.151, 74.11]).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.rlab import RLAB

class Color(Base): ...

Color.register(RLAB())
```
