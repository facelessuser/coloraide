# Manipulating Colors

## Reading Coordinates

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

If you need to get a color coordinate from another color space, but don't want to go the usual convert route,
you can pass in the space and coordinate and it will all happen behind the scenes:

```pycon3
>>> Color("blue").get("lch.chroma")
131.20704008299427
```

## Modifying Coordinates

You can change the value of the current color by adjusting the channel coordinates directly via the named property.
Here we modify `#!color red` and change it to `#!color rgb(255 127.5 0)`.

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
you'd use in CSS, you can specify coordinates as a string, and they will be parsed accordingly. Here we change
`#!color red` and change it to `#!color rgb(255 128 0)`.

```pycon3
>>> color = Color("red")
>>> color.to_string()
'rgb(255 0 0)'
>>> color.green = "128"
>>> color.to_string()
'rgb(255 128 0)'
```

In most cases, this would be identical to the units used in CSS, but sRGB has to distinguish the hex form from normal
floats and integers, so you have to append `#` to sRGB coordinates if you wish to treat them as hex. Here we change
`#!color red` and change it to `#!color rgb(255 51 0)`.

```pycon3
>>> color = Color("red")
>>> color.to_string()
'rgb(255 0 0)'
>>> color.green = "#33"
>>> color.to_string()
'rgb(255 51 0)'
```

If desired, you can also set attributes with the `set` method. As these methods return a reference to the class, you can
chain these settings together. Chaining the changes together, we can transform `#!color white` to
`#!color rgb(0 127.5 255)`.

```pycon3
>>> Color("white").set("red", "0%").set("green", "50%").to_string()
'rgb(0 127.5 255)'
```

You can also use `set` to set the attributes in other color spaces as well. Here we alter the the color `#!color blue`
in the LCH color space and get `#!color rgb(19.403 81.154 0)`.

```pycon3
>>> Color("blue").set('lch.hue', 130).to_string()
'rgb(19.403 81.154 0)'
```

You can also pass a function to modify the attribute. Here we do a relative adjustment of the green channel and
transform the color `#!color pink` to `#!color rgb(255 249.6 203)`.

```pycon3
>>> Color("pink").set('green', lambda g: g * 1.3).to_string()
'rgb(255 249.6 203)'
```