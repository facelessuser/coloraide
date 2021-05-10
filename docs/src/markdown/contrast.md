# Contrast

## Relative Luminance

Relative luminance is used to calculate the contrast ratio. To get the luminance, simply call the `luminance` method:

```playground
Color("black").luminance()
Color("white").luminance()
Color("blue").luminance()
```

## Contrast Ratio

To get the contrast ratio between two colors, simply pass in the second color:

```playground
Color("blue").contrast("red")
```
