# Color Harmonies

In color theory, color harmony refers to the property that certain aesthetically pleasing color combinations have.
Modern day color theory probably starts with the first color wheel created by Isaac Newton. Based on his observations of
light with prisms, he formed one the first color wheels. From there, many others built upon this work, sometimes with
opposing ideas.

The original color wheel, while inspired by what was observed by light, was created based on experiments with pigments
as well. As most know, in paint, red, yellow, and blue are considered primary colors. Newton thought this translated to
light as well and stated they were also the primary colors of light. While this isn't actually true, his work was very
important in reshaping how people viewed color.

Over time, the color wheel was refined. The traditional model, which we will call an RYB color model, defined 12 colors
that made up the wheel: the primary colors, the secondary colors, and the tertiary colors. The secondary colors are
created by evenly mixing the primary colors, and the tertiary colors are created by evenly mixing those primary colors
with the secondary colors.

```py play wheel
Color('ryb', [1, 0, 0]).harmony('wheel', space='ryb')
```

The idea of color harmonies originates from the idea that colors, based on their relative position on the wheel, can
form more pleasing color combinations.

## Which Color Space is Best for Color Harmonies?

As we know, these days, there are many color spaces out there: subtractive models, additive models, perceptually
uniform models, high dynamic range models, etc. Many color spaces trying to solve specific issues based on the knowledge
at the time.

It should be noted, that the idea of primary colors stems from the idea that there are a set of pure colors from which
all colors can be made from. If you've spent any time with paint, you will know that not all colors can be made from
red, yellow, and blue. There are colors like `#!color cyan` and `#!color magenta` that cannot be made with the
traditional primary colors. The early work that helped create the first color wheels was done with the limited paints
that was available at the time, and the color harmony concepts were built upon the early RYB color model.

In modern TVs and monitors, the RYB color model is not used. Paint has subtractive properties, but light has additive
properties. Electronic screens create all their colors with light based methods that mix red, green, and blue lights. In
addition, the human eye perceives colors using red, green, and blue light as well. This is As far as light is concerned,
the primary colors are red, green, and blue.

In reality, we could create a color wheel from any of the various color spaces out there and end up with different
results. If we were to compose a color wheel based on the common sRGB color space, we could base it off the 3 primary
colors of light. Starting with red (0˚), we could extract the colors at evenly spaced degrees, 30˚ to be exact. This
would give us our 12 colors for the sRGB color space.

```py play
Steps([Color('hsl', [x, 1, 0.5]) for x in range(0, 360, 30)])
```

From this we can construct an sRGB color wheel.

```py play wheel
Color('red').harmony('wheel', space='srgb')
```

This is different from the RYB color wheel we showed earlier, and more accurate in relation to how light works, but does
it yield better harmonies for colors?

The sRGB color space is additive, just like light, but pigments are subtractive. We can use CMY to generate a
subtractive wheel with a far greater range that red, green blue creates by use magenta, yellow, and cyan. But does this
create better harmonies?

```py play
Steps(Color('magenta').harmony('wheel', space='cmy'))
```

```py play wheel
Color('magenta').harmony('wheel', space='cmy')
```

If we were to select the perceptually uniform OkLCh color space, and seed it with red's lightness and chroma, we'd get
the wheel below.

```py play
Steps(Color('red').harmony('wheel', space='oklch'))
```

```py play wheel
Color('red').harmony('wheel', space='oklch')
```

This produces colors with visually more uniform lightness, does that mean these are better?

The truth is, what is better or even harmonious can be largely subjective, and everyone has reasons for selecting
certain color spaces for a specific task.

Many artists swear by the limited, classical color wheel, others are fine with using the RGB color wheel as it is easy
to work with in CSS via the HSL color space, and there are still others that are more interested in perceptually uniform
color spaces that aim for more consistent hues and predictable lightness.

As far as ColorAide is concerned, we've chosen to use OkLCh as the color space in which we work in. This is based
mainly on the fact that it keeps hue more consistent than some other options, and it allows us to support a wider gamut
than options like HSL.

```py play
Steps(Color.steps(['black', 'blue', 'white'], steps=11, space='oklch'))
Steps(Color.steps(['black', 'blue', 'white'], steps=11, space='hsl'))
Steps(Color.steps(['black', 'blue', 'white'], steps=11, space='lch'))
```

While OkLCh is the default, we understand that there are many reasons to use other spaces, so use what you like, we
won't judge :smile:. If you are a color theory purist, you can use the classical RYB model.

```py play
Steps(Color('red').harmony('complement'))
Steps(Color('ryb', [1, 0, 0]).harmony('complement', space='ryb'))
```

/// tip | RYB Model
The RYB model has a more limited color gamut than sRGB as the red, yellow and blue primaries cannot make all colors.
Additionally, the red, yellow, and blue primaries are not the same as the ones in sRGB, so when using RYB to generate
harmonies, make sure you are working directly within RYB to ensure you are not out of gamut.
///

/// tip
`harmony()` can output the results in any color space you need by setting `out_space`.

```py play
Steps(Color('red').harmony('complement', out_space='srgb'))
```
///


## Supported Harmonies

ColorAide currently supports 7 theorized color harmonies: [monochromatic](#monochromatic),
[complementary](#complementary), [split complementary](#split-complementary), [analogous](#analogous),
[triadic](#triadic), [square](#tetradic-square), and [rectangular](#tetradic-rectangular). By default, all color
harmonies are calculated with the perceptually uniform OkLCh color space, but other color spaces can be used if desired.

![OkLCh Color Wheel](images/oklch-color-wheel.png)

### Monochromatic

The monochromatic harmony pairs various tints and shades of a color together to create pleasing color schemes.

![Harmony Monochromatic](images/harmony-mono.png)

```py play
Steps(Color('red').harmony('mono'))
```

/// note | Achromatic Colors
Pure `#!color white` and `#!color black` will not be included in a monochromatic color harmony unless the color is
achromatic.
///

### Complementary

Complementary harmonies use a dyad of colors at opposite ends of the color wheel.

![Harmony Complementary](images/harmony-complement.png)

```py play
Steps(Color('red').harmony('complement'))
```

### Split Complementary

Split Complementary is similar to complementary, but actually uses a triad of colors. Instead of just choosing one
complement, it splits and chooses two colors on the opposite side that are close, but not adjacent.

![Harmony Split Complementary](images/harmony-split-complement.png)

```py play
Steps(Color('red').harmony('split'))
```

### Analogous

Analogous harmonies consists of 3 adjacent colors.

![Harmony Analogous](images/harmony-analogous.png)

```py play
Steps(Color('red').harmony('analogous'))
```

### Triadic

Triadic draws an equilateral triangle between 3 colors on the color wheel. For instance, the primary colors have triadic
harmony.

![Harmony Triadic](images/harmony-triadic.png)

```py play
Steps(Color('red').harmony('triad'))
```

### Tetradic Square

Tetradic color harmonies refer to a group of four colors. One tetradic color harmony can be found by drawing a square
between four colors on the color wheel.

![Harmony Tetradic](images/harmony-tetradic.png)

```py play
Steps(Color('red').harmony('square'))
```

### Tetradic Rectangular

The rectangular tetradic harmony is very similar to the square tetradic harmony except that it draws a rectangle between
four colors instead of a square.

![Harmony Tetradic Rectangular](images/harmony-tetradic-rect.png)

```py play
Steps(Color('red').harmony('rectangle'))
```

### Others

If you have a particular configuration that you are after that is not covered under the defaults, you can use `harmony`
to calculate your own. Simply use the `wheel` harmony that can generate a color wheel of any size. Simply use a color to
seed the wheel, specify the space in which to generate the wheel. Optionally, provide the desired number of colors in
the color wheel via the `count` argument. We can generate a wheel for any color (assuming the color space can properly
handle the color). We can even generate an extended color wheel if so desired.

```py play wheel
Color('ryb', [1, 0, 0]).harmony('wheel', space='ryb', count=48)
```

```py play
Steps(Color('ryb', [1, 0, 0]).harmony('wheel', space='ryb', count=48))
```

## Changing the Default Harmony Color Space

/// new | New 2.7
Non-cylindrical space support was added in 2.7.
///

If you'd like to change the `#!py3 Color()` class's default harmony color space, it can be done with
[class override](./color.md#override-default-settings). Simply derive a new `#!py3 Color()` class from the original and
override the `HARMONY` property with the name of a suitable color space. Color spaces must be either a cylindrical
space, a Lab-like color space, or what we will call a regular, rectangular space. By "regular" we mean a normal 3
channel color space _usually_ with a range of [0, 1]. Afterwards, all color harmony calculations will use the specified
color space unless overridden via the method's `space` parameter.

```py play
class Custom(Color):
    HARMONY = 'hsl'

Steps(Custom('red').harmony('split'))
```

/// warning
Remember that every color space is different. Some may rotate hues in a different direction and some may just not be
very compatible for extracting harmonies from.

Additionally, a color space may not handle colors beyond its gamut well, for such color spaces, it is important to work
within that spaces gamut opposed to picking colors outside of the gamut and relying on gamut mapping.
///
