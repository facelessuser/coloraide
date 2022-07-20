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

There have actually been numerous approaches to determining reliable contrast. ColorAide currently only implements the
color contrast ratio as outlined in the [WCAG 2.1 spec](https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio), but has done
so as a plugin to allow for expanding implementations in the future to allow for more reliable approaches as the WCAG
2.1 approach is not without flaws.

It should be noted that as we talk about contrast, we will refer to the colors as the **text** and **background** as
this is generally the context in which such a function is used. The **text** is always the calling color and the
**background** is the input parameter. Not all contrast algorithms care about such details, but it is important to note
as some future algorithms assuredly will.

```py
text.contrast(background)
```

While in all normal circumstances a negative luminance should not occur, if one does occur, the luminance will be
clamped to zero.

```py
# Where `l1` is the lighter luminance and `l2` the darker
contrast_ratio = (l1 + 0.05) / (l2 + 0.05)
```
To get the this contrast ratio between two colors, simply pass in the second color:

```playground
Color("blue").contrast("red")
```

!!! warning "Distancing and Symmetry"
    It should be noted that not all contrast algorithms are symmetrical. Some are order dependent.

Methods  | Symmetrical         | Description
-------- | ------------------  | -----------
`wcag21` | :octicons-check-16: | WCAG 2.1 contrast ratio.

To use different methods, simply specify the method via the `method` parameter:

```playground
Color("blue").contrast("red", method='wcag21')
```
