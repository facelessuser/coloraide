# sCAM JMh

> [!failure] The sCAM JMh color space is not registered in `Color` by default

/// html | div.info-container
> [!info | inline | end] Properties
> **Name:** `scam-jmh`
>
> **White Point:** D65 / 2˚
>
> **Coordinates:**
>
> Name | Range^\*^
> ---- | -----
> `j`  | [0, 100]
> `m`  | [0, 25]
> `h`  | [0, 360)
>
> ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
> relation to the Display P3 color space.

![sCAM JMh](../images/scam-jmh-3d.png)
//// figure-caption
The sRGB gamut represented within the sCAM JMh color space.
////

A color appearance model (CAM) is a mathematical model that seeks to describe the perceptual aspects of human color
vision, i.e. viewing conditions under which the appearance of a color does not tally with the corresponding physical
measurement of the stimulus source.

The simple Color Appearance Model (sCAM) is a CAM model that is built on top of the simple Uniform Color Space (sUCS)
whose structure is based on that of [IPT](./ipt.md) and [CAM16-UCS](./cam16-ucs.md) for their hue linearity, and
space uniformity, respectively. The model has a simple structure but provides comprehensive functions for color related
applications.

The model defines numerous different attributes:

Name | Description
---- | -----------
J    | Lightness
C    | Chroma
h    | hue
Q    | Brightness
M    | Colorfulness
D    | Saturation
V    | Vividness
W    | Whiteness
K    | Blackness
H    | Hue Quadrature

A color space can be constructed by using a subset of these attributes: JMh, JCh, QMh, etc. The provided color
spaces uses JMh.

[Learn more](https://opg.optica.org/oe/fulltext.cfm?uri=oe-29-4-6036&id=447640).
///

## Viewing Conditions

sCAM is a color appearance model and can be configured with different viewing environments. An sCAM color space will
also have an associated environment object. This environment object determines the viewing conditions. Colors will
appear different based on the viewing conditions.

Viewing\ Conditions    | Description
---------------------- | -----------
White                  | This is the white point and output white and should be the same as defined in the color class. This is provided as (x, y) chromaticity coordinates. sCAM expects and was designed for this to be D65.
Adapting\ Luminance    | The luminance of the adapting field (`La`). The units are in cd/m2.
Background\ Luminance  | The background luminance (`Yb`) the relative luminance of the nearby background (out to 10°), relative to the reference white's luminance (`Y`).
Surround               | A description of the peripheral area. Use "dark" for a movie theater, "dim" for e.g. viewing a bright television in a dimly lit room, or "average" for surface colors.
Discounting            | Discounts the illuminant. If true, the eye is assumed to be fully adapted to the illuminant. Otherwise, the degree of discounting is based on other parameters. When the eye is not fully adapted, it can affect the way colors appear and the chromatic response.

ColorAide must provide some defaults, so sCAM comes with a default set of viewing conditions that uses a D65 white
point, an adapting luminance of 64 lux or a value of ~4 cd/m^2^, it uses the "gray world" assumption and sets the
background to 20, an "average" surround and leaves discounting set to `#!py False`.

The default settings do not have to be used and a new sCAM variant with different viewing conditions can be created.
When doing this, the space should be derived from the default

```py play
from coloraide import Color as Base
from coloraide.spaces.scam import sCAMJMh, Environment
from coloraide.cat import WHITES
from coloraide import util
import math

cdm2 = 1000 / math.pi

class CustomSCAMJMh(sCAMJMh):
    NAME = "scam-custom"
    SERIALIZE = ("--scam-custom",)
    WHITE = WHITES['2deg']['D65']
    ENV = Environment(
        white=WHITE,
        adapting_luminance=cdm2,
        background_luminance=100,
        surround='average',
        discounting=False
    )

class Color(Base): ...

Color.register([sCAMJMh(), CustomSCAMJMh()])

Color('red').convert('scam-jmh')
Color('red').convert('scam-custom')
```

## Channel Aliases

Channels | Aliases
-------- | -------
`j`      | `lightness`
`m`      | `colorfulness`
`h`      | `hue`

## Input/Output

The sCAM JMh space is not currently supported in the CSS spec, the parsed input and string output formats use the
`#!css-color color()` function format using the custom name `#!css-color --scam-jmh`:

```css-color
color(--scam-jmh j m h / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--scam-jmh j m h / a)` form.

```py play
Color("scam-jmh", [54.635, 15.852, 29.937], 1)
Color("scam-jmh", [74.208, 11.547, 67.919], 1).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.scam import sCAMJMh

class Color(Base): ...

Color.register(sCAMJMh())
```
