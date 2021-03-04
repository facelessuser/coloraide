### Supported Colors

### HSV

[Learn about HSV](https://en.wikipedia.org/wiki/HSL_and_HSV)

**White Point**
:   D65

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    hue        | 0 - 360
    saturation | 0 - 100
    value      | 0 - 100

**Supported Inputs**
: 
    ```pycon3
    >>> Color('hsv', [0, 0, 100])
    color(hsv 0 0 100 / 1)
    >>> Color('color(hsv 0 0 100)')
    color(hsv 0 0 100 / 1)
    >>> Color('color(hsv 0 0% 100%)')
    color(hsv 0 0 100 / 1)
    ```

### sRGB

[Learn about sRGB](https://en.wikipedia.org/wiki/SRGB)

**White Point**
:   D65

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

**Supported Inputs**
: 
    ```pycon3
    >>> Color("srgb", [1, 1, 1])
    color(srgb 1 1 1 / 1)
    >>> Color("white")
    color(srgb 1 1 1 / 1)
    >>> Color("#ffffff")
    color(srgb 1 1 1 / 1)
    >>> Color("rgb(100% 100% 100%)")
    color(srgb 1 1 1 / 1)
    >>> Color("rgb(255 255 255)")
    color(srgb 1 1 1 / 1)
    >>> Color("rgb(255 255 255 / 1)")
    color(srgb 1 1 1 / 1)
    >>> Color("rgba(255, 255, 255, 1)")
    color(srgb 1 1 1 / 1)
    >>> Color("rgb(255, 255, 255)")
    color(srgb 1 1 1 / 1)
    >>> Color('color(srgb 100% 100% 100%)')
    color(srgb 1 1 1 / 1)
    >>> Color('color(srgb 1 1 1 / 1)')
    color(srgb 1 1 1 / 1)
    ```

### HSL

[Learn about HSL](https://en.wikipedia.org/wiki/HSL_and_HSV)

**White Point**
:   D65

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    hue        | 0 - 360
    saturation | 0 - 100
    lightness  | 0 - 100

**Supported Inputs**
: 
    ```pycon3
    >>> Color("hsl", [0, 0, 100])
    color(hsl 0 0 100 / 1)
    >>> Color("hsl(0 0% 100%)")
    color(hsl 0 0 100 / 1)
    >>> Color("hsl(0, 0%, 100%)")
    color(hsl 0 0 100 / 1)
    >>> Color("hsl(0 0% 100% / 1)")
    color(hsl 0 0 100 / 1)
    >>> Color("hsla(0, 0%, 100%, 1)")
    color(hsl 0 0 100 / 1)
    >>> Color("color(hsl 0 0% 100%)")
    color(hsl 0 0 100 / 1)
    >>> Color("color(hsl 0 0 100 / 1)")
    color(hsl 0 0 100 / 1)
    ```

### HWB

[Learn about HWB](https://en.wikipedia.org/wiki/HWB_color_model)

**White Point**
:   D65

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    hue        | 0 - 360
    whiteness  | 0 - 100
    blackness  | 0 - 100

**Supported Inputs**
: 
    ```pycon3
    >>> Color("hwb", [0, 100, 0])
    color(hwb 0 100 0 / 1)
    >>> Color("color(hwb 0 100 0)")
    color(hwb 0 100 0 / 1)
    >>> Color("hwb(0 100% 0%)")
    color(hwb 0 100 0 / 1)
    >>> Color("hwb(0, 100%, 0%)")
    color(hwb 0 100 0 / 1)
    >>> Color("hwb(0 100% 0% / 1)")
    color(hwb 0 100 0 / 1)
    >>> Color("hwb(0, 100%, 0%, 1)")
    color(hwb 0 100 0 / 1)
    >>> Color("color(hwb 0 100% 0%)")
    color(hwb 0 100 0 / 1)
    >>> Color("color(hwb 0 100 0 / 1)")
    color(hwb 0 100 0 / 1)
    ```

### Lab

[Learn about Lab](https://en.wikipedia.org/wiki/CIELAB_color_space)

**White Point**
:   D50

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    lightness  | 0 - 100
    a          | +/-160 - +/-160
    b          | +/-160 - +/-160

**Supported Inputs**
: 
    ```pycon3
    >>> Color("lab", [100, 0, 0])
    color(lab 100 0 0 / 1)
    >>> Color("color(lab 100  0  0)")
    color(lab 100 0 0 / 1)
    >>> Color("lab(100%  0  0)")
    color(lab 100 0 0 / 1)
    >>> Color("lab(100%,  0,  0, 1)")
    color(lab 100 0 0 / 1)
    >>> Color("lab(100%  0  0 / 1)")
    color(lab 100 0 0 / 1)
    >>> Color("color(lab 100%  0  0)")
    color(lab 100 0 0 / 1)
    >>> Color("color(lab 100 0 0 / 1)")
    color(lab 100 0 0 / 1)
    ```

### LCH

[Learn about LCH](https://en.wikipedia.org/wiki/CIELAB_color_space#Cylindrical_representation:_CIELCh_or_CIEHLC)

**White Point**
:   D50

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    lightness  | 0 - 100
    chroma     | 0 - 100
    hue        | 0 - 360

**Supported Inputs**
: 
    ```pycon3
    >>> Color("lch", [100, 0, 0])
    color(lch 100 0 0 / 1)
    >>> Color("color(lch 100  0  0)")
    color(lch 100 0 0 / 1)
    >>> Color("lch(100%  0  0)")
    color(lch 100 0 0 / 1)
    >>> Color("lch(100%,  0,  0, 1)")
    color(lch 100 0 0 / 1)
    >>> Color("lch(100%  0  0 / 1)")
    color(lch 100 0 0 / 1)
    >>> Color("color(lch 100%  0  0)")
    color(lch 100 0 0 / 1)
    >>> Color("color(lch 100 0 0 / 1)")
    color(lch 100 0 0 / 1)
    ```

### XYZ

[Learn about XYZ](https://en.wikipedia.org/wiki/CIE_1931_color_space)

**White Point**
:   D50

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    x          | 0 - 1
    y          | 0 - 1
    z          | 0 - 1

**Supported Inputs**
: 
    ```pycon3
    >>> Color("xyz", [0.96422, 1, 0.82521])
    color(xyz 0.96422 1 0.82521 / 1)
    >>> Color("color(xyz 0.96422 1 0.82521)")
    color(xyz 0.96422 1 0.82521 / 1)
    ```

### Display P3

[Learn about Display P3](https://en.wikipedia.org/wiki/DCI-P3#Display_P3)

**White Point**
:   D65

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

**Supported Inputs**
: 
    ```pycon3
    >>> Color("display-p3", [1, 1, 1])
    color(display-p3 1 1 1 / 1)
    >>> Color("color(display-p3 1 1 1)")
    color(display-p3 1 1 1 / 1)
    >>> Color("color(display-p3 100% 100% 100%)")
    color(display-p3 1 1 1 / 1)
    ```

### Adobe(r) RGB Compatible

[Learn about Adobe(r) RGB Compatible](https://en.wikipedia.org/wiki/Adobe_RGB_color_space)

**White Point**
:   D65

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

**Supported Inputs**
: 
    ```pycon3
    >>> Color("a98-rgb", [1, 1, 1])
    color(a98-rgb 1 1 1 / 1)
    >>> Color("color(a98-rgb 1 1 1)")
    color(a98-rgb 1 1 1 / 1)
    >>> Color("color(a98-rgb 100% 100% 100%)")
    color(a98-rgb 1 1 1 / 1)
    ```

### REC.2020

[Learn about REC.2020](https://en.wikipedia.org/wiki/Rec._2020)

**White Point**
:   D65

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

**Supported Inputs**
: 
    ```pycon3
    >>> Color("rec2020", [1, 1, 1])
    color(rec2020 1 1 1 / 1)
    >>> Color("color(rec2020 1 1 1)")
    color(rec2020 1 1 1 / 1)
    >>> Color("color(rec2020 100% 100% 100%)")
    color(rec2020 1 1 1 / 1)
    ```

### ProPhoto

[Learn about ProPhoto](https://en.wikipedia.org/wiki/ProPhoto_RGB_color_space)

**White Point**
:   D50

**Coordinates**
: 
    Name       | Range
    ---------- | -----
    red        | 0 - 1
    green      | 0 - 1
    blue       | 0 - 1

**Supported Inputs**
: 
    ```pycon3
    >>> Color("prophoto-rgb", [1, 1, 1])
    color(prophoto-rgb 1 1 1 / 1)
    >>> Color("color(prophoto-rgb 1 1 1)")
    color(prophoto-rgb 1 1 1 / 1)
    >>> Color("color(prophoto-rgb 100% 100% 100%)")
    color(prophoto-rgb 1 1 1 / 1)
    ```
