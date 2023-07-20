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

```py play
Color.average(['orange', 'yellow', 'red'], space='srgb')
Color.average(['orange', 'yellow', 'red'], space='hsl')
```

Because calculations are done in a cylindrical space, the averaged colors can be different than what is acquired with
rectangular space averaging.

```py play
Color.average(['purple', 'green', 'blue'], space='srgb')
Color.average(['purple', 'green', 'blue'], space='hsl')
```

## Averaging with Transparency

ColorAide, by default, will account for transparency when averaging colors. Colors which which are more transparent
will have less of an impact on the average. This is done by premultiplying the colors before averaging.

```py play
Steps([Color('darkgreen'), Color('color(srgb 0 0.50196 0 / 1)'), Color('color(srgb 0 0 1)')])
for i in range(12):
    Color.average(['darkgreen', f'color(srgb 0 0.50196 0 / {i / 11})', 'color(srgb 0 0 1)'], space='srgb')
```

If you'd like to average the channels without taking transparency into consideration, simply set `premultiplied` to
`#!py False`.

```py play
Steps([Color('darkgreen'), Color('color(srgb 0 0.50196 0 / 1)'), Color('color(srgb 0 0 1)')])
for i in range(12):
    Color.average(['darkgreen', f'color(srgb 0 0.50196 0 / {i / 11})', 'color(srgb 0 0 1)'], space='srgb', premultiplied=False)
```

## Averaging with Undefined Values

When averaging with undefined values, ColorAide will not consider the undefined values in the average.
```py play
for i in range(12):
    Color.average(['darkgreen', f'color(srgb 0 none 0 / {i / 11})', 'color(srgb 0 0 1)'], space='srgb')

```

When `premultiplied` is enabled, premultiplication will not be applied to a color if its `alpha` is undefined.

```py play
Color.average(['darkgreen', f'color(srgb 0 0.50196 0 / none)', 'color(srgb 0 0 1)'], space='srgb')
```
