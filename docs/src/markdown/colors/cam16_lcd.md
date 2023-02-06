# CAM16 LCD

!!! failure "The CAM16 LCD color space is not registered in `Color` by default"

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `cam16-lcd`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `j`  | [0, 100]
    `a`  | [-75, 75]
    `b`  | [-75, 75]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown>

![CAM16 LCD](../images/cam16-lcd.png)

<figcaption markdown>
The sRGB gamut represented within the CAM16 LCD color space.
</figcaption>
</figure>

This is the LCD variant of the CAM16 UCS color space and is optimized for "large" color distancing. See
[CAM16 UCS](./cam16_ucs.md) for more info.

[Learn more](https://doi.org/10.1002/col.22131).
</div>

## Channel Aliases

Channels | Aliases
-------- | -------
`j`      | `lightness`
`a`      |
`b`      |

## Input/Output

The CAM16 LCD space is not currently supported in the CSS spec, the parsed input and string output formats use
the `#!css-color color()` function format using the custom name `#!css-color --cam16-lcd`:

```css-color
color(--cam16-lcd j a b / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--cam16-lcd j a b / a)` form.

```playground
Color("cam16-lcd", [46.026, 81.254, 27.393], 1)
Color("cam16-lcd", [68.056, 43.51, 71.293], 1).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide_extras.spaces.cam16_ucs import CAM16LCD

class Color(Base): ...

Color.register(CAM16LCD())
```

<style>
.info-container {display: inline-block;}
</style>

## Subclassing

CAM16 LCD is a color model that can vary due to viewing conditions. Factors such as coefficients used (UCS/LCD/LCD),
surround (average/dim/dark), adapting luminance, background luminance, white point, and whether the eye is assumed to be
fully adapted to the illuminant can all play into how the color model responds.

If it is desired to create a CAM16 LCD that uses different viewing conditions, the `CAM16LCD` class can be subclassed.
A new `Environment` object should be set to the class describing the viewing conditions. As CAM16 LCD is directly uses
the CAM16 (Jab) color space as its base for conversion, that base would also need to be subclassed with the correct
environment, or the the CAM16 LCD class would need to make the transform directly from XYZ. All the helper functions are
available to pull this off if needed.

When subclassing, always use a new, unique name, like `cam16-custom` as other features or color spaces may depend on the
`cam16-lcd` name converting a certain way.

You can check out the source to learn more.
