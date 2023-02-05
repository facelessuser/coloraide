# Contrast

ColorAide provides a number of utilities related to luminance and contrast.

## Relative Luminance

In the CIE XYZ and xyY color spaces, the Y parameter is linear to changes in the volume of light. Specifically this
refers to the amount of reflected light where 1.0 is assumed to be a perfect reflector in relation to the reference
white.

The `luminance` method exposes access to this value to make it quick and easy to query the relative luminance, or Y
parameter from XYZ D65 after converting the current color.

```playground
Color("black").luminance()
Color("white").luminance()
Color("blue").luminance()
```

!!! tip "Luminance and WCAG 2.1"
    Luminance as described in the WCAG 2.1 spec is essentially the exact same as what the luminance method returns. The
    only difference is the lower precision by which they calculate the value:

    ```playground
    r, g, b = Color('purple')[:-1]
    r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
    g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
    b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
    l = (0.2126 * r + 0.7152 * g + 0.0722 * b)
    print(l)
    Color('purple').convert('xyz-d65')['y']
    ```

## Contrast

Chromatic contrast refers to the ability to see the difference of a colored object against a colored background. This
can be very important when it comes to visual design and other fields. Determining contrast has been explored in many
different ways and, depending on the application, there may be approaches to contrast that are more favorable. In the
context of the web, contrast often refers to the ability to see text on a colored background and is of particular
importance to those that suffer from visual impairments or disabilities.

It should be noted that as we talk about contrast, we will refer to the colors as the **text** and **background** as
this is often the context in which such a function is used. As far as ColorAide is concerned, the **text** is always the
calling color and the **background** is the input parameter. It is important to note this as not all contrast algorithms
are symmetrical, and can differ depending which color is referenced as **text**, and which is referenced as the
**background**.

At this time, ColorAide only offers a handful of contrast approaches, and they can be by using the `contrast()` method.

```playground
Color("blue").contrast("red")
```

To select different contrast methods, simply use the `method` parameter.

```playground
Color("blue").contrast("red", method='wcag21')
```

Methods  | Symmetrical         | Description
-------- | ------------------  | -----------
`wcag21` | :octicons-check-16: | WCAG 2.1 contrast ratio.
`lstar`  | :octicons-check-16: | Color difference between two tones in the HCT color space.


### WCAG 2.1 Contrast Ratio

!!! success "The WCAG 2.1 contrast ratio is registered in `Color` by default"

ColorAide implements the color contrast ratio as outlined in the [WCAG 2.1 spec](https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio).
This is currently, the default contrast method. It is not without fault, but is currently the standard outlined for the
web.

The contrast ratio as outlined in the WCAG 2.1 specification is simply the ratio of color luminance from a foreground
and background color and is very easy to determine if you are able to acquire the luminance of the two colors.

```py
# Where `l1` is the lighter luminance and `l2` the darker
contrast_ratio = (l1 + 0.05) / (l2 + 0.05)
```

This method can be used by specifying `wcag21` as the contrast method.

```playground
Color("blue").contrast("red", method='wcag21')
```

### Lstar Lightness Difference

!!! failure "The Lstar contrast method is **not** registered in `Color` by default"

Google's Material Design uses a new color space called [HCT](./colors/hct.md). It uses the hue and chroma from
[CAM16](./colors/cam16.md) and the tone/lightness from CIELab. For contrast, they determined using tones that are
"far enough apart" in the HCT color space was a good indication of sufficient contrast. Since HCT tone is exactly the
same as CIELab's lightness (also known as L\*), we've referred to this approach as Lstar.

Lstar's color difference approach to contrast is quite simple, it's literally the difference between two color's
lightness as provided by CIELab. This method does not care which color is text or background.

```playground
Color('hct', [30, 20, 70]).contrast(Color('hct', [30, 20, 50]), method='lstar')
```

In order to use this contrast method, the plugin must be registered. This assumes the CIELab color space is currently
registered, which it is by default.

```py
from coloraide import Color as Base
from coloraide.contrast.lstar import LstarContrast

class Color(Base): ...

Color.register(LstarContrast())
```
