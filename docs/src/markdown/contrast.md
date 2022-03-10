# Contrast

ColorAide provides a number of utilities related to luminance and contrast, or better put, contrast as defined by
[Web Content Accessibility Guidelines (WCAG) 2.0 specification](https://www.w3.org/TR/WCAG20/).

## Relative Luminance

In the CIE XYZ and xyY color spaces, the Y parameter is linear to changes in the volume of light. Specifically this
refers to the amount of reflected light where 1.0 is assumed to be a perfect reflector in relation to the reference
white.

The WCAG in the 2.0 specification provides the following formula to acquire the relative luminance from an sRGB
color. What is not explicitly said, but is happening, is the formula removes the gamut correction from each of the color
channels and then calculates the luminance. What we end up with is actually the Y channel of the XYZ color space with a
D65 white point.

```playground
r, g, b = Color('purple').coords()
r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
l = (0.2126 * r + 0.7152 * g + 0.0722 * b)
print(l)
Color('purple').convert('xyz-d65').y
```

For convenience, the `luminance` method exposes access to this value to make it quick and easy query the relative
luminance, or Y parameter from XYZ D65, for a given color.

```playground
Color("black").luminance()
Color("white").luminance()
Color("blue").luminance()
```

## Contrast Ratio

WCAG 2.0 spec specifies the contrast ratio using the equation below.

```py
# Where `l1` is the lighter luminance and `l2` the darker
contrast_ratio = (l1 + 0.05) / (l2 + 0.05)
```
To get the this contrast ratio between two colors, simply pass in the second color:

```playground
Color("blue").contrast("red")
```
