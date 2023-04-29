# HCT

/// failure | The HCT color space is not registered in `Color` by default
///

/// html | div.info-container
//// info | Properties
    attrs: {class: inline end}

**Name:** `hct`

**White Point:** D65

**Coordinates:**

Name | Range^\*^
---- | -----
`h`  | [0, 360)
`c`  | [0, 145]
`t`  | [0, 100]

^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
relation to the Display P3 color space.
////

//// html | figure
![HCT](../images/hct-3d.png)

///// html | figcaption
The sRGB gamut represented within the HCT color space.
/////
////

The HCT color space is Google's attempt at a perceptually accurate color system. Essentially, it is two color spaces
glued together. 'H' (hue) and 'C' (chroma) come from the CAM16 color appearance model and 'T' (tone) is the lightness
from the CIELAB (D65) color space. The idea was to take the more consistent perceptual hues from CAM16 and use the
better lightness prediction found in CIELAB, so a new space was created by literally sticking the components together.

In general, CAM16 is not a cheap color space to calculate, and all the glue to hold the components together makes it a
bit more expensive, but considering the use case that it was designed for, creating better color schemes with decent
contrast, it has attractive benefits.

[Learn more](https://material.io/blog/science-of-color-design).
///

## Channel Aliases

Channels | Aliases
-------- | -------
`h`      | `hue`
`c`      | `chroma`
`t`      | `tone`, `lightness`

## Input/Output

The HCT space is not currently supported in the CSS spec, the parsed input and string output formats use
the `#!css-color color()` function format using the custom name `#!css-color --hct`:

```css-color
color(--hct h c t / a)  // Color function
```

The string representation of the color object and the default string output use the
`#!css-color color(--hct h c t / a)` form.

```py play
Color("hct", [27.41, 113.36, 53.237], 1)
Color("hct", [71.257, 60.528, 74.934], 1).to_string()
```

## Registering

```py
from coloraide import Color as Base
from coloraide.spaces.hct import HCT

class Color(Base): ...

Color.register(HCT())
```

## Tonal Palettes

One of the applications of HCT is generating tonal palettes. When coupled with ColorAide's [∆E~hct~](../distance.md#delta-e-hct)
distancing algorithm and the [`hct-chroma` gamut mapping algorithm](../gamut.md#hct-chroma), we can produce tonal
palettes just like in Material's color utilities.

```py play
c = Color('hct', [325, 24, 50])
tones = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
Steps([c.clone().set('tone', tone).convert('srgb').to_string(hex=True, fit='hct-chroma') for tone in tones])
```

Results in our library may be slightly different in some cases when compared to Material's color utilities output. This
is because we have implemented the color space as _described_, but we did not port their implementation or tools as
their approach did not fit our goals, so we do not share the exact same quirks of their implementation.

Material's color utilities force HCT colors to specific chroma steps giving their implementation a lower resolution of
chroma. They also limit their implementation to the sRGB color space. Additionally, Material uses different precision
for their transformation matrices between sRGB and XYZ.

In contrast, ColorAide implements HCT as a normal color space and does not enforce artificial chroma steps. ColorAide
also does not clamp translations to the sRGB gamut and employs a generalized method to convert from HCT to sRGB and
other color space gamuts. This means we can generate tonal palettes in wide gamut color spaces as well.

```py play
tones = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
c1 = Color('display-p3', [1, 0, 1]).convert('hct')
Steps([c1.clone().set('tone', tone).convert('display-p3').to_string(fit='hct-chroma') for tone in tones])
c2 = Color('rec2020', [0, 0, 1]).convert('hct')
Steps([c2.clone().set('tone', tone).convert('rec2020').to_string(fit='hct-chroma') for tone in tones])
```

/// note | Conversion from HCT
HCT will convert from HCT nicely in a number of gamuts, but some extremes in some gamuts may give it a difficult time.
For instance, ProPhoto, which has regions outside of the viewable spectrum, has regions where round tripping can get
drop and accurate color conversion can become difficult. This could be improved with tweaks to the algorithm and even
more iterations at the cost of performance. For now, we've instead opted to optimize for the more reasonable gamuts:
sRGB, Display P3, Rec2020, etc. It is possible in the future we may be able to further optimize this process with lookup
tables and other approaches.
///

Since ColorAide has a different chroma resolution and transformation precision than Material's color utilities, the
results for tonal palettes are sometimes slightly different, but for all intents and purposes the same. Even though
there can sometimes be subtle differences, the eye will generally have difficulties perceiving those differences.
ColorAide did not set out to port the Material color utilities but to give access the the HCT color space generally.

Below we have two examples. We've taken the results from Material's tests and we've generated the same tonal palettes
and output both as HCT. We can compare which hues stay overall more constant, which chroma gets reduced more than
others, and which hue and tone are less affected by the gamut mapping. Can you definitively say that one looks more
correct than the other?

```py play
def tonal_palette(c):
    tones = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
    return [c.clone().set('tone', tone).fit('srgb', method='hct-chroma') for tone in tones]

material1 = ['#000000', '#00006e', '#0001ac',
             '#0000ef', '#343dff', '#5a64ff',
             '#7c84ff', '#9da3ff', '#bec2ff',
             '#e0e0ff', '#f1efff', '#ffffff']
c = Color('blue').convert('hct')
Steps([x.to_string() for x in tonal_palette(c)])
Steps([Color(x).convert('hct').to_string() for x in material1])

material2 = ['#000000', '#191a2c', '#2e2f42',
             '#444559', '#5c5d72', '#75758b',
             '#8f8fa6', '#a9a9c1', '#c5c4dd',
             '#e1e0f9', '#f1efff', '#ffffff']
c['chroma'] = 16
Steps([x.to_string() for x in tonal_palette(c)])
Steps([Color(x).convert('hct').to_string() for x in material2])
```
