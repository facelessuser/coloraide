# ColorAide

## Overview

ColorAide is a color library for Python. It was written to handle most modern CSS colors that are available and that
will be available. Most of the conversion algorithms come straight from the [CSS specifications][css-spec-convert].

In the process of developing this library, we also stumbled upon [Color.js][colorjs] which is created/maintained by the
co-authors of some of the recent CSS color specifications. Some work, such as their gamut mapping algorithm using LCH
chroma was lifted, and it eventually also helped influence some the API, but is not intended to match the work they are
doing over there.

Currently this project is in a early stage, and while usable, some things may change as we get closer to a stable
release.

With ColorAide, you can specify a color, convert it to other color spaces, mix it with other colors, output it different
CSS formats, and various other things.

## Installation

You can install ColorAide via Python's `pip`:

`pip install coloraide`.

If you need to upgrade

## Creating Colors

The `Color` object can be imported from either `coloraide.css` or `coloraide.colors`. Generally, it is recommended to
import the `Color` object from `coloraide.css` as this gives the ability to create colors using CSS syntax and output
colors in CSS format. `coloraide.colors` only accepts and outputs colors the generic form `color(space coords / alpha)`,
it is more the base form.

```py3
from coloraide.css import Color
```

Afterwards, you can begin working with colors. You can import CSS syntax.

```pycon3
>>> Color("red")
color(srgb 1 0 0 / 1)
>>> Color("#ff0000")
color(srgb 1 0 0 / 1)
>>> Color("rgb(255 0 0 / 1)")
color(srgb 1 0 0 / 1)
```

You can see, that we can use all sorts of valid CSS syntax, and we get the same color `#!color red`.

You can also insert raw data points directly, but notice, when doing this, you are required to enter the data as it is
used internally, and in the case for sRGB, the channels are in the range of \[0, 1\].

```pycon3
>>> Color("srgb", [0.5, 0, 1], 0.3)
color(srgb 0.5 0 1 / 0.3)
```

So in the example above, the raw data is parsed, and we get a transparent color in the sRGB space:
`#!color color(srgb 0.5 0 1 / 0.3)`.

You can also pass in other color objects, which is really only useful if you've subclassed the `Color` object and want
to cast the object back to the standard one.

```pycon3
>>> from coloraide.colors import Color as Generic
>>> from coloraide.css import Color
>>> generic = Generic("color(srgb 0.1 0.5 0.2)")
>>> generic.to_string()
'color(srgb 0.1 0.5 0.2)'
>>> Color(generic).to_string()
'rgb(25.5 127.5 51)'
```

The same color creation can be preformed from a color's `new` class method as well. New accepts the same inputs
as the class object itself.

```pycon3
>>> color1 = Color("red")
>>> color2 = color1.new("blue")
>>> color1, color2
(color(srgb 1 0 0 / 1), color(srgb 0 0 1 / 1))
```

## Cloning

The `clone` method is an easy way to duplicate the current color object.

Here we clone the `#!color green` object so we have two.

```pycon3
>>> c1 = Color("green")
>>> c2 = c1.clone()
>>> c1, c2
(color(srgb 0 0.50196 0 / 1), color(srgb 0 0.50196 0 / 1))
```

## Updating

A color can be "updated" using another color object. When an update occurs, the current color space is updated with the
data from the second color, but the color space does not change. It is basically the equivalent of converting the second
color to the color space of the first and then updating all the coordinates (including alpha). The input parameters
are identical to the `new` method, so you can use a color object, a color string, or even raw data points.

Here we update the `#!color red` color to `#!color blue`:

```pycon3
>>> color1 = Color("red")
>>> color2 = Color("blue")
>>> color1.update(color2)
color(srgb 0 0 1 / 1)
>>> color1, color2
(color(srgb 0 0 1 / 1), color(srgb 0 0 1 / 1))
```

Here we update the sRGB `#!color red` with the color `#!color lch(100% 50 130)`. Notice that the result is still in the
sRGB color space, but the color is bigger than the sRGB color space making the color out of gamut:
`#!color color(srgb 0.82374 1.0663 0.69484 / 1)`.

```pycon3
>>> Color("red").update("lch(100% 50 130)")
color(srgb 0.82374 1.0663 0.69484 / 1)
```

## Mutating

"Mutating" is similar to [updating](#updating) except that it will update the color and the color space from another
color. The input parameters are identical to the `new` method, so you can use a color object, a color string, or even
raw data points.

Here the `#!color red` color object literally becomes `#!color lch(50% 50 130)`.

```pycon3
>>> Color("red").mutate("lch(50% 50 130)")
color(lch 50 50 130 / 1)
```

## Converting

Colors can be converted to other color spaces as needed. Converting will always return a new color unless `in_place` is
set `True`.

For instance, if we had a color `#!color yellow`, and we needed to work with it in another color space, we
could simply call the `convert` method. In the example below, we convert the `#!color yellow`, which is in the
sRGB color space, to the Lab color space which gives us `#!color color(lab 97.607 -15.753 93.388 / 1)`.

```pycon3
>>> Color('yellow').convert("Lab")
color(lab 97.607 -15.753 93.388 / 1)
```

## Coordinates

To get the numerical value of coordinates, there are various ways.

1. You can read the channel property directly:

    ```pycon3
    >>> color = Color("orange")
    >>> color.red
    1.0
    ```

2. You can also call the `get` method and send in the name of the channel.

    ```pycon3
    >>> color = Color("orange")
    >>> color.get("green")
    0.6470588235294118
    ```

3. You can retrieve all the coordinates at once.

    ```pycon3
    >>> color = Color("orange")
    >>> color.coords()
    [1.0, 0.6470588235294118, 0.0]
    ```

    Alpha is never included in `coords` and must be accessed via the `alpha` property.

## Modifying Coordinates

You can change the value of the current color by adjusting the channel coordinates directly via the named property.

```pycon3
>>> color = Color("red")
>>> color.to_string()
'rgb(255 0 0)'
>>> color.green = 0.5
>>> color.to_string()
'rgb(255 127.5 0)'
```

When doing so, keep in mind, you are adjusting the internal coordinate, and you must modify it within the range in which
it is stored, and for sRGB, it is in the range of \[0, 1\]. If you'd like to modify it with parameters similar to what
you'd use in CSS, you can specify coordinates as a string, and they will be parsed accordingly.

```pycon3
>>> color = Color("red")
>>> color.to_string()
'rgb(255 0 0)'
>>> color.green = "128"
>>> color.to_string()
'rgb(255 128 0)'
```

In most cases, this would be identical to the units used in CSS, but sRGB has to distinguish hex form from normal floats
and integers, so you have to append `#` to sRGB coordinates if you wish to treat them as hex.

```pycon3
>>> color = Color("red")
>>> color.to_string()
'rgb(255 0 0)'
>>> color.green = "#33"
>>> color.to_string()
'rgb(255 51 0)'
```

If desired, you can also set attributes with the `set` method. As these methods return a reference to the class, you can
chain these settings together.

```pycon3
>>> Color("white").set("red", "0%").set("green", "50%").to_string()
'rgb(0 127.5 255)'
```

## Contrast

ColorAide gives access to the relative luminance of colors. Relative luminance is acquired by translating the color to
the XYZ color space and reading the Y channel.

Looking at the color `#!color orange` we see if we convert it to the XYZ color space, we get
`#!color color(xyz 0.58096 0.49224 0.05047)`. It can be noted that the Y coordinate is `0.49224`, which matches the
return of `luminance`.

```
>>> Color("orange").luminance()
0.49223879421047334
```

If given two colors, we can use the relative luminance and calculate the contrast ratio between the two colors. We
can simply call the `contrast_ratio` method:

```pycon3
>>> Color("red").contrast_ratio("blue")
2.463497175178265
```

## Interpolating

The `interpolation` method allows a user to create an interpolation function. This can be used to create a list of
gradient colors, or whatever the desired needs are.

Interpolation functions are returned and accept an input between 0 - 1. Values outside of this range will not be
interpolated, but extrapolated. Extrapolated values may not be as expected.

Here we create a an interpolation between `#!color lch(50% 50 0)` and `#!color lch(90% 50 20)`. We then step through
values of `0.1`, `0.2`, and `0.3` which creates: `#!color lch(54% 49.728 1.9707 / 1)`,
`#!color lch(58% 49.515 3.9608 / 1)`, `#!color lch(62% 49.363 5.9656 / 1)`.

```pycon3
>>> i = Color("lch(50% 50 0)").interpolate("lch(90% 50 20)")
>>> i(0.1)
color(lch 54 49.728 1.9707 / 1)
>>> i(0.2)
color(lch 58 49.515 3.9608 / 1)
>>> i(0.3)
color(lch 62 49.363 5.9656 / 1)
```

If desired, we can target specific channels for mixing which will keep all the other channels constant on the base
color. In this example, we have a base color of `#!color lch(52% 58.1 22.7)` which we mix with
`#!color lch(56% 49.1 257.1)`. We also specify the that we want to only mix the `hue` channel. The final color is
`#!color lch(52% 58.1 351.59)`. Notice that only the `hue` has changed.

```pycon3
>>> i = Color("lch(52% 58.1 22.7)").interpolate("lch(56% 49.1 257.1)", space="lch", adjust=["hue"])
>>> i(0.2477).to_string()
'lch(52% 58.1 351.59)'
```

Additionally, hues are special, and we can control the way the interpolation is evaluated. The `hue` parameter
accepts such values as `longer` or `shorter`, `shorter` being the default (see API for all options). In this example,
we run the same command, but specify that the interpolation should use the longer angle between the two hues. This time,
when we mix `#!color lch(52% 58.1 22.7)` and `#!color lch(56% 49.1 257.1)`, we get a different color
(`#!color lch(52% 58.1 80.761)`) as we interpolated in between the larger angle between the two points.

```pycon3
>>> i = Color("lch(52% 58.1 22.7)").interpolate("lch(56% 49.1 257.1)", space="lch", adjust=["hue"], hue="longer")
>>> i(0.2477).to_string()
'lch(52% 58.1 80.761)'
```

It is important to note that the you must specify the channels of the space the interpolation is occurring in.
Specifying `hue` while interpolating in the sRGB color space would target no channels and would be ignored.

You can also do non-linear interpolation by providing a function. Here we use a function that returns `p ** 3` creating
the colors: `#!color lch(50.04% 49.997 0.0196 / 1)`, `#!color lch(50.32% 49.976 0.15685 / 1)`, and
`#!color lch(51.08% 49.921 0.52995 / 1)`.

```pycon3
>>> i = Color("lch(50% 50 0)").interpolate("lch(90% 50 20)", progress=lambda p: p ** 3)
>>> i(0.1)
color(lch 50.04 49.997 0.0196 / 1)
>>> i(0.2)
color(lch 50.32 49.976 0.15685 / 1)
>>> i(0.3)
color(lch 51.08 49.921 0.52995 / 1)
```

## Color Mixing

Colors can be mixed together to create new colors. Mixing is built on top of the [`interpolation`](#interpolating)
function and will return a color between the current and specified colors. If a colors are requested to be interpolated
within a color space smaller than the original, the colors will be gamut mapped into the desired color space.

As an example, if we had the color `#!color red` and the color
`#!color blue`, and we wanted to mix them, we can just call the `mix` method, and we'll get the color
`#!color rgb(127.5 0 127.5)`.

```pycon3
>>> red = Color("red")
>>> blue = Color("blue")
>>> red.mix(blue).to_string()
'rgb(127.5 0 127.5)'
```

The `mix` method will mix the two colors in the color space of the color calling the method. If one desired to mix in a
different color space, the `space` parameter would just need to be set to the desired color space. Notice that this
creates a different color: `#!color rgb(180.38 44.003 76.616)`. The results of mixing in a
different color space may be more desirable as color mixing may be more natural.

```pycon3
>>> red = Color("red")
>>> blue = Color("blue")
>>> red.mix(blue, space="lab").to_string()
'rgb(180.38 44.003 76.616)'
```

By default, colors are mixed at 50%, but can control the percentage at which the color is mixed. Here we mix the color
blue into red at 20%. This gives us the color of `#!color rgb(204 0 51)`.

```pycon3
>>> red = Color("red")
>>> blue = Color("blue")
>>> red.mix(blue, 0.2).to_string()
'rgb(204 0 51)'
```

Mix can also accept a string and will create the color for you which is great if you don't need to work with the
second color afterwards.

```pycon3
>>> Color("red").mix("blue", 0.2).to_string()
'rgb(204 0 51)'
```

Mixing will always return a new color unless `in_place` is set `True`.

## Overlaying Colors

The `overlay` method allows a transparent color to be overlaid on top of another color creating the composite of the
two. To perform an overlay, a background color must be provided to the color along with an optional color space. If a
color is to be overlaid within a smaller color space, the colors will be mapped to the smaller space.

In the example below, we take the `#!color rgb(100% 0% 0% / 0.5)` and overlay it on the color `#!color black`. This
yields the color: `#!color rgb(127.5 0 0)`.

```pycon3
>>> color = Color("rgb(100% 0% 0% / 0.5)")
>>> color.overlay("black").to_string()
'rgb(127.5 0 0)'
```

A new color will be returned instead of modifying the current color unless `in_place` is set `True`.

## Color Distance

ColorAide implements a couple different distance algorithms.

- `euclidean`: basic Euclidean distancing. By default it is performed in the Lab color space matching Delta E 1976,
  but can be configured to work directly in any color space via the `space` parameter.
- `de-76`: the Delta E 1976 algorithm which is euclidean distance in the `lab` color space.
- `de-94`: the Delta E 1994 algorithm which was created as a correction to Delta E 76 as the Lab color space was not as
  uniform as originally thought. By default, it uses a weighting for "graphic arts" where `kl=1`, `k1=0.045`, and
  `k2=0.015`.
- `de-cmc`: the Delta E CMC algorithm which is more accurate than the 1976 algorithm. It is performed in the Lab color
   space. It's weighting can be tweaked with `l` and `c` parameter. Current default is `2:1` where `l=2` and `c=1`.
- `de-2000`: the Delta E 2000 algorithm is an even more "correct" algorithm performed in the Lab color space. weighting
  is controlled by `kl`, `kc`, and `kh` which is `1:1:1` by default where `kl=1`, `kc=1`, and `kh=1`.

To use the `distance` method, we simply provide a color object or color string, the optional `method` (or algorithm) to
use to calculate the difference, and optional algorithm specific parameters.

Here we calculate the distance between `#!color pink` and `#!color purple` using the default algorithm which is
`euclidean` in the Lab color space and is equivalent to `de-76`.

```pycon3
>>> pink = Color("pink")
>>> purple = Color("purple")
>>> pink.distance(purple)
74.39016675581851
```

If we like, we could evaluate the euclidean distance in the sRGB color space:

```pycon3
>>> pink.distance(purple, space="srgb")
0.9494570374154544
```

Or evaluate the color using a different algorithm altogether:

```pycon3
>>> pink.distance(purple, "de-2000")
53.74936462933638
```

## Gamut

A given color may not always be in gamut, or may not be in the gamut of another color space that we'd like it to be in.

For instance, we may have a color `#!color rgb(30% 105% 0%)` which is not in it's own gamut. We can
check this via the `in_gamut` method.

```pycon3
>>> Color("rgb(30% 105% 0%)").in_gamut()
False
```

If desired we can force the color in gamut via the `fit` method. By doing this, we'll get the color
`#!color rgb(138 255 98.203)` which is in gamut.

```pycon3
>>> Color("rgb(30% 105% 0%)").fit().to_string(fit=False)
'rgb(138 255 98.203)'
```

!!! tip "Tip"
    By default, the `to_string` method will fit a color into gamut. If this is not desired, the `fit` parameter can be
    set to `False`.

    ```pycon3
    >>> Color("rgb(30% 105% 0%)").to_string()
    'rgb(138 255 98.203)'
    >>> Color("rgb(30% 105% 0%)").to_string(fit=False)
    'rgb(76.5 267.75 0)'
    ```

Gamut fitting can be done in two ways in ColorAide

1. `lch-chroma`: This is the default implemented as described [here][lch-chroma].
2. `clip`: Simply clips the colors until they are in gamut.

If we wanted to use a different "fitting" method, we can simply set `fit` to the desired fit type. Notice when we use
the clipping on the previous example, the color that we get is a bit different. This time, instead of
`#!color rgb(138 255 98.203)`, we get `#!color rgb(76.5 255 0)`.

```pycon3
>>> Color("rgb(30% 105% 0%)").fit(method="clip").to_string(fit=False)
'rgb(76.5 255 0)'
```

Gamut fitting will always return a new color unless `in_place` is set `True`.

## Convert to Strings

Colors can be output back into strings by using the `to_string` method. The CSS color class will convert any of the
supported color classes into CSS strings of various formats.

```pycon3
>>> color = Color("srgb", [0.5, 0, 1], 0.3)
>>> color.to_string()
'rgb(127.5 0 255 / 0.3)'
```

If we want commas, we can force the comma syntax:

```pycon3
>>> color.to_string(comma=True)
'rgba(127.5, 0, 255, 0.3)'
```

In general, a color in a given color space may share a number of the same options as other color spaces, but a given
color space may also have options unique to itself. For instance, sRGB can output colors to a hex format which is unique
compared to HSL and others.

```pycon3
>>> color.to_string(hex=True)
'#8000ff4d'
```

!!! tip "Precision"
    By default, ColorAide works with full precision internally to reduce the chances of colors not round tripping
    through the conversion process properly. When outputting a string, the default precision (actually adjusts precision
    and scale) is 5. Notice that in the case below, `#!color blue`, when converted to the Lch color space and
    output to a string, we can see if we read that color back in and check its gamut, that it shows the color is "out of
    gamut". But if we do the same thing with a greater precision (6), we reads as in gamut.

    - Precision 5: `#!color lch(29.568% 131.21 301.37)`
    - Precision 6: `#!color lch(29.5676% 131.207 301.369)`

    ```pycon3
    >>> string = Color('blue').convert("Lch").to_string()
    >>> Color(string).in_gamut("srgb")
    False
    >>> string = Color('blue').convert("Lch").to_string(precision=6)
    >>> Color(string).in_gamut("srgb")
    True
    ```

--8<--
refs.txt
--8<--
