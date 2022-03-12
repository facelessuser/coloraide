# Gamut Mapping

Many color spaces are designed in such a way that they can only represent colors accurately within a specific range.
This range in which a color can accurately be represented is known as the color gamut. Some color spaces are
theoretically unbounded, but past a point, the eye can't see them anyways.

The sRGB color space as well defined bounds for its gamuts while CIELAB is a color space that has no real defined gamut.
When translating a color from such a large, unbounded color space as CIELAB to a small color space like sRGB, there are
many colors that simply cannot be represented within the smaller sRGB color space. In order to visually represent a
color outside of the gamut, a suitable color within the gamut must be selected to be shown in its place. This selecting
of a suitable replacement is called gamut mapping.

ColorAide defines a couple methods to help identify when a color is outside the gamut bounds of a color space and to
help find a suitable, alternative color that is within the gamut.

## Checking Gamut

When dealing with colors, it can be important to know whether a color is within its own gamut. The `in_gamut` function
allows for comparing the current color's specified values against the color space's gamut.

Let's assume we have a color `#!color rgb(30% 105% 0%)`. The color is out of gamut due to the green channel exceeding
the channel's limit of `#!py3 100%`. When we execute `in_gamut`, we can see that the color is not in its own gamut.

```playground
Color("rgb(30% 105% 0%)").in_gamut()
```

On the other hand, some color spaces do not have a limit. CIELAB is one such color space. Sometimes limits will be
placed on the color space channels for practicality, but theoretically, there are no bounds. When we check a CIELAB
color, we will find that it is always considered in gamut.

```playground
Color("lab(200% -20 40 / 1)").in_gamut()
```

While checking CIELAB's own gamut isn't very useful, we can test it against a different color space's gamut. By simply
passing in the name of a different color space, the current color will be converted to the provided space and then
will run `in_gamut` on the new color. You could do this manually, but using `in_gamut` in this manner can be very
convenient. In the example below, we can see that the CIELAB color of `#!color lab(200% -20 40 / 1)` is outside the
narrow gamut of sRGB.

```playground
Color("lab(200% -20 40 / 1)").in_gamut('srgb')
```

### Tolerance

Generally, ColorAide does not round off values in order to guarantee the best possible values for round tripping, but
due to [limitations of floating-point arithmetic][floating-point] and precision of conversion algorithms, there can be
edge cases where colors don't round trip perfectly. By default, `in_gamut` allows for a tolerance of `#!py3 0.000075` to
account for such cases where a color is "close enough". If desired, this "tolerance" can be adjusted.

Let's consider CIELAB. The sRGB round trip through CIELAB for `#!color white` does not perfectly convert back to the
original color. We can see that when using a tolerance of zero, the color is considered out of gamut. Depending on what
you are doing, this may not be an issue up until you are ready to finalize the color, so sometimes it may be desirable
to have some tolerance, and other times not.

```playground
Color('color(srgb 1 1 1)').convert('lab').convert('srgb').coords()
Color('color(srgb 1 1 1)').convert('lab').convert('srgb').in_gamut()
Color('color(srgb 1 1 1)').convert('lab').convert('srgb').in_gamut(tolerance=0)
```

On the topic of tolerance, there are some color models that are alternate representations of an existing color space.
For instance, the cylindrical spaces HSL, HSV, and HWB are just different color models for the sRGB color space. They
are are essentially the sRGB color space, just with cylindrical coordinates that isolate certain attributes of the
color space: saturation, whiteness, blackness, etc. So their gamut is exactly the same as the sRGB space, because they
are the sRGB color space. So it stands to reason that simply using the sRGB gamut check for them should be sufficient,
and if we are using strict tolerance, this would be true.

```playground
Color('rgb(255 255 255)').in_gamut('srgb', tolerance=0)
Color('hsl(0 0% 100%)').in_gamut('srgb', tolerance=0)
Color('color(--hsv 0 0% 100%)').in_gamut('srgb', tolerance=0)
Color('rgb(255.05 255 255)').in_gamut('srgb', tolerance=0)
Color('hsl(0 0% 100.05%)').in_gamut('srgb', tolerance=0)
Color('color(--hsv 0 0% 100.05%)').in_gamut('srgb', tolerance=0)
```

But when we are not using a strict threshold, and we check one of these models **only** using the sRGB gamut, there are
some cases where these cylindrical colors can exhibit coordinates wildly outside of the model's range but still very
close to the sRGB gamut.

In this example, we have an sRGB color that is extremely close to being in gamut, but when we convert it to HSL,
we can see wildly large saturation.

```playground
hsl = Color('color(srgb 0.9999999999994 1.0000000000002 0.9999999999997)').convert('hsl')
hsl.to_string(fit=False)
hsl.in_gamut('srgb')
```

This happens because these cylindrical color models do not represent colors out of gamut in a very sane way. They are
simply not designed to extend past the color gamut. So even a slightly out of gamut sRGB color can translate to a value
way outside the cylindrical color model's boundaries.

For this reason, gamut checks in the HSL, HSV, or HWB models apply tolerance checks on the color's coordinates in the
sRGB color space **and** the respective cylindrical model ensuring we have coordinates that are close to the color's
actual gamut and reasonably close to the cylindrical model's constraints as well.

So, when using HSL as the gamut check, we can see that it ensures the color is not only very close to the sRGB gamut,
but that it is also very close the color model's constraints.

```playground
hsl = Color('color(srgb 0.9999999999994 1.0000000000002 0.9999999999997)').convert('hsl')
hsl
hsl.in_gamut('hsl')
```

If the Cartesian check is the only desired check, and the strange cylindrical values that are returned are not a
problem, `srgb` can always be specified. `#!py3 tolerance=0` can also be used to constrain the check to values exactly
in the gamut.

When a color is precisely in gamut, HSL has a very tight conversion to and from sRGB. A color that is gamut, will remain
in gamut throughout the conversion, forwards and backwards. Okhsl and Okhsv, on the other hand, are color models have
a looser conversion algorithm. While the constrains mimic the traditional HSL and HSV boundaries, the edges of those
boundaries do not always convert precisely back into the sRGB gamut.

Okhsl and Okhsv are color models that more approximate the sRGB gamut, and seem to expect some clipping and/or rounding
when going back to sRGB. Adjusting the tolerance for these color models may be sufficient until you are ready to
finalize the color by clipping the color to remove the noise.

```playground
okhsv = Color('color(--okhsv 20 100% 75% / 1)')
okhsv.in_gamut()
okhsv.convert('srgb')
okhsv.in_gamut(tolerance=0.0005)
```

## Mapping Colors

Gamut mapping is the process of taking a color that is out of gamut and adjusting it such that it fits within the gamut.
While there are various different ways to gamut map a color into a smaller gamut, ColorAide currently only offers a
couple.

Method         | Description
-------------- | -----------
`clip`         | Simple, naive clipping.
`lch-chroma`   | Uses a combination of chroma reduction and MINDE in the CIELCH color space to bring a color into gamut. This is the default method used.
`oklch-chroma` | Like `lch-chroma`, but uses the Oklch color space instead. Currently experimental and is meant to be similar to `css-color-4`, but provides better results at the cost of being a little slower.
`css-color-4`  | This is the algorithm as currently specified by the [CSS Color Level 4 specification](https://drafts.csswg.org/css-color/#binsearch). It is like `oklch-chroma`, but it is faster at the cost of providing slightly inferior results.

!!! note "CSS Level 4 Gamut Mapping"
    `css-color-4` matches the CSS algorithm as described in the [CSS Color Level 4 specification](https://drafts.csswg.org/css-color/#binsearch).
    `oklch-chroma` is an improved version of `css-color-4`, and while not as fast as `css-color-4`, provides better
    results. This is most evident when generating gradients as they are more smooth when using `oklch-chroma`. While
    maybe some eyes may struggle to see the difference, some may notice some color banding.

    ```playground
    class ColorCss(Color):
        FIT = 'css-color-4'
    class ColorOk(Color):
        FIT = 'oklch-chroma'

    ColorCss("lch(85% 80 310)").interpolate("lch(85% 100 85)", space='oklch')
    ColorOk("lch(85% 80 310)").interpolate("lch(85% 100 85)", space='oklch')
    ```

Gamut mapping occurs automatically any time a color is serialized to a string via `#!py3 to_string()` and in a few other
specific cases, like interpolating in a color space that cannot represent out of gamut colors. With this said, gamut
mapping can also be performed on-demand.

To gamut map a color we can call `#!py3 fit()`. We calling it, it will fit the current color in the current color space,
but if we send in a color space, it will fit the given color in a whatever color space is specified.

```playground
c1 = Color('color(display-p3 1 1 0)')
c1.in_gamut('srgb')
c1.fit('srgb', in_place=True)
c1.in_gamut()
```

We can use also specify a specific gamut mapping method, such as `clip`, `oklch-chroma`, etc.

```playground
c1 = Color('color(display-p3 1 1 0)')
c1.in_gamut('srgb')
c1.fit('srgb', method='clip', in_place=True)
c1.in_gamut()
```

Clip is always available as a dedicated function called `#!py3 clip()` as well.

```playground
c1 = Color('color(display-p3 1 1 0)')
c1.in_gamut('srgb')
c1.clip('srgb', in_place=True)
c1.in_gamut()
```

Keep in mind that clipping has its uses, but generally, clipping can create some odd cases when being used as a gamut
mapping method. It should be prefaced that clipping is currently how web browsers handle out of gamut colors. It is
very quick and easy to do, but just because it is quick, it doesn't mean it is the best way to go.

In order to demonstrate gamut mapping vs clipping, in this example, we will take the color
`#!color color(display-p3 1 1 0)`. We will interpolate with it in the CIELCH color space reducing just the lightness.
This will leave both chroma and hue intact. The Interactive playground below will gamut map everything to sRGB, but
we'll use two different `#!py Color` objects: one that uses `lch-chroma` (the default) for gamut mapping, and one that
uses `clip`. Notice how clipping, the bottom color set, clips these dark colors and makes them reddish.

```playground
class ColorClip(Color):
    FIT = 'clip'

# Gamut mapping in Lch
yellow = Color('color(display-p3 1 1 0)')
lightness_mask = Color('lch(0% none none)')
yellow.steps(lightness_mask, steps=10, space='lch')

# Force a new row for next example
ColorRow()

# Clipping
yellow = ColorClip('color(display-p3 1 1 0)')
lightness_mask = Color('lch(0% none none)')
yellow.steps(lightness_mask, steps=10, space='lch')
```

When fitting in another color space, results may vary depending on what color space you are in and what color space you
are using to fit the color. We went into great depths when discussing [gamut checking](#gamut-checking) and about how
transform functions from one color space to another are not always exact. We also gave quite a number of examples
showing cases in which some color spaces were more sensitive to slight deviations from their gamut than others. This is
mainly mentioned as fitting in one color space and round tripping back may not give exact results:

```playground
Color("lch(100% 50 75)").convert('srgb').fit().coords()
Color("lch(100% 50 75)").fit('srgb').convert('srgb').coords()
```

Depending on what you are doing, and what spaces you are working in, it may make sense to fully convert to a space and
work directly in that space opposed to the indirect fitting of a color in a different color space.
