# Color Distance and Delta E

The difference or distance between two colors allows for a quantified analysis of how far apart two colors are from one
another. This metric is of particular interest in the field of color science, but it has practical applications in
color libraries working with colors.

Usually, color distance is applied to near perceptual uniform color spaces in order to obtain a metric regarding a
color's visual, perceptual distance from another color. This can be useful in gamut mapping or even determining that
colors are close enough or far enough away from each other.

## Color Distance

ColorAide provides a simple euclidean color distance function. By default, it evaluates the distance in the CIELab color
space, but it can be configured to evaluate in any color space, such as Oklab, etc. It may be less useful in some color
spaces compared to others. Cylindrical spaces with polar coordinates will be converted to rectangular coordinates if
specified. Some spaces might not be as very perceptually uniform.

```py play
Color("red").distance("blue", space="srgb")
Color("red").distance("blue", space="lab")
```

/// new | New 3.3
Handling spaces with polar coordinates is new in 3.3.
///

## Delta E

The `delta_e` function gives access to various ∆E implementations, which are just different algorithms to calculate
distance. Some are simply Euclidean distance withing a certain color space, some are far more complex.

If no `method` is specified, the default implementation is ∆E^\*^~ab~ (CIE76) which uses a simple Euclidean distancing
algorithm on the CIELab color space. It is fast, but not as accurate as later iterations of the algorithm as CIELab is
not actually as perceptually uniform as it was thought when CIELab was originally developed.

```py play
Color("red").delta_e("blue")
```

When `method` is set, the specified ∆E algorithm will be used instead. For instance, below we use ∆E^\*^~00~ which is a
more complex algorithm that accounts for the CIELab's weakness in perceptually uniformity. It does come at the cost of
being a little slower.

```py play
Color("red").delta_e("blue", method="2000")
```

/// warning | Distancing and Symmetry
It should be noted that not all distancing algorithms are symmetrical. Some are order dependent.
///

### Delta E CIE76

/// success | The ∆E~ab~ distancing algorithm is registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | ----------
[∆E^\*^~ab~][de76]\ (CIE76)              | :octicons-check-16:   | `76`            | `space='lab-d65'`

One of the first approaches to color distancing and is actually just Euclidean distancing in the [CIELab](./colors/lab_d65.md)
color space.

/// note
By default, Lab D65 is used for color distancing. In the print industry, it is common for Lab D50 to be used. If Lab
D50 is desired, simply specify it as the `space` color space. `space` must be a CIE Lab color space.

```py play
Color("red").delta_e("blue", method="76")
Color("red").delta_e("blue", method="76", space='lab')
```
///

### Delta E CMC (1984)

/// success | The ∆E~cmc~ distancing algorithm is registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | ----------
[∆E^\*^~cmc~][decmc]\ (CMC\ l:c\ (1984)) | :octicons-check-16:   | `cmc`           | `l=2, c=1, space='lab-d65'`

Delta E CMC is based on the [CIELCh](./colors/lch_d65.md) color space. The CMC calculation mathematically defines an
ellipsoid around the standard color with semi-axis corresponding to hue, chroma and lightness.

Parameter | Acceptability | Perceptibility
--------- | ------------- | --------------
`l`       | 2             | 1
`c`       | 1             | 1

/// note
By default, Lab D65 is used for color distancing. In the print industry, it is common for Lab D50 to be used. If Lab
D50 is desired, simply specify it as the `space` color space. `space` must be a CIE Lab color space.

```py play
Color("red").delta_e("blue", method="cmc")
Color("red").delta_e("blue", method="cmc", space='lab')
```
///

### Delta E CIE94

/// success | The ∆E^\*^~94~ distancing algorithm is registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | ----------
[∆E^\*^~94~][de94]\ (CIE94)              | :octicons-x-16:       | `94`            | `kl=1, k1=0.045, k2=0.015, space='lab-d65'`

The [1976](#delta-e-cie76) definition was extended to address perceptual non-uniformities, while retaining the
[CIELab](./colors/lab_d65.md) color space, by the introduction of application-specific weights derived from an
automotive paint test's tolerance data.

Parameter | Graphic\ Arts | Textiles
--------- | ------------- | --------
`kl`      | 1             | 2
`k1`      | 0.045         | 0.048
`k2`      | 0.015         | 0.014

/// note
By default, Lab D65 is used for color distancing. In the print industry, it is common for Lab D50 to be used. If Lab
D50 is desired, simply specify it as the `space` color space. `space` must be a CIE Lab color space.

```py play
Color("red").delta_e("blue", method="94")
Color("red").delta_e("blue", method="94", space='lab')
```
///

### Delta E CIEDE2000

/// success | The ∆E^\*^~00~ distancing algorithm is registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | ----------
[∆E^\*^~00~][de2000]\ (CIEDE2000)        | :octicons-check-16:   | `2000`          | `kl=1, kc=1, kh=1, space='lab-d65'`

Since the 1994 definition did not adequately resolve the perceptual uniformity issue, the CIE refined their definition,
adding five corrections:

- A hue rotation term (RT), to deal with the problematic blue region (hue angles in the neighborhood of 275°)
- Compensation for neutral colors (the primed values in the LCh differences)
- Compensation for lightness (SL)
- Compensation for chroma (SC)
- Compensation for hue (SH)

/// note
By default, Lab D65 is used for color distancing. In the print industry, it is common for Lab D50 to be used. If Lab
D50 is desired, simply specify it as the `space` color space. `space` must be a CIE Lab color space.

```py play
Color("red").delta_e("blue", method="2000")
Color("red").delta_e("blue", method="2000", space='lab')
```
///

### Delta E HyAB

/// success | The ∆E~HyAB~ distancing algorithm is registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | ----------
[∆E~HyAB~][dehyab]\ (HyAB)               | :octicons-check-16:   | `hyab`          | `space="lab-d65"`

A combination of a Euclidean metric in hue and chroma with a city‐block metric to incorporate lightness differences. It
can be used on any Lab like color space, the default being CIELab D65.

### Delta E OK

/// success | The ∆E~ok~ distancing algorithm is registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | ----------
∆E~ok~                                   | :octicons-check-16:   | `ok`            | `scalar=1`

A color distancing algorithm that performs Euclidean distancing in the [Oklab](./colors/oklab.md) color space. This is
used in the [OkLCh Chroma gamut mapping algorithm](./gamut.md#oklch-chroma). The `scalar` parameter allows you to scale
the result up if desired.

### Delta E ITP

/// success | The ∆E~itp~ distancing algorithm is registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | --------------------
[∆E~itp~][deitp]\ (ICtCp)                | :octicons-check-16:   | `itp`           | `scalar=720`

Various algorithms are designed for and perform decently in the SDR range, but ∆E~itp~ aims to provide good
distancing in the HDR range using the [ICtCp](./colors/ictcp.md) color space (must be registered in order to use ∆E~itp~).
It was determined that a `scalar` of 240 was more comparable to the average [∆E^\*^~00~](#delta-e-2000) result from the
JND data set and 720 equates them to a JND.

### Delta E Z

/// success | The ∆E~z~ distancing algorithm is registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | --------------------
[∆E~z~][dez]\ (Jzazbz)                   | :octicons-check-16:   | `jz`            |

Performs Euclidean distancing in the [Jzazbz](./colors/jzazbz.md) color space, useful for the HDR range.

### Delta E 99o

/// failure | The ∆E~99o~ distancing algorithm is **not** registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | --------------------
[∆E~99o~][de99o]\ (DIN99o)               | :octicons-check-16:   | `99o`           |

∆E~99o~ performs Euclidean distancing in the [DIN99o](./colors/din99o.md) color space.

Both the DIN99o color space and the ∆E algorithm must be registered to use.

```py
from coloraide import Color as Base
from coloraide.distance.delta_e_99o import DE99o
from coloraide.spaces.din99o import DIN99o

class Color(Base): ...

Color.register([DIN99o(), DE99o()])
```

### Delta E CAM16

/// failure | The ∆E~cam16~ distancing algorithm is **not** registered in `Color` by default
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | --------------------
∆E~cam16~                                | :octicons-check-16:   | `cam16`         | `model='ucs'`

The [CAM16 UCS](./colors/cam16_ucs.md) uniform color space applies an additional nonlinear transformation to lightness
and colorfulness so that a color difference metric ΔE can be based more closely on Euclidean distance. This algorithm
performs distancing using the CAM16 UCS color space. If desired `model` can be changed to use the SCD or LCD model for
"small" and "large" distancing respectively

Parameter | Default     | Description
--------- | ----------- | -----------
`space`   | `cam16-ucs` | The CAM16 color space derived from the `CAM16UCS` space. `cam16-ucs`, `cam16-scd`, and `cam16-lcd` are provided in ColorAide (unregistered by default). Variants using different lighting environments can be created and registered and provided as the UCS space to operate in.

/// warning | Deprecated `model` parameter
In 3.3 the `model` parameter was deprecated and will be removed at some future time. `space` is more flexible and should
be used instead.
///

The one or more of the CAM16 (UCS/SCD/LCD) color spaces and the ∆E algorithm must be registered to use.

```py
from coloraide import Color as Base
from coloraide.distance.delta_e_cam16 import DECAM16
from coloraide.spaces.cam16_ucs import CAM16UCS, CAM16SCD, CAM16LCD

class Color(Base): ...

Color.register([CAM16UCS(), CAM16SCD(), CAM16LCD(), DECAM16()])
```

### Delta E HCT

/// failure | The ∆E~hct~ distancing algorithm is **not** registered in `Color` by default
///

/// warning
This approach was specifically added to help produce tonal palettes, but with the recent addition of the [ray trace
approach to chroma reduction in any perceptual space](./gamut.md#ray-tracing-chroma-reduction-in-any-perceptual-space),
users can defer to the ray tracing approach which does not require a special ∆E method and it performs much faster.

On occasions, MINDE approach can be slightly more accurate very close to white due to the way ray trace handles HCT's
atypical achromatic response, but differences should be imperceptible to the eye at such lightness levels making the
the improved performance of the ray trace approach much more desirable.

```py play
c = Color('hct', [325, 24, 50])
tones = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100]
Steps([c.clone().set('tone', tone).convert('srgb').to_string(hex=True, fit={'method': 'raytrace', 'pspace': 'hct'}) for tone in tones])
```
///

Delta\ E                                 | Symmetrical           | Name            | Parameters
---------------------------------------- | --------------------- | --------------- | --------------------
∆E~HCT~                                  | :octicons-check-16:   | `hct`           |

This takes the HCT color space C and H components (CAM16's M and h) and converts them to CAM16 UCS M and h, and applies
Euclidean distancing on them along with the T component (CIELab's L\*). This is necessary for the
[HCT Chroma gamut mapping approach](./gamut.md/#hct-chroma).

```py
from coloraide import Color as Base
from coloraide.distance.delta_e_hct import DEHCT
from coloraide.spaces.HCT import HCT

class Color(Base): ...

Color.register([HCT(), DEHCT()])
```

## Finding Closest Color

ColorAide implements a simple way to find the closest color, given a list of colors, to another color. The method is
called `closest` and takes a list of colors that are to be compared to the calling color object. The first color with
the smallest distance between the calling color object and itself will be considered the nearest/closest color.

Consider the following example. Here we provide a list of colors to compare against `#!color red`. After comparing all
the colors, the closest ends up being `#!color maroon`.

```py play
Color('red').closest(['pink', 'yellow', 'green', 'blue', 'purple', 'maroon'])
```

The default distancing method is used if one is not supplied, but others can be used:

```py play
Color('red').closest(['pink', 'yellow', 'green', 'blue', 'purple', 'maroon'], method='2000')
```

## Configuring Delta E Defaults

A number of distancing algorithms have configurable features that can be set on demand. If you'd like to have these
options set by default, you create a custom class and register the the plugins with the defaults of your choice.

In this example, we will configure ∆E^\*^~00~ to use CIE Lab D50 instead of D65 by default.

```py play
from coloraide import Color as Base
from coloraide.distance.delta_e_2000 import DE2000

class Color(Base):
    ...

Color.register(DE2000(space='lab'), overwrite=True)

Color('red').delta_e('blue', method='2000')
Color('red').delta_e('blue', method='2000', space='lab-d65')
```
