## Convert to Strings

Colors can be translated to strings by using the `to_string` method. The CSS color class will convert the current color
into one of many of the color's CSS formats.

```pycon3
>>> color = Color("srgb", [0.5, 0, 1], 0.3)
>>> color.to_string()
'rgb(127.5 0 255 / 0.3)'
```

All color spaces support the following parameters:

- `alpha`: set to `None` by default, alpha will only be shown if less than 100%, but if set to `True`, alpha will always
  be shown. Setting to `False` will cause alpha to be ignored in the output.
- `precision`: precision controls the precision of the output values. The name is a little misleading as it will
  actually adjust the precision and scale of the values. The default is 5. In some cases, like sRGB hex output,
  precision may not really come into play as hex values are rounded to the nearest whole number anyways.

    ```pycon3
    >>> Color("rgb(30% 75% 100%)").to_string(precision=5)
    'rgb(76.5 191.25 255)'
    >>> Color("rgb(30% 75% 100%)").to_string(precision=4)
    'rgb(76.5 191.3 255)'
    >>> Color("rgb(30% 75% 100%)").to_string(precision=3)
    'rgb(76.5 191 255)'
    >>> Color("rgb(30% 75% 100%)").to_string(precision=2)
    'rgb(77 190 260)'
    >>> Color("rgb(30% 75% 100%)").to_string(precision=1)
    'rgb(80 200 300)'
    ```

    Providing a precision of `0` will simply enable simple rounding to the nearest whole number.

    ```pycon3
    >>> Color("rgb(30% 75% 100%)").to_string(precision=0)
    'rgb(77 191 255)'
    ```

    Providing a precision of `-1` is a special input that will give the highest precision that can be given.

    ```pycon3
    >>> Color("rgb(30.3% 75.7% 100%)").to_string(precision=-1)
    'rgb(77.2650000000000005684341886080801486968994140625 193.034999999999996589394868351519107818603515625 255)'
    ```

- `fit`: set to `True` by default, `fit` controls whether colors are fit to their gamut or not. Some color spaces are
  technically unbounded, so no fitting may occur in those color spaces. Additionally, some color formats, like sRGB hex,
  are always fitted (regardless of the this setting) as they must fit into the gamut or they cannot be translated.

      ```pycon3
      >>> Color("rgb(30% 105% 0%)").to_string()
      'rgb(138 255 98.203)'
      >>> Color("rgb(30% 105% 0%)").to_string(fit=False)
      'rgb(76.5 267.75 0)'
      ```

- `color`: For some color spaces, this is the default output, but for others this format can be explicitly requested by
  setting `color` to `True`. If set to `True`, this will usually take priority over other format options.

    ```pycon3
    >>> Color("rebeccapurple").to_string(color=True)
    'color(srgb 0.4 0.2 0.6)'
    ```

In general, a color in a given color space may share the same options as listed above, but a given color space may also
have options unique to itself.

## sRGB Specific

sRGB can output colors to a hex format which is unique compared to HSL and others. Simply enable `hex`.

```pycon3
>>> color.to_string(hex=True)
'#8000ff4d'
```

When converting to hex color format, a color can be compressed in certain cases, enabling `compress` will compress a
hex color if possible.

```pycon3
>>> Color("#11223388").to_string(hex=True)
'#11223388'
>>> Color("#11223388").to_string(hex=True, compress=True)
'#1238'
```

sRGB can also output color names. If a color evaluates to a hex code which also evaluates to a color name in the
internal CSS color name mapping, then a color name will be returned. If the color does not match a color name, it will
fallback to whatever the other options dictate. Simply enable `names`.

```pycon3
>>> Color("#663399").to_string(names=True)
'rebeccapurple'
```

## Comma Format

In CSS, there are a number of color spaces that allow a comma format. Those are `srgb`, `hsl`, `hwb`, `lch`, and `lab`.
Basically, the only formats that do not allow comma format at this time are the colors that *only* support the `color()`
format.

If we want commas, we can force the comma syntax by setting `comma` to `True`. This can alter some color space output
in other subtle ways. As the comma format is the old legacy approach, when sRGB has commas enabled, it will use `rgba`
instead of the `rgb`. If using the default space syntax, `rgb` is always used, even when the color has transparency.

```pycon3
>>> Color("rgb(30 75 100 / 20%)").to_string(comma=True)
'rgba(30, 75, 100, 0.2)'
```
