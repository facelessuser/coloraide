# Manipulating Colors

## Reading Coordinates

There are various ways to read the current values of color coordinates.

1. Channel properties can be read directly:

    ```pycon3
    >>> color = Color("orange")
    >>> color.red
    1.0
    ```

2. Channel values can also be read by using the `get` method and providing the name of desired channel.

    ```pycon3
    >>> color = Color("orange")
    >>> color.get("green")
    0.6470588235294118
    ```

3. All non-alpha coordinates can be read simultaneously by using the `coords` function.

    ```pycon3
    >>> color = Color("orange")
    >>> color.coords()
    [1.0, 0.6470588235294118, 0.0]
    >>> color.alpha
    1.0
    ```

If a color coordinate is needed from another color space, it can be accessed by passing in the color space followed by
the name of the desired coordinate. The necessary conversions will happen behind the scenes and the desired value will
be returned.

```pycon3
>>> Color("blue").get("lch.chroma")
131.20704008299427
```

## Modifying Coordinates

Channel properties can be modified directly by using the named property. Here we modify `#!color red` and change it to
`#!color rgb(255 127.5 0)`.

```pycon3
>>> color = Color("red")
>>> color.to_string()
'rgb(255 0 0)'
>>> color.green = 0.5
>>> color.to_string()
'rgb(255 127.5 0)'
```

When doing so, keep in mind, the internal coordinates are being adjusted, and so they must be modified within the range
in which the values are stored, and for sRGB, it is in the range of \[0, 1\].

If desired, the values can be modified with the `set` method. As these methods return a reference to the class, multiple
set operations can be chained together. Chaining the operations together, we can transform `#!color white` to
`#!color rgb(0 127.5 255)`.

```pycon3
>>> Color("white").set("red", 0).set("green", 0.5).to_string()
'rgb(0 127.5 255)'
```

Channels in other color spaces can also be modified with the `set` function. Here we alter the color `#!color blue` in
the LCH color space and get `#!color rgb(19.403 81.154 0)`.

```pycon3
>>> Color("blue").set('lch.hue', 130).to_string()
'rgb(19.403 81.154 0)'
```

Functions can also be used to modify a channel property. Here we do a relative adjustment of the green channel and
transform the color `#!color pink` to `#!color rgb(255 249.6 203)`.

```pycon3
>>> Color("pink").set('green', lambda g: g * 1.3).to_string()
'rgb(255 249.6 203)'
```
