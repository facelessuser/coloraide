# Gamut Mapping

Many color spaces are designed in such a way that they can only represent colors accurately within a specific range.
This range in which a color can accurately be represented is known as the color gamut. While some color spaces are
theoretically unbounded, there are many that are designed with distinct ranges.

The sRGB and Display P3 color spaces are both RGB color spaces, but they actually can represent a different amount of
colors. Display P3 has a wider gamut and allows for greener greens and redder reds, etc. In the image below, we show
four different RGB color spaces, each with varying different gamut sizes. Display P3 contains all the colors in sRGB
and extends it even further. Rec. 2020, another RGB color space, is even wider. ProPhoto is so wide that it contains
colors that the human eye can't even see.

![Gamut Comparison](images/gamut-compare.png)

In order to visually represent a color from a wider gamut color space, such as Display P3, in a more narrow color space,
such as sRGB, a suitable color within the more narrow color space must must be selected and be shown in its place. This
selecting of a suitable replacement is called gamut mapping.

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

On the other hand, some color spaces do not have a limit. CIELab is one such color space. Sometimes limits will be
placed on the color space channels for practicality, but theoretically, there are no bounds. When we check a CIELab
color, we will find that it is always considered in gamut.

```playground
Color("lab(200% -20 40 / 1)").in_gamut()
```

While checking CIELab's own gamut isn't very useful, we can test it against a different color space's gamut. By simply
passing in the name of a different color space, the current color will be converted to the provided space and then
will run `in_gamut` on the new color. You could do this manually, but using `in_gamut` in this manner can be very
convenient. In the example below, we can see that the CIELab color of `#!color lab(200% -20 40 / 1)` is outside the
narrow gamut of sRGB.

```playground
Color("lab(200% -20 40 / 1)").in_gamut('srgb')
```

### Tolerance

Generally, ColorAide does not round off values in order to guarantee the best possible values for round tripping, but
due to [limitations of floating-point arithmetic][floating-point] and precision of conversion algorithms, there can be
edge cases where colors don't round trip perfectly. By default, `in_gamut` allows for a tolerance of `#!py3 0.000075` to
account for such cases where a color is "close enough". If desired, this "tolerance" can be adjusted.

Let's consider CIELab with a D65 white point. The sRGB round trip through CIELab D65 for `#!color white` does not
perfectly convert back to the original color. This is due to the perils of floating point arithmetic.

```playground
Color('color(srgb 1 1 1)').convert('lab-d65')[:]
Color('color(srgb 1 1 1)').convert('lab-d65').convert('srgb')[:]
```

We can see that when using a tolerance of zero, and gamut checking in sRGB, that the color is considered out of gamut.
This makes sense as the round trip through CIELab D65 and back is so very close, but ever so slightly off. Depending on
what you are doing, this may not be an issue up until you are ready to finalize the color, so sometimes it may be
desirable to have some tolerance, and other times not.

```playground
Color('color(srgb 1 1 1)').convert('lab-d65').convert('srgb')[:]
Color('color(srgb 1 1 1)').convert('lab-d65').convert('srgb').in_gamut()
Color('color(srgb 1 1 1)').convert('lab-d65').convert('srgb').in_gamut(tolerance=0)
```

On the topic of tolerance, lets consider some color models that do not handle out of gamut colors very well. There are
some color models that are alternate representations of an existing color space. For instance, the cylindrical spaces
HSL, HSV, and HWB are just different color models for the sRGB color space. They are are essentially the sRGB color
space, just with cylindrical coordinates that isolate certain attributes of the color space: saturation, whiteness,
blackness, etc. So their gamut is exactly the same as the sRGB space, because they are the sRGB color space. So it
stands to reason that simply using the sRGB gamut check for them should be sufficient, and if we are using strict
tolerance, this would be true.

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

HSL has a very tight conversion to and from sRGB, so when an sRGB color is precisely in gamut, it will remain in gamut
throughout the conversion to and from HSL, both forwards and backwards. On the other hand, there may be color models
that have a looser conversion algorithm. There may be cases where it may be beneficial to increase the threshold.

## Mapping Colors

Gamut mapping is the process of taking a color that is out of gamut and adjusting it such that it fits within the gamut.
There are various ways to map an out of bound color to an in bound color, each with their own pros and cons. ColorAide
offers two methods related to gamut mapping: `#!py3 clip()` and `#!py3 fit()`. `#!py3 clip()` is a dedicated function
that performs the speedy, yet naive, approach of simply truncating a color channel's value to fit within the specified
gamut, and `#!py3 fit()` is a method that allows you to do more advanced gamut mapping approaches that, while slower,
generally yield better results.

While clipping won't always yield the best results, clipping is still very important and can be used to trim channel
noise after certain mathematical operations or even used in other gamut mapping algorithms if used carefully. For this
reason, clip has its own dedicated method for quick access: `#!py3 clip()`. It can be applied directly to the current
color space or can be applied on the gamuts of other color spaces.

```playground
Color('rgb(270 30 120)').clip()
Color('color(display-p3 1 1 0)').clip('srgb')
```

The `#!py3 fit()` method, is the generic gamut mapping method that exposes access to all the different gamut mapping
methods available. By default, `#!py3 fit()` uses a more advanced method of color mapping that tries to preserve hue and
lightness, hue being the attribute the human eye is most sensitive to. If desired, a user can also specify any currently
registered gamut mapping algorithm via the `method` parameter.

```playground
Color('rgb(270 30 120)').fit()
Color('rgb(270 30 120)').fit(method='clip')
```

Gamut mapping can also be used to fit colors in other gamuts, just like `#!py3 clip()`. For instance, fitting a Display
P3 color into an sRGB gamut.

```playground
c1 = Color('color(display-p3 1 1 0)')
c1.in_gamut('srgb')
c1.fit('srgb')
c1.in_gamut()
```

!!! warning "Caveats when Mapping in Other Spaces"
    When fitting in another color space, results may vary depending on what color space you are in and what color space
    you are using to fit the color. We went into great depths when discussing [gamut checking](#gamut-checking) about
    how transform functions from one color space to another are not always exact. We also gave quite a number of
    examples showing cases in which some color spaces were more sensitive to slight deviations outside their gamut than
    others. This is mainly mentioned as fitting in one color space and round tripping back may not give exact results:

    ```playground
    Color("color(--lch-d65 100 50 75)").convert('srgb').fit()[:]
    Color("color(--lch-d65 100 50 75)").fit('srgb').convert('srgb')[:]
    ```

    While the above case does fit the LCh color within the sRGB color space, and once converted back to LCh, it is
    technically well within the "in gamut" threshold, the conversion can't quite keep it precisely in gamut. Depending
    on what you are doing and what spaces you are working in, this may be okay, but it may also make sense to fully
    convert to color space with the gamut you wish to work in and work directly in that space opposed to the indirect
    fitting of a color in a different color space.

There are actually many different ways to gamut map a color. Some are computationally expensive, some are quite simple,
and many do really good in some cases and not so well in others. There is probably no perfect gamut mapping method, but
some are better than others. ColorAide currently only offers a couple simple methods to gamut map.

Method         | Description
-------------- | -----------
`clip`         | Simple, naive clipping.
`lch-chroma`   | Uses a combination of chroma reduction and MINDE in the CIELCh color space to bring a color into gamut. This is the default method used.
`oklch-chroma` | Like `lch-chroma`, but uses the OkLCh color space instead. This is currently what the [CSS Color Level 4 specification](https://drafts.csswg.org/css-color/#binsearch) recommends.

!!! note "CSS Level 4 Gamut Mapping"
    The CSS [CSS Color Level 4 specification](https://drafts.csswg.org/css-color/#binsearch) currently recommends using
    OkLCh as the gamut mapping color space. `oklch-chroma` is our implementation of the CSS Level 4 color specification.

    OkLCh is a very new color space to be used in the field of gamut mapping. While CIELCh is not perfect, its weakness
    are known. OkLCh does seem to have certain quirks of its own, and may have more that have yet to be discovered.
    While we have not made `oklch-chroma` our default yet, we have exposed the algorithm so users can begin exploring
    it.

### Why Not Just Clip?

In the past, clipping has been the default way in which out of gamut colors have been handled in web browsers. It is
fast, and has generally been fine as most browsers have been constrained to using sRGB. But as modern browsers begin to
adopt more wide gamut monitors such as Display P3, and CSS grows to support an assortment of wide and ultra wide color
spaces, representing the best intent of an out of gamut color becomes even more important.

ColorAide currently uses a default gamut mapping algorithm that performs gamut mapping in the CIELCh color space using
chroma reduction coupled with minimum ∆E (MINDE). This approach is meant to preserve enough of the important attributes
of the out of gamut color as is possible, mostly preserving both lightness and hue, hue being the attribute that people
are most sensitive to. MINDE is used to abandon chroma reduction and clip the color when the color is very close to
being in gamut. MINDE also allows us to catch cases where the geometry of the color space's gamut is such that we may
slip by higher chroma options resulting in undesirable, aggressive chroma reduction. While CIELCh is not a perfect
color space, and we may use a different color space in the future, this method is generally more accurate that using
clipping alone.

Below we have an example of using chroma reduction with MINDE. It can be noted that chroma is reduced until we are very
close to being in gamut. The MINDE helps us catch the peak of the yellow shape as, otherwise, we would have continued
reducing chroma until we were at a very chroma reduced, pale yellow.

![Gamut LCh Chroma - yellow](images/gamut-lch-chroma-yellow.png)

One might see some cases of clipping and think it does a fine job and question why any of this complexity is necessary.
In order to demonstrate the differences in gamut mapping vs clipping, see the example below. We start with the color
`#!color color(display-p3 1 1 0)` and interpolate with it in the CIELCh color space reducing just the lightness. This
will leave both chroma and hue intact. The Interactive playground below automatically gamut maps the color previews to
sRGB, but we'll control the method being used by providing two different `#!py Color` objects: one that uses
`lch-chroma` (the default) for gamut mapping, and one that uses `clip`. Notice how clipping, the bottom color set, clips
these dark colors and makes them reddish. This is a very undesirable outcome.

```playground
# Gamut mapping in LCh
yellow = Color('color(display-p3 1 1 0)')
lightness_mask = Color('lch(0% none none)')
HtmlRow([c.fit() for c in Color.steps([yellow, lightness_mask], steps=10, space='lch')])

# Clipping
yellow = Color('color(display-p3 1 1 0)')
lightness_mask = Color('lch(0% none none)')
HtmlRow([c.clip() for c in Color.steps([yellow, lightness_mask], steps=10, space='lch')])
```

There are times when clipping is simply preferred. It is fast, and if you are just trimming noise off channels, it is
very useful, but if the idea is to present an in gamut color that tries to preserve as much of the intent of the
original color as possible, other methods may be desired. There are no doubt better gamut methods available than what
ColorAide offers currently, and more may be added in the future, but ColorAide can also be extended using 3rd party
plugins as well.
