# Introduction

## What is ColorAide?

ColorAide is a pure Python, object oriented approach to colors.

```playground
from coloraide import Color
Color.steps(['lch(75% 50 0)', 'lch(75% 50 300)'], steps=8, space='lch', hue='longer')
```

ColorAide particularly has a focus on the following:

- [x] Accurate colors.

- [x] Proper round tripping (where reasonable).

- [x] Be generally easy to pick up for the average user.

- [x] Support modern CSS color spaces and syntax.

- [x] Make accessible many new and old non-CSS color spaces.

- [x] Provide a number of useful utilities such as interpolation, color distancing, blending, gamut mapping, etc.

- [x] Provide a plugin API to extend supported color spaces and more.

- [x] Allow users to configure defaults to their liking.

ColorAide is not meant to be the _one_ library to replace all other color libraries. There are many great libraries out
there such such as: [Colour Science][colour-science], [Colorio][colorio], [Python Color Math][color-math], and many
others. Some focus on the scientific aspects of colors and provide a wealth of various spaces, illuminants, access to
complex color space visualizers, and numerous esoteric tools. Some are highly focused on speed. Some are powerful, but
can be more complex to pick up by the average user.

At its heart, ColorAide was designed for convenience, flexibility, and to be very easy to pick up and work with. There
are, of course, some trade offs with speed when using a pure Python, object oriented approach, but there are also many
advantages as well. ColorAide might not always be the tool for **every** job, but hopefully it is a great tool all the
same.

## Installation

ColorAide can be installed via Python's `pip`:

```console
$ pip install coloraide
```
