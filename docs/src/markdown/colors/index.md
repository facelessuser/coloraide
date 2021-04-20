# Supported Colors

## sRGB

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `srgb`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

sRGB is a standard RGB (red, green, blue) color space that HP and Microsoft created cooperatively in 1996 to use on
monitors, printers, and the Web. SRGB stands for "Standard RGB". It is the most widely used color space and is supported
by most operating systems, software programs, monitors, and printers.

_[Learn about sRGB](https://en.wikipedia.org/wiki/SRGB)_
</div>

## HSV

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `hsv`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    hue        | 0 - 360
    saturation | 0 - 100
    value      | 0 - 100

HSV is a color space similar to the modern [RGB](#srgb) and CMYK models. The HSV color space has three components: hue,
saturation and value. 'Value' is sometimes substituted with 'brightness' and then it is known as HSB. HSV represents
models how colors appear under light.

_[Learn about HSV](https://en.wikipedia.org/wiki/HSL_and_HSV)_
</div>

## HSL

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `hsl`

    **White Point:**   D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    hue        | 0 - 360
    saturation | 0 - 100
    lightness  | 0 - 100

HSL is an alternative representations of the [RGB](#srgb) color model, designed in the 1970s by computer graphics
researchers to more closely align with the way human vision perceives color-making attributes. In these models, colors
of each hue are arranged in a radial slice, around a central axis of neutral colors which ranges from black at the
bottom to white at the top.

HSL models the way different paints mix together to create color in the real world, with the lightness dimension
resembling the varying amounts of black or white paint in the mixture.

_[Learn about HSL](https://en.wikipedia.org/wiki/HSL_and_HSV)_
</div>

## HWB

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `hwb`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    hue        | 0 - 360
    whiteness  | 0 - 100
    blackness  | 0 - 100

HWB is a cylindrical-coordinate representation of points in an [RGB](#srgb) color model, similar to HSL and HSV. It was
developed by [HSV](#hsv)'s creator Alvy Ray Smith in 1996 to address some of the issues with HSV. HWB was designed to be
more intuitive for humans to use and slightly faster to compute. The first coordinate, H (Hue), is the same as the Hue
coordinate in [HSL](#hsl) and [HSV](#hsv). W and B stand for Whiteness and Blackness respectively and range from 0-100%
(or 0-1). The mental model is that the user can pick a main hue and then "mix" it with white and/or black to produce the
desired color.

_[Learn about HWB](https://en.wikipedia.org/wiki/HWB_color_model)_
</div>

## Display P3

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `display-p3`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

Display P3 is a combination of the DCI-P3 color gamut with the D65 white point together with the [sRGB](#srgb) gamma
curve. It originated from the DCI-P3 color gamut's implementation in digital cinema projectors, as this standard offers
more vibrant greens and reds than the traditional [sRGB](#srgb) color gamut.

_[Learn about Display P3](https://en.wikipedia.org/wiki/DCI-P3#Display_P3)_
</div>

## A98 RGB

<div class="info-container" markdown="1">

!!! info inline end "Properties"

    **Identifier:** `a98-rgb`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

The Adobe RGB (1998) color space or opRGB is a color space developed by Adobe Systems, Inc. in 1998. It was designed to
encompass most of the colors achievable on CMYK color printers, but by using [RGB](#srgb) primary colors on a device
such as a computer display. The Adobe RGB (1998) color space encompasses roughly 50% of the visible colors specified by
the [CIELAB](#cielab) color space - improving upon the gamut of the [sRGB](#srgb) color space, primarily in cyan-green
hues.

_[Learn about A98 RGB](https://en.wikipedia.org/wiki/Adobe_RGB_color_space)_
</div>

## REC.2020

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `rec2020`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

The Rec. 2020 color space is a result of this and is a very wide gamut RGB color space which is used in 4k and 8k UHDTV.
ITU-R Recommendation BT.2020, more commonly known by the abbreviations Rec. 2020 or BT.2020, defines various aspects of
ultra-high-definition television (UHDTV) with standard dynamic range (SDR) and wide color gamut (WCG), including picture
resolutions, frame rates with progressive scan, bit depths, color primaries, RGB and luma-chroma color representations,
chroma subsamplings, and an opto-electronic transfer function.

_[Learn about REC.2020](https://en.wikipedia.org/wiki/Rec._2020)_
</div>

## ProPhoto

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `prophoto-rgb`

    **White Point:** D50

    **Coordinates:**

    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

The ProPhoto RGB color space, also known as ROMM RGB (Reference Output Medium Metric), is an output referred RGB color
space developed by Kodak. It offers an especially large gamut designed for use with photographic output in mind. The
ProPhoto RGB color space encompasses over 90% of possible surface colors in the [CIE L\*a\*b\*](#cielab) color space,
and 100% of likely occurring real-world surface colors documented by Pointer in 1980.

_[Learn about ProPhoto](https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space)_
</div>

## XYZ

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `xyz`

    **White Point:** D50

    **Coordinates:**

    Name       | Range
    ---------- | -----
    x          | 0 - 1
    y          | 0 - 1
    z          | 0 - 1

The CIE 1931 RGB color space and CIE 1931 XYZ color space were created by the International Commission on Illumination
(CIE) in 1931. They resulted from a series of experiments done in the late 1920s by William David Wright using ten
observers and John Guild using seven observers. The experimental results were combined into the specification of the
CIE RGB color space, from which the CIE XYZ color space was derived. The CIE 1931 color spaces are the first defined
quantitative links between distributions of wavelengths in the electromagnetic visible spectrum, and physiologically
perceived colors in human color vision.

_[Learn about XYZ](https://en.wikipedia.org/wiki/CIE_1931_color_space)_
</div>

## XYZ D65

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `xyz-d65`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    x          | 0 - 1
    y          | 0 - 1
    z          | 0 - 1

XYZ D65 is the same as [XYZ](#xyz) except it uses a D65 white point.

_[Learn about XYZ](https://en.wikipedia.org/wiki/CIE_1931_color_space)_
</div>

<style>
.info-container { overflow: hidden; }
.info-container .admonition.inline.end {
    margin-right: 0.5rem;
}
</style>

## CIELAB

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `lab`

    **White Point:** D50

    **Coordinates:**

    Name       | Range
    ---------- | -----
    lightness  | 0 - 100
    a          | -160 - 160
    b          | -160 - 160

The CIELAB color space also referred to as L\*a\*b\* is a color space defined by the International Commission on
Illumination (abbreviated CIE) in 1976. It expresses color as three values: L\* for perceptual lightness, and a\* and
b\* for the four unique colors of human vision: red, green, blue, and yellow. CIELAB was intended as a perceptually
uniform space, where a given numerical change corresponds to similar perceived change in color. While the CIELAB space
is not truly perceptually uniform, it nevertheless is useful in industry for detecting small differences in color.

_[Learn about CIELAB](https://en.wikipedia.org/wiki/CIELAB_color_space)_
</div>

## CIELCH

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `lch`

    **White Point:** D50

    **Coordinates:**

    Name       | Range
    ---------- | -----
    lightness  | 0 - 100
    chroma     | 0 - 100
    hue        | 0 - 360

The "CIELCH" or "CIEHLC" space is a color space based on [CIELAB](#cielab), which uses the polar coordinates C\*
(chroma, relative saturation) and h&deg; (hue angle, angle of the hue in the CIELAB color wheel) instead of the Cartesian
coordinates a\* and b\*. The CIELAB lightness L\* remains unchanged.

_[Learn about CIELCH](https://en.wikipedia.org/wiki/CIELAB_color_space#Cylindrical_representation:_CIELCh_or_CIEHLC)_
</div>

## CIELAB D65

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `lab-d65`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    lightness  | 0 - 100
    a          | -160 - 160
    b          | -160 - 160

CIELAB D65 is the same as [CIELAB](#cielab) except it uses a D65 white point.

_[Learn about CIELAB](https://en.wikipedia.org/wiki/CIELAB_color_space)_
</div>

## CIELCH D65

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `lch-d65`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    lightness  | 0 - 100
    chroma     | 0 - 100
    hue        | 0 - 360

CIELCH D65 is the same as [CIELCH](#cielch) except it uses a D65 white point.

_[Learn about CIELCH](https://en.wikipedia.org/wiki/CIELAB_color_space#Cylindrical_representation:_CIELCh_or_CIEHLC)_
</div>

## Oklab

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `oklab`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    lightness  | 0 - 1
    a          | -0.5 - 0.5
    b          | -0.5 - 0.5

A new perceptual color space that claims to be simple to use, while doing a good job at predicting perceived lightness,
chroma and hue. It is called the Oklab color space, because it is an OK Lab color space.

_[Learn about Oklab](https://bottosson.github.io/posts/oklab/)_
</div>

## Oklch

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `oklch`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    lightness  | 0 - 1
    chroma     | 0 - 1
    hue        | 0 - 360

Oklch is the cylindrical form of [Oklab](#oklab).

_[Learn about Oklch](https://bottosson.github.io/posts/oklab/)_
</div>

## Jzazbz

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `jzazbz`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    lightness  | 0 - 1
    a          | -0.5 - 0.5
    b          | -0.5 - 0.5

Jzazbz is a a color space designed for perceptual uniformity in high dynamic range (HDR) and wide color gamut (WCG)
applications. Conceptually it is similar to [CIELAB](#cielab), but claims the following improvements:

- Perceptual color difference is predicted by Euclidean distance.
- Perceptually uniform: MacAdam ellipses of just-noticeable-difference (JND) are more circular, and closer to the same
  sizes.
- Hue linearity: changing saturation or lightness has less shift in hue.

_[Learn about Jzazbz](https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272)_
</div>

## JzCzhz

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `jzczhz`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    lightness  | 0 - 1
    chroma     | 0 - 1
    hue        | 0 - 360

JzCzhz is the cylindrical form of [Jzazbz](#jzazbz).

_[Learn about JzCzhz](https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272)_
</div>

## ICtCp

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Identifier:** `ictcp`

    **White Point:** D65

    **Coordinates:**

    Name       | Range
    ---------- | -----
    i          | 0 - 1
    ct         | -0.5 - 0.5
    cp         | -0.5 - 0.5

ICtCp is a color space format with better perceptual uniformity than [CIELAB](#cielab) and is used as a part of the
color image pipeline in video and digital photography systems for high dynamic range (HDR) and wide color gamut (WCG)
imagery. It was developed by Dolby Laboratories from the IPT color space by Ebner and Fairchild. It was designed with
the intention to replace YCbCr.

_[Learn about ICtCp](https://en.wikipedia.org/wiki/ICtCp)_
</div>
