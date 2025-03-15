# CAM02 JMh

/// failure | The CAM16 JMh color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `cam02-jmh`

**White Point:** D65 / 2˚

**Coordinates:**

Name | Range^\*^
---- | -----
`j`  | [0, 100]
`m`  | [0, 120]
`h`  | [0, 360)

^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
relation to the Display P3 color space.
////

![CAM16 JMh](../images/cam02-jmh-3d.png)
//// figure-caption
The sRGB gamut represented within the CAM02 JMh color space.
////

A color appearance model (CAM) is a mathematical model that seeks to describe the perceptual aspects of human color
vision, i.e. viewing conditions under which the appearance of a color does not tally with the corresponding physical
measurement of the stimulus source.

CAM02 is a successor of CIECAM97s with various fixes and improvements. The model actually defines numerous different
attributes:

Name | Description
---- | -----------
J    | Lightness
C    | Chroma
h    | hue
s    | saturation
Q    | Brightness
M    | Colorfulness
H    | Hue Quadrature

A color space can be constructed of using a subset of these attributes: JCh, JMh, Jsh, QCh, QMh, Qsh, etc. You can also
construct Lab like spaces taking using the hue and either C, M, or s. The `cam02-jmh` color space in ColorAide
represents the JMh configuration.

[Learn more](https://www.researchgate.net/publication/221501922_The_CIECAM02_color_appearance_model).
///

## Viewing Conditions

CAM02 is a color appearance model and can be configured with different viewing environments. A CAM02 color space will
also have an associated environment object. This environment object determines the viewing conditions. Colors will
appear different based on the viewing conditions.

Viewing\ Conditions    | Description
---------------------- | -----------
White                  | This is the white point and should be the same as defined in the color class. This is provided as (x, y) chromaticity coordinates.
Adapting\ Luminance    | The luminance of the adapting field (`La`). The units are in cd/m2.
Background\ Luminance  | The background luminance (`Yb`) the relative luminance of the nearby background (out to 10°), relative to the reference white's luminance (`Y`). Usually 20 providing a gray world assumption.
Surround               | A description of the peripheral area. Use "dark" for a movie theater, "dim" for e.g. viewing a bright television in a dimly lit room, or "average" for surface colors.
Discounting            | Discounts the illuminant. If true, the eye is assumed to be fully adapted to the illuminant. Otherwise, the degree of discounting is based on other parameters. When the eye is not fully adapted, it can affect the way colors appear and the chromatic response.

ColorAide must provide some defaults, so CAM02 comes with a default set of viewing conditions that uses a D65 white
point, an adapting luminance of 64 lux or a value of ~4 cd/m^2^, it uses the "gray world" assumption and sets the
background to 20, an "average" surround and leaves discounting set to `#!py False`. Variants such as
[CAM02 UCS](./cam02_ucs.md), [CAM02 SCD](./cam02_scd.md), and [CAM02 LCD](./cam02_lcd.md) assume these same defaults.

The default settings do not have to be used and a new CAM16 variant with different viewing conditions can be created.
When doing this, the space should be derived from the default. A UCS variant would be derived from their defaults, etc.

```py play
from coloraide import Color as Base
from coloraide.spaces.cam02 import CAM02JMh, Environment
from coloraide.cat import WHITES
from coloraide import util
import math

class CustomCAM02JMh(CAM02JMh):
    NAME = "cam02-custom"
    SERIALIZE = ("--cam02-custom",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(
        white=WHITE,
        adapting_luminance=1000 / math.pi,
        background_luminance=20,
        surround='average',
        discounting=False
    )

class Color(Base): ...

Color.register([CAM02JMh(), CustomCAM02JMh()])

Color('white').convert('cam02-jmh')
Color('white').convert('cam02-custom')
```

/// note
It can be noted in the above example that white does not have the typical zero chroma. This is because the eye is not
assumed as being fully adapted to the environment. Due to the environment, the colors considered achromatic may appear
differently.

If `discounting` was enabled, the eye is then assumed to be fully adapted, and achromatic colors would align better with
expectations in other color spaces.
///

## Channel Aliases

Channels | Aliases
-------- | -------
`j`      | `lightness`
`m`      | `colorfulness`
`h`      | `hue`

## Input/Output

The CAM16 JMh space is not currently supported in the CSS spec, the parsed input and string output formats use
the `#!css-color color()` function format using the custom name `#!css-color --cam02-jmh`:

```css-color
color(--cam02-jmh j m h / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--cam02-jmh j m h / a)` form.

```py play
Color("cam02-jmh", [46.931, 80.436, 32.157], 1)
Color("cam02-jmh", [68.929, 48.62, 72.359], 1).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.cam02 import CAM02JMh

class Color(Base): ...

Color.register(CAM02JMh())
```
