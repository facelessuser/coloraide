# Supported Colors

ColorAide aims to support all the color spaces and models currently offered in modern CSS, such as sRGB, Display P3,
CIELAB, Oklab, etc. We also include a number of color spaces that are not available in CSS.

While ColorAide supports a lot of color spaces, it is rare that a user would ever need every color space implemented by
ColorAide available at all times, so to keep the Color object lighter, and color matching logic quicker, the
`coloraide.Color` object does not register all color spaces by default.

The following color spaces are registered by default:

&nbsp;                                | &nbsp;                                      | Default Color\ Spaces       | &nbsp;                                   | &nbsp;
------------------------------------- | ------------------------------------------- | --------------------------- | ---------------------------------------- | -----
[XYZ\ D65](#xyz-d65)                  | [XYZ\ D50](#xyz-d50)                        | [Linear sRGB](#linear-srgb) | [Linear Display\ P3](#linear-display-p3) | [Linear A98\ RGB](#linear-a98-rgb)
[Linear Rec.\ 2020](#linear-rec-2020) | [Linear ProPhoto\ RGB](#linear-prohoto-rgb) | [sRGB](#srgb)               | [Display\ P3](#display-p3)               | [A98\ RGB](#a98-rgb)
[Rec.\ 2020](#rec-2020)               | [ProPhoto\ RGB](#prophoto-rgb)              | [HSL](#hsl)                 | [HSV](#hsv)                              | [HWB](#hwb)
[Lab](#cielab-d50)                    | [Lch](#cielch-d50)                          | [Lab\ D65](#cielab-d65)     | [Lch\ D65](#cielch-d65)                  | [Oklab](#oklab)
[Oklch](#oklch)                       |                                             |                             |                                          |

Normally, it is suggested that a user cherry pick any additional color spaces they need by subclassing the
`coloraide.Color` object and registering any additional color spaces that are needed (and any other plugins that are
desired). With that said, ColorAide does also provide `coloraide.ColorAll` which includes every implemented color space,
∆E method, and other relevant plugins. In our live examples, it is the default color object we use to demonstrate
features. Below we've provided a diagram of all the color spaces and how they translate to one another.

```diagram
flowchart TB

    acescc --- acescg ---- xyz-d65
        acescct --- acescg

    aces2065-1 --- xyz-d65

    oklch --- oklab ----- xyz-d65
        okhsl --- oklab
        okhsv --- oklab

    display-p3 --- display-p3-linear --- xyz-d65

    a98-rgb --- a98-rgb-linear --- xyz-d65

    hwb --- hsv --- hsl --- srgb --- srgb-linear ----- xyz-d65
        orgb --- srgb
        prismatic --- srgb
        hsi --- srgb
        cmy --- srgb
        cmyk --- srgb

    rec2020 --- rec2020-linear --- xyz-d65
        rec2100pq --- rec2020-linear

    prophoto-rgb --- prophoto-rgb-linear --- xyz-d50 ----- xyz-d65
        lch --- lab --- xyz-d50

    xyz-d65 --- lab-d65 --- lch-d65

    xyz-d65 --- jzazbz --- jzczhz

    xyz-d65 --- ipt

    xyz-d65 --- ictcp

    xyz-d65 --- igpgtg

    xyz-d65 --- din99o --- lch99o

    xyz-d65 --- hunter-lab

    xyz-d65 --- rlab

    xyz-d65 --- luv --- lchuv
        luv --- hsluv
        luv --- hpluv

    xyz-d65 --- xyy

    xyz-d65(XYZ D65)
    xyz-d50(XYZ D50)
    rec2020(Rec. 2020)
    rec2020-linear(Linear Rec. 2020)
    rec2100pq(Rec. 2100 PQ)
    srgb-linear(Linear sRGB)
    srgb(sRGB)
    hsl(HSL)
    hsv(HSV)
    hwb(HWB)
    display-p3-linear(Linear Display P3)
    display-p3(Display P3)
    a98-rgb-linear(Linear A98 RGB)
    a98-rgb(A98 RGB)
    prophoto-rgb-linear(Linear ProPhoto RGB)
    prophoto-rgb(ProPhoto RGB)
    lab(Lab)
    lch(Lch)
    lab-d65(Lab D65)
    lch-d65(Lch D65)
    oklab(Oklab)
    oklch(Oklch)
    okhsl(Okhsl)
    okhsv(Okhsv)
    luv(Luv)
    lchuv(LCHuv)
    hsluv(HSLuv)
    hpluv(HPLuv)
    din99o(DIN99o)
    lch99o(DIN99o Lch)
    jzazbz(Jzazbz)
    jzczhz(JzCzhz)
    ictcp(ICtCp)
    orgb(oRGB)
    ipt(IPT)
    igpgtg(IgPgTg)
    hunter-lab(Hunter Lab)
    rlab(RLAB)
    hsi(HSI)
    cmy(CMY)
    cmyk(CMYK)
    xyy(xyY)
    prismatic(Prismatic)
    aces2065-1(ACES2065-1)
    acescg(ACEScg)
    acescc(ACEScc)
    acescct(ACEScct)
```

## RGB

RGB is a color model used by a number of different color spaces. The sRGB color space is probably the one most think of
when someone mentions RGB.

The RGB model represents colors with three channels: red, green, and blue. Though a number of color spaces use the RGB
model, how colors translate to those coordinates differs from one color space to another. Depending on the color space,
the range of colors within its gamut can be quite different.

### sRGB

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `srgb`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

<figure markdown="1">

![sRGB](../images/srgb.png)

<figcaption>CIE 1931 xy Chromaticity -- sRGB Chromaticities</figcaption>
</figure>

The sRGB space is a standard RGB (red, green, blue) color space that HP and Microsoft created cooperatively in 1996 to
use on monitors, printers, and the Web. SRGB stands for "Standard RGB". It is the most widely used color space and is
supported by most operating systems, software programs, monitors, and printers.

_[Learn about sRGB](https://en.wikipedia.org/wiki/SRGB)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 
        Parsed input and string output formats support all valid CSS forms:

        ```css-color
        black                  // Color name
        #RRGGBBAA              // Hex
        rgb(r g b / a)         // RGB function
        rgb(r, g, b)           // Legacy RGB Function
        rgba(r, g, b, a)       // Legacy RGBA function
        color(srgb r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("srgb", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object will always default to the `#!css-color color(srgb r g b / a)`
        form, but the default string output will be the `#!css-color rgb(r g b / a)` form.

        ```playground
        Color("srgb", [0, 0, 0], 1)
        Color("srgb", [0, 0, 0], 1).to_string()
        ```

### Linear sRGB

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `srgb-linear`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

The sRGB Linear space is the same as [sRGB](#srgb) *except* that the transfer function is linear-light (there is no
gamma-encoding).

_[Learn about sRGB](https://en.wikipedia.org/wiki/SRGB)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 
        Parsed input and string output formats support all valid CSS forms:

        ```css-color
        color(srgb-linear r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("srgb-linear", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(srgb-linear r g b / a)` form.

        ```playground
        Color("srgb-linear", [0, 0, 0], 1)
        Color("srgb-linear", [0, 0, 0], 1).to_string()
        ```

### Display P3

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `display-p3`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

<figure markdown="1">

![Display P3](../images/display-p3.png)

<figcaption>CIE 1931 xy Chromaticity -- Display P3 Chromaticities</figcaption>
</figure>

Display P3 is a combination of the DCI-P3 color gamut with the D65 white point together with the [sRGB](#srgb) gamma
curve. It originated from the DCI-P3 color gamut's implementation in digital cinema projectors, as this standard offers
more vibrant greens and reds than the traditional [sRGB](#srgb) color gamut.

_[Learn about Display P3](https://www.color.org/chardata/rgb/DisplayP3.xalter)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs**
    : 
        Parsed input and string output formats support all valid CSS forms:

        ```css-color
        color(display-p3 r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("display-p3", [0, 0, 0], 1)
        ```

    **Output**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(display-p3 r g b / a)` form.

        ```playground
        Color("display-p3", [0, 0, 0], 1)
        Color("display-p3", [0, 0, 0], 1).to_string()
        ```

### Linear Display P3

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `display-p3-linear`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

The Linear Display P3 space is the same as [Display P3](#display-p3) *except* that the transfer function is linear-light
(there is no gamma-encoding).

_[Learn about Display P3](https://www.color.org/chardata/rgb/DisplayP3.xalter)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs**
    : 
        Linear Display P3 is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --display-p3-linear`:

        ```css-color
        color(--display-p3-linear r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("display-p3-linear", [0, 0, 0], 1)
        ```

    **Output**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(--display-p3-linear r g b / a)` form.

        ```playground
        Color("display-p3-linear", [0, 0, 0], 1)
        Color("display-p3-linear", [0, 0, 0], 1).to_string()
        ```

### A98 RGB

<div class="info-container" markdown="1">

!!! info inline end "Properties"

    **Name:** `a98-rgb`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

<figure markdown="1">

![A98 RGB](../images/a98-rgb.png)

<figcaption>CIE 1931 xy Chromaticity -- Adobe RGB 1998 Chromaticities</figcaption>
</figure>

The Adobe RGB (1998) color space or opRGB is a color space developed by Adobe Systems, Inc. in 1998. It was designed to
encompass most of the colors achievable on CMYK color printers, but by using [RGB](#srgb) primary colors on a device
such as a computer display. The Adobe RGB (1998) color space encompasses roughly 50% of the visible colors specified by
the [CIELAB](#cielab) color space - improving upon the gamut of the [sRGB](#srgb) color space, primarily in cyan-green
hues.

_[Learn about A98 RGB](https://en.wikipedia.org/wiki/Adobe_RGB_color_space)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 
        Parsed input and string output formats support all valid CSS forms:

        ```css-color
        color(a98-rgb r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("a98-rgb", [0, 0, 0], 1)
        ```

    **Output**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(a98-rgb r g b / a)` form.

        ```playground
        Color("a98-rgb", [0, 0, 0], 1)
        Color("a98-rgb", [0, 0, 0], 1).to_string()
        ```

### Linear A98 RGB

<div class="info-container" markdown="1">

!!! info inline end "Properties"

    **Name:** `a98-rgb-linear`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

The Linear A98 RGB space is the same as [A98 RGB](#a98-rgb) *except* that the transfer function is linear-light (there
is no gamma-encoding).

_[Learn about A98 RGB](https://en.wikipedia.org/wiki/Adobe_RGB_color_space)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 
        Linear A98 RGB is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --a98-rgb-linear`:

        ```css-color
        color(--a98-rgb-linear r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("a98-rgb-linear", [0, 0, 0], 1)
        ```

    **Output**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(--a98-rgb-linear r g b / a)` form.

        ```playground
        Color("a98-rgb-linear", [0, 0, 0], 1)
        Color("a98-rgb-linear", [0, 0, 0], 1).to_string()
        ```

### REC. 2020

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `rec2020`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

<figure markdown="1">

![Rec. 2020](../images/rec2020.png)

<figcaption>CIE 1931 xy Chromaticity -- Rec. 2020 Chromaticities</figcaption>
</figure>

ITU-R Recommendation BT.2020, more commonly known by the abbreviations Rec. 2020 or BT.2020, defines various aspects of
ultra-high-definition television (UHDTV) with standard dynamic range (SDR) and wide color gamut (WCG), including picture
resolutions, frame rates with progressive scan, bit depths, color primaries, RGB and luma-chroma color representations,
chroma subsamplings, and an opto-electronic transfer function. The color is used in 4k and 8k UHDTV.

_[Learn about REC.2020](https://en.wikipedia.org/wiki/Rec._2020)_

</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 

        Parsed input and string output formats support all valid CSS forms:

        ```css-color
        color(rec2020 r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("rec2020", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(rec2020 r g b / a)` form.

        ```playground
        Color("rec2020", [0, 0, 0], 1)
        Color("rec2020", [0, 0, 0], 1).to_string()
        ```

### Linear REC. 2020

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `rec2020-linear`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

The Linear Rec. 2020 space is the same as [Rec. 2020](#rec-2020) *except* that the transfer function is linear-light
(there is no gamma-encoding).

_[Learn about REC.2020](https://en.wikipedia.org/wiki/Rec._2020)_

</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 

        Linear Rec. 2020 is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --rec2020-linear`:

        ```css-color
        color(--rec2020-linear r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("rec2020-linear", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(--rec2020-linear r g b / a)` form.

        ```playground
        Color("rec2020-linear", [0, 0, 0], 1)
        Color("rec2020-linear", [0, 0, 0], 1).to_string()
        ```

### ProPhoto

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `prophoto-rgb`

    **White Point:** D50

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

<figure markdown="1">

![ProPhoto RGB](../images/prophoto-rgb.png)

<figcaption>CIE 1931 xy Chromaticity -- ProPhoto RGB Chromaticities</figcaption>
</figure>

The ProPhoto RGB color space, also known as ROMM RGB (Reference Output Medium Metric), is an output referred RGB color
space developed by Kodak. It offers an especially large gamut designed for use with photographic output in mind. The
ProPhoto RGB color space encompasses over 90% of possible surface colors in the [CIE L\*a\*b\*](#cielab) color space,
and 100% of likely occurring real-world surface colors documented by Pointer in 1980.

_[Learn about ProPhoto](https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 
        Parsed input and string output formats support all valid CSS forms:

        ```css-color
        color(prophoto-rgb r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("prophoto-rgb", [0, 0, 0], 1)
        ```
    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(prophoto-rgb r g b / a)` form.

        ```playground
        Color("prophoto-rgb", [0, 0, 0], 1)
        Color("prophoto-rgb", [0, 0, 0], 1).to_string()
        ```

### Linear ProPhoto

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `prophoto-rgb-linear`

    **White Point:** D50

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

The Linear ProPhoto space is the same as [ProPhoto](#prophoto) *except* that the transfer function is linear-light
(there is no gamma-encoding).

_[Learn about ProPhoto](https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 
        Linear ProPhoto is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --prophoto-rgb-linear`:

        ```css-color
        color(--prophoto-rgb-linear r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("prophoto-rgb-linear", [0, 0, 0], 1)
        ```
    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(--prophoto-rgb-linear r g b / a)` form.

        ```playground
        Color("prophoto-rgb-linear", [0, 0, 0], 1)
        Color("prophoto-rgb-linear", [0, 0, 0], 1).to_string()
        ```

### REC. 2100 PQ

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `rec2100pq`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

<figure markdown="1">

![Rec. 2020](../images/rec2020.png)

<figcaption>CIE 1931 xy Chromaticity -- Rec. 2100 Chromaticities (Same as Rec. 2020)</figcaption>
</figure>

BT.2100, more commonly known by the abbreviations Rec. 2100 or BT.2100, introduced high-dynamic-range television
(HDR-TV) by recommending the use of the perceptual quantizer (PQ) or hybrid log–gamma (HLG) transfer functions instead
of the traditional "gamma" previously used for SDR-TV. Rec. 2100 PQ specifically uses the perceptual quantizer.

The actual gamut of Rec. 2100 uses the same wide color gamut of Rec. 2020, but the color space itself supports an HDR
range.

_[Learn about REC.2020](https://en.wikipedia.org/wiki/Rec._2100)_

</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 

        Rec. 2100 PQ is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --rec2100pq`:

        ```css-color
        color(--rec2100pq r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("rec2100pq", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(--rec2100pq r g b / a)` form.

        ```playground
        Color("rec2100pq", [0, 0, 0], 1)
        Color("rec2100pq", [0, 0, 0], 1).to_string()
        ```

## Cylindrical sRGB Spaces

The sRGB color space has been represented in a number of cylindrical models. Each model was an attempt to either align
the color with human perception or make it more intuitive to work with. The term "cylindrical" is used as the spaces
take on the shape of a cylinder, whereas the RGB model is very much a cube:

<figure markdown="1">

![sRGB 3D](../images/srgb-3d.png)

<figcaption>sRGB color space in 3D</figcaption>
</figure>

### HSV

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `hsv`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `h`    | [0, 360)
    `s`    | [0, 1]
    `v`    | [0, 1]

<figure markdown="1">

![HSV 3D](../images/hsv-3d.png)

<figcaption>HSV color space in 3D</figcaption>
</figure>

HSV is a color space similar to the modern [RGB](#srgb) and CMYK models. The HSV color space has three components: hue,
saturation and value. 'Value' is sometimes substituted with 'brightness' and then it is known as HSB. HSV models how
colors appear under light.

_[Learn about HSV](https://en.wikipedia.org/wiki/HSL_and_HSV)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `h`      | `hue`
        `s`      | `saturation`
        `v`      | `value`

    **Inputs:**
    : 
        HSV is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --hsv`:

        ```css-color
        color(--hsv 0 0% 0% / 1)
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("hsv", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and default string output will always use the
        `#!css-color color(hsv h s v / a)` form.

        ```playground
        Color("hsv", [0, 0, 0], 1)
        Color("hsv", [0, 0, 0], 1).to_string()
        ```

### HSL

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `hsl`

    **White Point:**   D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `h`  | [0, 360)
    `s`  | [0, 1]
    `l`  | [0, 1]

<figure markdown="1">

![HSL 3D](../images/hsl-3d.png)

<figcaption>HSL color space in 3D</figcaption>
</figure>

HSL is an alternative representations of the [RGB](#srgb) color model, designed in the 1970s by computer graphics
researchers to more closely align with the way human vision perceives color-making attributes. In these models, colors
of each hue are arranged in a radial slice, around a central axis of neutral colors which ranges from black at the
bottom to white at the top.

HSL models the way different paints mix together to create color in the real world, with the lightness dimension
resembling the varying amounts of black or white paint in the mixture.

_[Learn about HSL](https://en.wikipedia.org/wiki/HSL_and_HSV)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `h`      | `hue`
        `s`      | `saturation`
        `l`      | `lightness`

    **Inputs:**
    : 
        Parsed input and string output formats support all valid CSS forms. In addition, we also allow the `#!css-color 
        color()` function format using the custom name `#!css-color --hsl`:

        ```css-color
        hsl(h s l / a)          // HSL function
        hsl(h, s, l)            // Legacy HSL function
        hsla(h, s, l, a)        // Legacy HSLA function
        color(--hsl h s l / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("hsl", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object will always default to the `#!css-color color(--hsl h s l / a)`
        form, but the default string output will be the `#!css-color hsl(h s l / a)` form.

        ```playground
        Color("hsl", [0, 0, 0], 1)
        Color("hsl", [0, 0, 0], 1).to_string()
        ```

### HWB

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `hwb`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `h`  | [0, 360)
    `w`  | [0, 1]
    `b`  | [0, 1]

<figure markdown="1">

![HWB 3D](../images/hwb-3d.png)

<figcaption>HWB color space in 3D</figcaption>
</figure>

HWB is a cylindrical-coordinate representation of points in an [RGB](#srgb) color model, similar to HSL and HSV. It was
developed by [HSV](#hsv)'s creator Alvy Ray Smith in 1996 to address some of the issues with HSV. HWB was designed to be
more intuitive for humans to use and slightly faster to compute. The first coordinate, H (Hue), is the same as the Hue
coordinate in [HSL](#hsl) and [HSV](#hsv). W and B stand for Whiteness and Blackness respectively and range from 0-100%
(or 0-1). The mental model is that the user can pick a main hue and then "mix" it with white and/or black to produce the
desired color.

_[Learn about HWB](https://en.wikipedia.org/wiki/HWB_color_model)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels    | Aliases
        ----------- | -------
        `h`         | `hue`
        `w`         | `whiteness`
        `b`         | `blackness`

    **Inputs:**
    : 
        Parsed input and string output formats support all valid CSS forms. In addition, we also allow the
        `#!css-color color()` function format using the custom name `#!css-color --hwb`:

        ```css-color
        hwb(h w b / a)          // HWB function
        color(--hwb h w b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("hwb", [0, 0, 100], 1)
        ```

    **Output:**
    : 
        The string representation of the color object will always default to the `#!css-color color(--hwb h w b / a)`
        form, but the default string output will be the `#!css-color hwb(h s l / a)` form.

        ```playground
        Color("hwb", [0, 0, 100], 1)
        Color("hwb", [0, 0, 100], 1).to_string()
        ```

### Okhsv

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `okhsv`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `h`  | [0, 360)
    `s`  | [0, 1]
    `v`  | [0, 1]

<figure markdown="1">

![Okhsv 3D](../images/okhsv-3d.png)

<figcaption>Okhsv color space in 3D</figcaption>
</figure>

Okhsv is a color space created by Björn Ottosson. It is based off his early work and leverages the [Oklab](#oklab) color
space. The aim was to create a color space that was better suited for being used in color pickers than the current HSV.

_[Learn about Okhsv](https://bottosson.github.io/posts/colorpicker/)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels    | Aliases
        ----------- | -------
        `h`         | `hue`
        `s`         | `saturation`
        `v`         | `value`

    **Inputs:**
    : 
        Okhsv is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --okhsv`:

        ```css-color
        color(--okhsv h s l / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("okhsv", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--okhsv h s l / a)` form.

        ```playground
        Color("okhsv", [0, 0, 0], 1)
        Color("okhsv", [0, 0, 0], 1).to_string()
        ```

### Okhsl

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `okhsl`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `h`  | [0, 360)
    `s`  | [0, 1]
    `l`  | [0, 1]

<figure markdown="1">

![Okhsl 3D](../images/okhsl-3d.png)

<figcaption>Okhsl color space in 3D</figcaption>
</figure>

Okhsl is a another color space created by Björn Ottosson. It is based off his early work and leverages the
[Oklab](#oklab) color space. The aim was to create a color space that was better suited for being used in color pickers
than the current HSL.

_[Learn about Okhsv](https://bottosson.github.io/posts/colorpicker/)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels    | Aliases
        ----------- | -------
        `h`         | `hue`
        `s`         | `saturation`
        `l`         | `lightness`

    **Inputs:**
    : 
        Okhsl is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --okhsl`:

        ```css-color
        color(--okhsl h s l / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("okhsl", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--okhsl h s l / a)` form.

        ```playground
        Color("okhsl", [0, 0, 0], 1)
        Color("okhsl", [0, 0, 0], 1).to_string()
        ```

### HSLuv

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `hsluv`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `h`  | [0, 360)
    `s`  | [0, 100]
    `l`  | [0, 100]

<figure markdown="1">

![HSLuv 3D](../images/hsluv-3d.png)

<figcaption>HSLuv color space in 3D</figcaption>
</figure>

HSLuv is a human-friendly alternative to HSL. It was formerly known as "HUSL" and is a variation of the
[CIELCH~uv~](#cielchuv) color space, where the chroma component is replaced by a saturation component which allows you
to span all the available chroma as a percentage. HSLuv is constrained to the sRGB gamut.

_[Learn about HSLuv](https://www.hsluv.org/)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels    | Aliases
        ----------- | -------
        `h`         | `hue`
        `s`         | `saturation`
        `l`         | `lightness`

    **Inputs:**
    : 
        HSLuv is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --hsluv`:

        ```css-color
        color(--hsluv h s l / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("hsluv", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--hsluv h s l / a)` form.

        ```playground
        Color("hsluv", [0, 0, 0], 1)
        Color("hsluv", [0, 0, 0], 1).to_string()
        ```

### HPLuv

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `hpluv`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `h`  | [0, 360)
    `p`  | [0, 100]
    `l`  | [0, 100]

<figure markdown="1">

![HPLuv 3D](../images/hpluv-3d.png)

<figcaption>HSLuv color space in 3D</figcaption>
</figure>

HPLuv is similar to [HSLuv](#hsluv) but takes as many colors as it can from [CIELCH~uv~](#cielchuv) without distorting
the chroma. This ends up reducing the gamut to a subset of the sRGB gamut. In the end, only more pastel colors remain.

_[Learn about HSLuv](https://www.hsluv.org/)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels    | Aliases
        ----------- | -------
        `h`         | `hue`
        `s`         | `perpendiculars`
        `l`         | `lightness`

    **Inputs:**
    : 
        HPLuv is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --hpluv`:

        ```css-color
        color(--hpluv h p l / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("hpluv", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--hpluv h p l / a)` form.

        ```playground
        Color("hpluv", [0, 0, 0], 1)
        Color("hpluv", [0, 0, 0], 1).to_string()
        ```

### HSI

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `hsi`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `h`  | [0, 360)
    `s`  | [0, 1]
    `i`  | [0, 1]

<figure markdown="1">

![HSI](../images/hsi-3d.png)

<figcaption>The sRGB gamut represented within the HSI color space.</figcaption>
</figure>

The HSI model is similar to models like HSL and HSV except that it uses I for intensity instead of Lightness or Value.
It does not attempt to "fill" a cylinder by its definition of saturation leading to a very different look when we plot
it.

![HSI Slice](../images/hsi-slice.png)

[Learn more](https://en.wikipedia.org/wiki/HSL_and_HSV#HSI_to_RGB).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `h`      | `hue`
        `s`      | `saturation`
        `i`      | `intensity`

    **Inputs**
    : 

        The HSI space is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --hsi`:

        ```css-color
        color(--hsi h s i / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--hsi h s i / a)` form.

        ```playground
        Color("hsi", [0, 0, 0], 1)
        Color("hsi", [0, 0, 0], 1).to_string()
        ```

## ACES

The Academy Color Encoding System (ACES) is a color image encoding system created under the auspices of the
[Academy of Motion Picture Arts and Sciences](https://acescentral.com/). ACES allows for a fully encompassing color
accurate workflow, with "seamless interchange of high quality motion picture images regardless of source".

### ACES 2065-1

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `aces2065-1`

    **White Point:** D60

    **Coordinates:**

    Name | Range
    ---- | -----
    `r`  | [0, 65504]
    `g`  | [0, 65504]
    `b`  | [0, 65504]

<figure markdown="1">

![ACES 2065-1](../images/aces2065-1.png)

<figcaption>CIE 1931 xy Chromaticity -- ACES AP0 Chromaticities</figcaption>
</figure>

ACES 2065-1 is a linear color space that uses set of primaries known as AP0 and has the widest gamut of all the ACES
color spaces and fully encompasses the entire visible spectrum. It is meant primarily as an archival format due to
its ability to encapsulate all visible colors. Typically, this is the color space you would use to transfer
images/animations between production studios.

_[Learn about ACES 2065-1](https://docs.acescentral.com/#aces-2065-1)_

</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 

        ACES 2065-1 is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --aces2065-1`:

        ```css-color
        color(--aces2065-1 r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("aces2065-1", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(--aces2065-1 r g b / a)` form.

        ```playground
        Color("aces2065-1", [0, 0, 0], 1)
        Color("aces2065-1", [0, 0, 0], 1).to_string()
        ```

### ACEScg

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `acescg`

    **White Point:** D60

    **Coordinates:**

    Name | Range
    ---- | -----
    `r`  | [0, 65504]
    `g`  | [0, 65504]
    `b`  | [0, 65504]

<figure markdown="1">

![ACEScg](../images/acescg.png)

<figcaption>CIE 1931 xy Chromaticity -- ACES AP1 Chromaticities</figcaption>
</figure>

ACEScg is a color space often used by CG artists. It is "scene-referred" or linear. It doesn't have as wide a color
gamut as ACES 2065-1 as it uses a different set of primaries called AP1, but it is far larger than most other color
spaces one might use and has an enormous dynamic range.

_[Learn about ACEScg](https://docs.acescentral.com/specifications/acescg/)_

</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 

        ACEScg is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --acescg`:

        ```css-color
        color(--acescg r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("acescg", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(--acescg r g b / a)` form.

        ```playground
        Color("acescg", [0, 0, 0], 1)
        Color("acescg", [0, 0, 0], 1).to_string()
        ```

### ACEScc

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `acescc`

    **White Point:** D60

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [-0.0729,\ 1.468]
    `g`  | [-0.0729,\ 1.468]
    `b`  | [-0.0729,\ 1.468]

    ^\*^ Ranges are approximate and have been rounded.

ACEScc is a color space based on the API primaries and is primarily used for color grading. It is a logarithmic color
space, unlike ACEScg, and maps black at 0 and white at 1.

_[Learn about ACEScc](https://docs.acescentral.com/specifications/acescc/)_

</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 

        ACEScc is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --acescc`:

        ```css-color
        color(--acescc r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("acescc", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(--acescc r g b / a)` form.

        ```playground
        Color("acescc", [0, 0, 0], 1)
        Color("acescc", [0, 0, 0], 1).to_string()
        ```

### ACEScct

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `acescct`

    **White Point:** D60

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `r`  | [-0.3584,\ 1.468]
    `g`  | [-0.3584,\ 1.468]
    `b`  | [-0.3584,\ 1.468]

    ^\*^ Ranges are approximate and rounded to 3 decimal places.

ACEScct is very similar to [ACEScc](#acescc) except that it adds a "toe" or a gamma curve in the dark region of the
color space. This encoding is more appropriate for legacy color correction operators.

_[Learn about ACEScct](https://docs.acescentral.com/specifications/acescct/)_

</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs:**
    : 

        ACEScct is not supported via the CSS spec and the parser input and string output only supports the
        `#!css-color color()` function format using the custom name `#!css-color --acescct`:

        ```css-color
        color(--acescct r g b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("acescct", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(--acescct r g b / a)` form.

        ```playground
        Color("acescct", [0, 0, 0], 1)
        Color("acescct", [0, 0, 0], 1).to_string()
        ```

## CMY(K)

CMY and CMYK are subtractive color models. The CMY color model itself does not define what is meant by cyan, magenta and
yellow colorimetrically, and so the results of mixing them are not specified as absolute. As far as ColorAide Extra is
concerned, it has defined its primaries the same as sRGB making it an absolute color space.

There are many places in which CMY or CMYK are used, often in device dependent applications. CMYK is used in all sorts
of printing applications, and the exact definition of cyan, magenta, yellow, and black will differ depending on how the
device has implemented it. Unless they are calibrated to the sRGB color space primaries, it is almost certain this will
not match such implementations.

### CMY

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `cmy`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `c`  | [0, 1]
    `m`  | [0, 1]
    `y`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

<figure markdown="1">

![CMY](../images/cmy-3d.png)

<figcaption>The sRGB gamut represented within the CMY color space.</figcaption>
</figure>

The CMY color model is a subtractive color model in which cyan, magenta and yellow pigments or dyes are added together
in various ways to reproduce a broad array of colors. The name of the model comes from the initials of the three
subtractive primary colors: cyan, magenta, and yellow.

The CMY color space, as ColorAide Extras has chosen to implement it, is directly calculated from the sRGB color space,
and as such, is based off the sRGB primaries.

[Learn more](https://en.wikipedia.org/wiki/CMY_color_model).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `c`      | `cyan`
        `m`      | `magenta`
        `y`      | `yellow`

    **Inputs**
    : 

        CMY is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --cmy`:

        ```css-color
        color(--cmy c m y / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--cmy c m y / a)` form.

        ```playground
        Color("cmy", [0, 0, 0], 1)
        Color("cmy", [0, 0, 0], 1).to_string()
        ```

### CMYK

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `cmyk`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `c`  | [0, 1]
    `m`  | [0, 1]
    `y`  | [0, 1]
    `k`  | [0, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

The CMYK color model is a just like [CMY](#cmy) except that it adds an additional channel `k` to control blackness.

The CMYK color space, as ColorAide Extras has chosen to implement it, is directly calculated from the sRGB color space,
and as such, is based off the sRGB primaries.

[Learn more](https://en.wikipedia.org/wiki/CMY_color_model).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `c`      | `cyan`
        `m`      | `magenta`
        `y`      | `yellow`
        `k`      | `black`

    **Inputs**
    : 

        CMY is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --cmyk`:

        ```css-color
        color(--cmyk c m y k / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--cmyk c m y k / a)` form.

        ```playground
        Color("cmyk", [0, 0, 0, 0], 1)
        Color("cmyk", [0, 0, 0, 0], 1).to_string()
        ```

## XYZ

The 1931 CIE XYZ color space encompasses all colors that are visible to a person with average eyesight. It also contains
many colors that the human eye cannot see:

<figure markdown="1">

![XYZ D65](../images/xyz-d65.png)

<figcaption>CIE 1931 xy Chromaticity -- overlaid with the XYZ D65 space.</figcaption>
</figure>

In many color libraries, it is used as a space through which different color conversions are passed through as it is
large enough to contain all visible colors. Many conversions use matrices based on this space to do chromatic adaption
or just direct translations.

While the chromaticity diagrams we've shown all use [XYZ with a D65 white point](#xyz-d65) to help generate them, XYZ
can be represented with other white points as well. CSS actually allows using either [XYZ D50](#xyz-d50) or
[XYZ D65](#xyz-d65). We also provide both.

### XYZ D65

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `xyz-d65`

    **White Point:** D65

    **Coordinates:**

    Name       | Range^\*^
    ---------- | ---------
    `x`        | [0, 1]
    `y`        | [0, 1]
    `z`        | [0, 1]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs.

<figure markdown="1">

![XYZ D65 3D](../images/xyz-d65-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the XYZ D65 color space.</figcaption>
</figure>

The CIE 1931 RGB color space and CIE 1931 XYZ color space were created by the International Commission on Illumination
(CIE) in 1931. They resulted from a series of experiments done in the late 1920s by William David Wright using ten
observers and John Guild using seven observers. The experimental results were combined into the specification of the
CIE RGB color space, from which the CIE XYZ color space was derived. The CIE 1931 color spaces are the first defined
quantitative links between distributions of wavelengths in the electromagnetic visible spectrum, and physiologically
perceived colors in human color vision.

_[Learn about XYZ](https://en.wikipedia.org/wiki/CIE_1931_color_space)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels    | Aliases
        ----------- | -------
        `x`         |
        `y`         |
        `z`         |

    **Inputs:**
    : 
        Parsed input and string output formats use the `#!css-color color()` format with either `#!css-color xyz-d65`
        or `#!css-color xyz` as the identifier with the latter being an alias of the former.

        ```css-color
        color(xyz x y z / a)      // Color function
        color(xyz-d65 x y z / a)  // Color function alternate name
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("xyz-d65", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the 
        `#!css-color color(xyz-d65 x y z / a)` form.

        ```playground
        Color("xyz-d65", [0, 0, 0], 1)
        Color("xyz-d65", [0, 0, 0], 1).to_string()
        ```

### XYZ D50

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `xyz-d50`

    **White Point:** D50

    **Coordinates:**

    Name       | Range^\*^
    ---------- | ---------
    `x`        | [0, 1]
    `y`        | [0, 1]
    `z`        | [0, 1]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs.

<figure markdown="1">

![XYZ D50 3D](../images/xyz-d50-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the XYZ D50 color space.</figcaption>
</figure>

XYZ D50 is the same as [XYZ D65](#xyz-d65) except it uses a D50 white point.

_[Learn about XYZ](https://en.wikipedia.org/wiki/CIE_1931_color_space)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels    | Aliases
        ----------- | -------
        `x`         |
        `y`         |
        `z`         |

    **Inputs:**
    : 
        Parsed input and string output formats support all valid CSS forms:

        ```css-color
        color(xyz-d50 x y z / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("xyz-d50", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output will be in the
        `#!css-color color(xyz x y z / a)` form.

        ```playground
        Color("xyz-d50", [0, 0, 0], 1)
        Color("xyz-d50", [0, 0, 0], 1).to_string()
        ```

## CIE xyY

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `xyy`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `x`  | [0, 1]
    `y`  | [0, 1]
    `Y`  | [0, 1]

    ^\*^ Space is not bound to the range and is used to define percentage inputs/outputs.

<figure markdown="1">

![xyY](../images/xyy-3d.png)

<figcaption>The sRGB gamut represented within the xyY color space.</figcaption>
</figure>

A derivative of the CIE 1931 XYZ space, the CIE xyY color space, is often used as a way to graphically present the
chromaticity of colors.

[Learn more](https://en.wikipedia.org/wiki/CIE_1931_color_space#CIE_xy_chromaticity_diagram_and_the_CIE_xyY_color_space).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `x`      |
        `y`      |
        `Y`      |

    **Inputs**
    : 

        The xyY space is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --xyy`:

        ```css-color
        color(--xyy x y Y / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--xyy x y Y / a)` form.

        ```playground
        Color("xyy", [0, 0, 0], 1)
        Color("xyy", [0, 0, 0], 1).to_string()
        ```

## CIELAB

CIELAB -- also referred to as L\*a\*b\* -- is another CIE color space. it was created as a perceptually uniform color
space. CIELAB doesn't really have a gamut, and pretty much any other color space can be mapped to it.

Much like [XYZ](#xyz), CIELAB and CIELCH currently use a [D50](#cielab-d50) white point just like the CSS, but we've
also included variants with D65 white points as well.

### CIELAB D50

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `lab`

    **White Point:** D50

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 100]
    `a`  | [-125, 125]
    `b`  | [-125, 125]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![CIELAB D50 3D](../images/lab-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the CIELAB D50 color space.</figcaption>
</figure>

The CIELAB color space also referred to as L\*a\*b\* is a color space defined by the International Commission on
Illumination (abbreviated CIE) in 1976. It expresses color as three values: L\* for perceptual lightness, and a\* and
b\* for the four unique colors of human vision: red, green, blue, and yellow. CIELAB was intended as a perceptually
uniform space, where a given numerical change corresponds to similar perceived change in color. While the CIELAB space
is not truly perceptually uniform, it nevertheless is useful in industry for detecting small differences in color.

_[Learn about CIELAB](https://en.wikipedia.org/wiki/CIELAB_color_space)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `a`      |
        `b`      |

    **Inputs:**
    : 
        Parsed input and string output formats support all valid CSS forms. In addition, we also allow the
        `#!css-color color()` function format using the custom name `#!css-color --lab`:

        ```css-color
        lab(l a b / a)          // Lab function
        color(--lab l a b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("lab", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object will always default to the `#!css-color color(--lab l a b / a)`
        form, but the default string output will be the `#!css-color lab(l a b / a)` form.

        ```playground
        Color("lab", [0, 0, 0], 1)
        Color("lab", [0, 0, 0], 1).to_string()
        ```

### CIELAB D65

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `lab-d65`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 100]
    `a`  | [-130, 130]
    `b`  | [-130, 130]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![CIELAB D65 3D](../images/lab-d65-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the CIELAB D50 color space.</figcaption>
</figure>

CIELAB D65 is the same as [CIELAB](#cielab-d50) except it uses a D65 white point.

_[Learn about CIELAB](https://en.wikipedia.org/wiki/CIELAB_color_space)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `a`      |
        `b`      |

    **Inputs:**
    : 
        As a D65 variant of CIELAB is not currently supported in the CSS spec, the parsed input and string output
        formats use the `#!css-color color()` function format using the custom name `#!css-color --lab-d65`:

        ```css-color
        color(--lab-d65 l a b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("lab-d65", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--lab-d65 l a b / a)` form.

        ```playground
        Color("lab-d65", [0, 0, 0], 1)
        Color("lab-d65", [0, 0, 0], 1).to_string()
        ```

## CIELCH

CIELAB generally is not an intuitive space to work with and instead is often converted to cylindrical coordinates with
hues represented as degrees and a chroma and lightness channel. The shape of the color space doesn't really change,
just how the colors are manipulated. CIELCH, like CIELAB, is available with a D50 white point that matches CSS and a
D65 white point.

### CIELCH D50

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `lch`

    **White Point:** D50

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 100]
    `c`  | [0, 150]
    `h`  | [0, 360)

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![CIELCH D50 3D](../images/lch-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the CIELCH D50 color space.</figcaption>
</figure>

The "CIELCH" or "CIEHLC" space is a color space based on [CIELAB](#cielab), which uses the polar coordinates C\*
(chroma, relative saturation) and h&deg; (hue angle, angle of the hue in the CIELAB color wheel) instead of the Cartesian
coordinates a\* and b\*. The CIELAB lightness L\* remains unchanged.

_[Learn about CIELCH](https://en.wikipedia.org/wiki/CIELAB_color_space#Cylindrical_representation:_CIELCh_or_CIEHLC)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `c`      | `chroma`
        `h`      | `hue`

    **Inputs:**
    : 
        Parsed input and string output formats support all valid CSS forms. In addition, we also allow the
        `#!css-color color()` function format using the custom name `#!css-color --lch`:

        ```css-color
        lch(l c h / a)          // Lch function
        color(--lch l c h / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("lch", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object will always default to the `#!css-color color(--lch l c h / a)`
        form, but the default string output will be the `#!css-color lch(l c h / a)` form.

        ```playground
        Color("lch", [0, 0, 0], 1)
        Color("lch", [0, 0, 0], 1).to_string()
        ```

### CIELCH D65

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `lch-d65`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 100]
    `c`  | [0, 160]
    `h`  | [0, 360)

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![CIELCH D65 3D](../images/lch-d65-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the CIELCH D65 color space.</figcaption>
</figure>

CIELCH D65 is the same as [CIELCH](#cielch-d50) except it uses a D65 white point.

_[Learn about CIELCH](https://en.wikipedia.org/wiki/CIELAB_color_space#Cylindrical_representation:_CIELCh_or_CIEHLC)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `c`      | `chroma`
        `h`      | `hue`

    **Inputs:**
    : 
        As a D65 variant of CIELCH is not currently supported in the CSS spec, the parsed input and string output
        formats use the `#!css-color color()` function format using the custom name `#!css-color --lch-d65`:

        ```css-color
        color(--lch-d65 l c h / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("lch-d65", [0, 0, 0], 1)
        ```

    **Outputs:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--lch-d65 l c h / a)` form.

        ```playground
        Color("lch-d65", [0, 0, 0], 1)
        Color("lch-d65", [0, 0, 0], 1).to_string()
        ```

## Oklab

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `oklab`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 1]
    `a`  | [-0.4, 0.4]
    `b`  | [-0.4, 0.4]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![Oklab](../images/oklab-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the Oklab color space.</figcaption>
</figure>


A new perceptual color space that claims to be simple to use, while doing a good job at predicting perceived lightness,
chroma and hue. It is called the Oklab color space, because it is an OK Lab color space.

_[Learn about Oklab](https://bottosson.github.io/posts/oklab/)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `a`      |
        `b`      |

    **Inputs:**
    : 
        Oklab is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --oklab`:

        ```css-color
        oklab(l a b / a)          // Oklab function
        color(--oklab l a b / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("oklab", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object will always default to the `#!css-color color(--oklab l a b / a)`
        form, but the default string output will be the `#!css-color oklab(l a b / a)` form.

        ```playground
        Color("oklab", [0, 0, 0], 1)
        Color("oklab", [0, 0, 0], 1).to_string()
        ```

## Oklch

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `oklch`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 1]
    `c`  | [0, 0.4]
    `h`  | [0, 360)

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![Oklch](../images/oklch-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the Oklch color space.</figcaption>
</figure>


Oklch is the cylindrical form of [Oklab](#oklab).

_[Learn about Oklch](https://bottosson.github.io/posts/oklab/)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `c`      | `chroma`
        `h`      | `hue`

    **Inputs**
    : 

        Oklab is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --oklch`:

        ```css-color
        oklch(l c h / a)          // Oklch function
        color(--oklch l c h / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object will always default to the `#!css-color color(--oklch l c h / a)`
        form, but the default string output will be the `#!css-color oklch(l a b / a)` form.

        ```playground
        Color("oklch", [0, 0, 0], 1)
        Color("oklch", [0, 0, 0], 1).to_string()
        ```

## CIELUV

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `luv`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 100]
    `u`  | [-215, 215]
    `v`  | [-215, 215]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![CIELUV 3D](../images/luv-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the CIELUV D65 color space.</figcaption>
</figure>

CIELUV is similar to CIELAB as they were both developed in 1976 as perceptually uniform color spaces, both are derived
from the color experiments in 1931 that brought us the XYZ color space, and neither are truly perceptually uniform.

The difference between the two comes from their intent. CIELAB attempted to create a space that aligned well with
human vision. CIELUV, on the other hand, was designed to be an easier-to-compute transformation of the 1931 CIE XYZ
color space.

CIELAB is more commonly used in subtractive color applications (printed pages, dyes, etc.), while CIELUV is better
suited in additive color applications such as display colorimetry (monitors, TVs, etc.).

_[Learn about CIELUV](https://en.wikipedia.org/wiki/CIELUV)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `u`      |
        `v`      |

    **Inputs:**
    : 
        As CIELUV D65 is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --luv`:

        ```css-color
        color(--luv l u v / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("luv", [0, 0, 0], 1)
        ```

    **Outputs**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--luv l u v / a)` form.

        ```playground
        Color("luv", [0, 0, 0], 1)
        Color("luv", [0, 0, 0], 1).to_string()
        ```

## CIELCH~uv~

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `lchuv`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 100]
    `c`  | [0, 220]
    `h`  | [0, 360)

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![CIELCH~uv~](../images/lchuv-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the CIELCH~uv~ color space.</figcaption>
</figure>

[CIELUV](#cieluv) is not an intuitive space to work with directly and instead is often converted to cylindrical
coordinates with hues represented as degrees and a chroma and lightness channel. The shape of the color space doesn't
really change, just how the colors are manipulated.

_[Learn about CIELCH~uv~](https://en.wikipedia.org/wiki/CIELUV)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `c`      | `chroma`
        `h`      | `hue`

    **Inputs:**
    : 
        As CIELCH~uv~ is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --lchuv`:

        ```css-color
        color(--lchuv l c h / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("lchuv", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--lchuv l c h / a)` form.

        ```playground
        Color("lchuv", [0, 0, 0], 1)
        Color("lchuv", [0, 0, 0], 1).to_string()
        ```

## Jzazbz

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `jzazbz`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `jz` | [0, 1]
    `az` | [-0.5, 0.5]
    `bz` | [-0.5, 0.5]

    ^\*^ Space is not bound to the range but is specified to enclose the full range of an HDR BT.2020 gamut and is used
    to define percentage inputs/outputs.

<figure markdown="1">

![Jzazbz](../images/jzazbz-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the Jzazbz color space.</figcaption>
</figure>

Jzazbz is a a color space designed for perceptual uniformity in high dynamic range (HDR) and wide color gamut (WCG)
applications. Conceptually it is similar to [CIELAB](#cielab), but claims the following improvements:

- Perceptual color difference is predicted by Euclidean distance.
- Perceptually uniform: MacAdam ellipses of just-noticeable-difference (JND) are more circular, and closer to the same
  sizes.
- Hue linearity: changing saturation or lightness has less shift in hue.

_[Learn about Jzazbz](https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `jz`     | `lightness`
        `az`     | `a`
        `bz`     | `b`

    **Inputs**
    : 
        As Jzazbz is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --jzazbz`:

        ```css-color
        color(--jzazbz jz az bz / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("jzazbz", [0, 0, 0], 1)
        ```

    **Output**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--jzazbz jz az bz / a)` form.

        ```playground
        Color("jzazbz", [0, 0, 0], 1)
        Color("jzazbz", [0, 0, 0], 1).to_string()
        ```

## JzCzhz

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `jzczhz`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `jz` | [0, 1]
    `cz` | [0, 0.5]
    `hz` | [0, 360)

    ^\*^ Space is not bound to the range but is specified to enclose the full range of an HDR BT.2020 gamut and is used
    to define percentage inputs/outputs.

<figure markdown="1">

![JzCzhz](../images/jzczhz-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the JzCzhz color space.</figcaption>
</figure>

JzCzhz is the cylindrical form of [Jzazbz](#jzazbz).

_[Learn about JzCzhz](https://www.osapublishing.org/oe/fulltext.cfm?uri=oe-25-13-15131&id=368272)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `jz`     | `lightness`
        `cz`     | `chroma`
        `hz`     | `hue`

    **Inputs**
    : 
        As JzCzhz is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --jzczhz`:

        ```css-color
        color(--jzczhz jz cz hz / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("jzczhz", [0, 0, 0], 1)
        ```

    **Output**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--jzczhz jz cz hz / a)` form.

        ```playground
        Color("jzczhz", [0, 0, 0], 1)
        Color("jzczhz", [0, 0, 0], 1).to_string()
        ```

## ICtCp

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `ictcp`

    **White Point:** D65

    **Coordinates:**

    Name       | Range^\*^
    ---------- | ---------
    `i`        | [0, 1]
    `ct`       | [-0.5, 0.5]
    `cp`       | [-0.5, 0.5]

    ^\*^ Space is not bound to the range but is specified to enclose the full range of an HDR BT.2020 gamut and is used
    to define percentage inputs/outputs.

<figure markdown="1">

![ICtCp](../images/ictcp-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the ICtCp color space.</figcaption>
</figure>

ICtCp is a color space format with better perceptual uniformity than [CIELAB](#cielab) and is used as a part of the
color image pipeline in video and digital photography systems for high dynamic range (HDR) and wide color gamut (WCG)
imagery. It was developed by Dolby Laboratories from the IPT color space by Ebner and Fairchild. It was designed with
the intention to replace YCbCr.

_[Learn about ICtCp](https://en.wikipedia.org/wiki/ICtCp)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `i`      |
        `ct`     |
        `cp`     |

    **Inputs:**
    : 
        As ICtCp is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --ictcp`:

        ```css-color
        color(--ictcp i ct cp / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("ictcp", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--ictcp i ct cp / a)` form.

        ```playground
        Color("ictcp", [0, 0, 0], 1)
        Color("ictcp", [0, 0, 0], 1).to_string()
        ```

## DIN99o

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `din99o`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 100]
    `a`  | [-55, 55]
    `b`  | [-55, 55]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![DIN99o](../images/din99o-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the DIN99o color space.</figcaption>
</figure>

The DIN99 color space system is a further development of the CIELAB color space system developed by the FNF / FNL 2
Colorimetry Working Committee. It takes the CIELAB space (with a D65 illuminant) and compresses it such that the space
yields better equidistant using Euclidean distance. The whole color space is essentially modified to better fit the
color distancing algorithm opposed to CIELAB which has adapted the color distancing algorithm to better fit the color
space, the latest iteration being ∆E^\*^~00~.

_[Learn about DIN99o](https://de.wikipedia.org/wiki/DIN99-Farbraum)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `a`      |
        `b`      |

    **Inputs:**
    : 
        As DIN99o is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --din99o`:

        ```css-color
        color(--din99o l u v / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("din99o", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--din99o l u v / a)` form.

        ```playground
        Color("din99o", [0, 0, 0], 1)
        Color("din99o", [0, 0, 0], 1).to_string()
        ```

## DIN99o Lch

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `lch99o`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | ---------
    `l`  | [0, 100]
    `c`  | [0, 60]
    `h`  | [0, 360)

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![DIN99o Lch](../images/lch99o-3d.png)

<figcaption markdown="1">The sRGB gamut represented within the DIN99o Lch color space.</figcaption>
</figure>

DIN99o Lch is the cylindrical form of [DIN99o](#din99o).

_[Learn about DIN99o Lch](https://de.wikipedia.org/wiki/DIN99-Farbraum)_
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `c`      | `chroma`
        `h`      | `hue`

    **Inputs:**
    : 
        As DIN99o Lch is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --lch99o`:

        ```css-color
        color(--lch99o jz cz hz / a)  // Color function
        ```

        When manually creating a color via raw data or specifying a color space as a parameter in a function, the color
        space name is always used:

        ```py
        Color("lch99o", [0, 0, 0], 1)
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--lch99o jz cz hz / a)` form.

        ```playground
        Color("lch99o", [0, 0, 0], 1)
        Color("lch99o", [0, 0, 0], 1).to_string()
        ```

## oRGB

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `orgb`

    **White Point:** D65

    **Coordinates:**

    Name  | Range^\*^
    ----- | -----
    `l`   | [0, 1]
    `cyb` | [-1, 1]
    `crg` | [-1, 1]

    ^\*^ Range denotes _in gamut_ colors, but the color space supports an extended range beyond the gamut.

<figure markdown="1">

![oRGB](../images/orgb-3d.png)

<figcaption>The sRGB gamut represented within the oRGB color space.</figcaption>
</figure>

A new color model that is based on opponent color theory. Like HSV, it is designed specifically for computer graphics.
However, it is also designed to work well for computational applications such as color transfer, where HSV falters.
Despite being geared towards computation, oRGB's natural axes facilitate HSV-style color selection and manipulation.
oRGB also allows for new applications such as a quantitative cool-to-warm metric, intuitive color manipulations and
variations, and simple gamut mapping. This new color model strikes a balance between simplicity and the computational
qualities of color spaces such as CIELAB.

[Learn more](https://graphics.stanford.edu/~boulos/papers/orgb_sig.pdf).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `luma`
        `cyb`    |
        `crb`    |

    **Inputs**
    : 

        The oRGB space is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --orgb`:

        ```css-color
        color(--orgb l cyb crb / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--orgb l cyb crg / a)` form.

        ```playground
        Color("orgb", [0, 0, 0], 1)
        Color("orgb", [0, 0, 0], 1).to_string()
        ```

## Hunter Lab

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `hunter-lab`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `l`  | [0, 100]
    `a`  | [-210, 210]
    `b`  | [-210, 210]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![oRGB](../images/hunter-lab-3d.png)

<figcaption>The sRGB gamut represented within the Hunter Lab color space.</figcaption>
</figure>

The Hunter Lab color space, defined in 1948 by Richard S. Hunter, is another color space referred to as "Lab". Like
CIELAB, it was also designed to be computed via simple formulas from the CIEXYZ space, but to be more perceptually
uniform than CIEXYZ. Hunter named his coordinates L, a, and b. The CIE named the coordinates for CIELAB as L*, a*, b* to
distinguish them from Hunter's coordinates.

[Learn more](https://support.hunterlab.com/hc/en-us/articles/203997095-Hunter-Lab-Color-Scale-an08-96a2).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `a`      |
        `b`      |

    **Inputs**
    : 

        The Hunter Lab space is not currently supported in the CSS spec, the parsed input and string output formats use
        the `#!css-color color()` function format using the custom name `#!css-color --hunter-lab`:

        ```css-color
        color(--hunter-lab l a b / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--hunter-lab l a b / a)` form.

        ```playground
        Color("hunter-lab", [0, 0, 0], 1)
        Color("hunter-lab", [0, 0, 0], 1).to_string()
        ```

## RLAB

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `rlab`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `l`  | [0, 100]
    `a`  | [-125, 125]
    `b`  | [-125, 125]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs in
    relation to the Display P3 color space.

<figure markdown="1">

![RLAB](../images/rlab-3d.png)

<figcaption>The sRGB gamut represented within the RLAB color space.</figcaption>
</figure>

The RLAB color-appearance space was developed by Fairchild and Berns for cross-media color reproduction applications in
which images are reproduced with differing white points, luminance levels, and/or surrounds.

[Learn more](https://scholarworks.rit.edu/cgi/viewcontent.cgi?article=1153&context=article).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `a`      |
        `b`      |

    **Inputs**
    : 

        The RLAB space is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --rlab`:

        ```css-color
        color(--rlab l a b / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--rlab l a b / a)` form.

        ```playground
        Color("rlab", [0, 0, 0], 1)
        Color("rlab", [0, 0, 0], 1).to_string()
        ```

## IPT

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `ipt`

    **White Point:** D65

    **Coordinates:**

    Name | Range^\*^
    ---- | -----
    `i`  | [0, 1]
    `p`  | [-1, 1]
    `t`  | [-1, 1]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs.

<figure markdown="1">

![IPT](../images/ipt-3d.png)

<figcaption>The sRGB gamut represented within the IPT color space.</figcaption>
</figure>

Ebner and Fairchild addressed the issue of non-constant lines of hue in their color space dubbed IPT. The IPT color
space converts D65-adapted XYZ data (XD65, YD65, ZD65) to long-medium-short cone response data (LMS) using an adapted
form of the Hunt-Pointer-Estevez matrix (M~HPE~(D65)).

The IPT color appearance model excels at providing a formulation for hue where a constant hue value equals a constant
perceived hue independent of the values of lightness and chroma (which is the general ideal for any color appearance
model, but hard to achieve). It is therefore well-suited for gamut mapping implementations.

[Learn more](https://www.researchgate.net/publication/21677980_Development_and_Testing_of_a_Color_Space_IPT_with_Improved_Hue_Uniformity.).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `i`      |
        `p`      |
        `t`      |

    **Inputs**
    : 

        The IPT space is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --ipt`:

        ```css-color
        color(--ipt i p t / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--ipt i p t / a)` form.

        ```playground
        Color("ipt", [0, 0, 0], 1)
        Color("ipt", [0, 0, 0], 1).to_string()
        ```

## IgPgTg

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `ipt`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `ig` | [0, 1]
    `pg` | [-1, 1]
    `tg` | [-1, 1]

    ^\*^ Space is not bound to the range and is only used as a reference to define percentage inputs/outputs.

<figure markdown="1">

![IgPgTg](../images/igpgtg-3d.png)

<figcaption>The sRGB gamut represented within the IgPgTg color space.</figcaption>
</figure>

IgPgTg uses the same structure as IPT, an established hue-uniform color space utilized in gamut mapping applications.
While IPT was fit to visual data on the perceived hue, IGPGTG was optimized based on evidence linking the peak
wavelength of Gaussian-shaped light spectra to their perceived hues.

[Learn more](https://www.researchgate.net/publication/21677980_Development_and_Testing_of_a_Color_Space_IPT_with_Improved_Hue_Uniformity.).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `ig`     |
        `pg`     |
        `tg`     |

    **Inputs**
    : 

        The IgPgTg space is not currently supported in the CSS spec, the parsed input and string output formats use the
        `#!css-color color()` function format using the custom name `#!css-color --igpgtg`:

        ```css-color
        color(--igpgtg ig pg tg / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--igpgtg ig pg tg / a)` form.

        ```playground
        Color("igpgtg", [0, 0, 0], 1)
        Color("igpgtg", [0, 0, 0], 1).to_string()
        ```

## Prismatic

<div class="info-container" markdown="1">
!!! info inline end "Properties"

    **Name:** `prismatic`

    **White Point:** D65

    **Coordinates:**

    Name | Range
    ---- | -----
    `l`  | [0, 1]
    `r`  | [0, 1]
    `g`  | [0, 1]
    `b`  | [0, 1]

<figure markdown="1">

![Prismatic](../images/prismatic.png)

<figcaption>Prismatic Illustrations</figcaption>
</figure>

The Prismatic model introduces a simple transform of the RGB color cube into a light/dark dimension and a 2D hue. The
hue is a normalized (barycentric)triangle with pure red, green, and blue at the vertices, often called the Maxwell Color
Triangle.  Each cross section of the space is the same barycentric triangle, and the light/dark dimension runs zero to
one for each hue so the whole color volume takes the form of a prism.

[Learn more](http://psgraphics.blogspot.com/2015/10/prismatic-color-model.html).
</div>

??? abstract "ColorAide Details"

    **Channel Aliases:**
    : 
        Channels | Aliases
        -------- | -------
        `l`      | `lightness`
        `r`      | `red`
        `g`      | `green`
        `b`      | `blue`

    **Inputs**
    : 

        The Prismatic space is not currently supported in the CSS spec, the parsed input and string output formats use
        the `#!css-color color()` function format using the custom name `#!css-color --prismatic`:

        ```css-color
        color(--prismatic l r g b / a)  // Color function
        ```

    **Output:**
    : 
        The string representation of the color object and the default string output use the
        `#!css-color color(--prismatic l r g b / a)` form.

        ```playground
        Color("prismatic", [0, 0, 0, 0], 1)
        Color("prismatic", [0, 0, 0, 0], 1).to_string()
        ```

<style>
.info-container {display: inline-block;}
</style>
