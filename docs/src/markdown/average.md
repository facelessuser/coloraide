# Color Averaging

Color averaging is the process of calculating an average color from a set of other colors by taking the mean of each
color channel.

Averaging under ColorAide can take as many colors as desired and will return a color that represents the average. This
is not to be confused with interpolation which employs a different technique, but in certain situations, it can sort of
function like mixing multiple colors.

## Rectangular Space Averaging

ColorAide, by default, averages in rectangular color spaces, the default being Linear sRGB. If desired, other color
spaces can be used, such as perceptually uniform spaces like Oklab.

```py play
Color.average(['red', 'blue'])
Color.average(['red', 'blue'], space='srgb')
Color.average(['red', 'blue'], space='oklab')
```

Averaging is not restricted to any certain amount of colors.

```py play
Color.average(['red', 'yellow', 'orange', 'green'])
```

## Cylindrical Space Averaging

ColorAide can average colors in rectangular spaces and cylindrical spaces. When applying averaging in a cylindrical
space, hues will be averaged taking the circular mean.

Colors that appear to be achromatic will have their hue treated as undefined, even if the hue is defined.

Cylindrical averaging may provide very different results that averaging in rectangular spaces.

```py play
Color.average(['purple', 'green', 'blue'])
Color.average(['purple', 'green', 'blue'], space='hsl')
```

It should be noted that when averaging colors with hues which are evenly distributed around the color wheel, the result
will produce an achromatic hue. When achromatic hues are produced during circular mean, the color will discard
chroma/saturation information, producing an achromatic color.

```py play
Color.average(['red', 'green', 'blue'], space='hsl')
```

## Averaging with Transparency

ColorAide, by default, will account for transparency when averaging colors. Colors which are more transparent will have
less of an impact on the average. This is done by premultiplying the colors before averaging, essentially weighting the
color components where more opaque colors have a greater influence on the average.

```py play
for i in range(12):
    Color.average(
        [f'color(srgb 0 1 0 / {i / 11})', 'color(srgb 0 0 1)']
    )
```

There are cases where this approach of averaging may not be desired. It may be that color averaging is desired without
considering transparency. If so, `premultiplied` can be disabled by setting it to `#!py False`. While the average of
transparency is calculated, it can be discarded from the final result if desired.

It should be noted that when a color is fully transparent, its color components will be ignored, regardless of the
`premultiplied` parameter, as fully transparent colors provide no meaningful color information.

```py play
for i in range(12):
    Color.average(
        [f'color(srgb 0 1 0 / {i / 11})', 'color(srgb 0 0 1)'],
        premultiplied=False,
    )
```

## Averaging with Undefined Values

When averaging with undefined values, ColorAide will not consider the undefined values in the average. This is mainly
provided for averaging cylindrical colors, particularly achromatic colors.

```py play
Color.average(['white', 'color(srgb 0 0 1)'], space='hsl')
```

When averaging hues in a polar space, implied achromatic hues are also treated as undefined as counting such hues would
distort the average in a non-meaningful way.

```py play
Color.average(['hsl(30 0 100)', 'hsl(240 100 50 / 1)'], space='hsl')
```

While undefined logic is intended to handle achromatic hues, this logic will be applied to any channel. It should be
noted that no attempt to carry forward the undefined values through conversion is made at this time. Conversions will
remove any undefined status unless the channel is an achromatic hues.

```py play
for i in range(12):
    Color.average(['darkgreen', f'color(srgb 0 none 0 / {i / 11})', 'color(srgb 0 0 1)'])
```

When `premultiplied` is enabled, premultiplication will not be applied to a color if its `alpha` is undefined as it is
unknown how to weight the color, instead the color is treated with full weight.

```py play
Color.average(['darkgreen', f'color(srgb 0 0.50196 0 / none)', 'color(srgb 0 0 1)'])
```
