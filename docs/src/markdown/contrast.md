# Contrast

## Relative Luminance

ColorAide provides a couple of contrast related tools out of the box. Relative luminance is used to calculate the
contrast ratio. To get the luminance, simply call the `luminance` method:

```pycon3
>>> Color("black").luminance()
0.0
>>> Color("white").luminance()
1.00000009242344
>>> Color("blue").luminance()
0.06061693873868999
```

## Contrast Ratio

To get the contrast ratio between two colors, simply pass in the second color:

```pycon3
>>> Color("blue").contrast("red")
2.463497175178265
```
