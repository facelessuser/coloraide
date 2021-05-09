# Setup

!!! warning "Currently in Alpha"
    While ColorAide is very usable, it is currently in an alpha stage. While that doesn't necessarily mean buggy, it
    does mean the API could be unstable.

## Overview

ColorAide is a color library for Python with the intent to provide an easy to use interface to work with colors. While
ColorAide is not just for CSS colors, there is a focus on supporting modern CSS color syntax as it is a format that is
very commonly used. In addition to being able to parse almost all colors as specified in the CSS specification,
ColorAide also supports a number of colors and formats for colors that are not in the CSS spec.

ColorAide is built on the idea of having a general color object in which you can easily manipulate a color, convert
between colors in different spaces, and perform color related functions: interpolation, color distancing, color
contrast, etc.

In the process of developing ColorAide, we also stumbled upon the JavaScript library [Color.js][colorjs] which is
created/maintained by the co-authors of some of the recent CSS color specifications. This project became heavily
influenced by Color.js as it adopted a model we were already interested in. While our aim was not to port that library
and be a 1:1 copy of it, it provided much clarity on the CSS specification and, in the end, left a clear impression on
our API.

With ColorAide, you can create colors:

```color
from coloraide import Color
c = Color('red')
c.to_string()
```

Convert colors:

```color
from coloraide import Color
Color('red').convert('hsl').to_string()
```

Modify colors:

```color
from coloraide import Color
Color('red').set("lch.chroma", 30).to_string()
```

Mix colors:

```color
from coloraide import Color
Color("blue").mix("yellow", space="lch").to_string()
```

And much more!

## Installation

ColorAide can be installed via Python's `pip`:

```console
$ pip install coloraide
```
