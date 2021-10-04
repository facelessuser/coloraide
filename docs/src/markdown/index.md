# Setup

!!! warning "Currently a Prerelease"
    While ColorAide is very usable and out of the alpha stage, it is currently in a prerelease. This simply means the
    API could still be in flux to some degree. ColorAide is still technically waiting for some issues related to CSS
    color syntax and behavior to be decided by the CSS Working Group.

## Overview

ColorAide is a color library for Python with the intent to provide an easy to use interface to work with colors. While
ColorAide is not just for CSS colors, there is a focus on supporting modern CSS color syntax as it is a format that is
very commonly used. In addition to being able to parse almost all colors as specified in the CSS specification,
ColorAide also supports a number of colors and formats for colors that are not in the CSS spec.

```playground
from coloraide import Color
c = Color('red')
c.coords()
c.to_string()
```

ColorAide was designed to be fairly easy library to pick up and start using. The idea was to have a simple interface to
specify any color, and once you have that color, you can convert it to any color you wish, manipulate it, mix it with
other colors, and then optionally get the color data or output into CSS strings. If desired, color spaces can be
overridden to output strings in other string formats or simply use the raw color data to manually construct the desired
output, but the primary focus was providing output in the familiar CSS output.

There are many color libraries out there, and if you happen to be looking for a library that is more for scientific
work, then maybe a library like [Colour Science](https://github.com/colour-science/colour) is more appropriate. That is
not to say you cannot analyze colors, plot them into diagrams and such with ColorAide, but we do not provide tools
geared towards such scientific endeavors, nor do we provide the shear amount of configurable options, color spaces,
white points, etc. that may come with a library such as Colour Science.

In the process of developing ColorAide, we spent a lot of time researching the CSS color spec and various color spaces.
In the process, we inevitably stumbled upon the JavaScript library [Color.js][colorjs] which is created/maintained by
the co-authors of some of the recent CSS color specifications. ColorAide became heavily influenced by Color.js as it
was useful in clarifying many points in the CSS color spec, and it adopted a very similar interface in which we were
aiming for. While our aim was not to port that library, we did learn a lot from it and it did leave a clear impression
on our API, though we do vary quite a bit and have gone our own way.

## Using ColorAide

ColorAide is easy to use.

You can create colors:

```playground
from coloraide import Color
c = Color('red')
c.to_string()
```

Convert colors:

```playground
from coloraide import Color
Color('red').convert('hsl').to_string()
```

Modify colors:

```playground
from coloraide import Color
Color('red').set("lch.chroma", 30).to_string()
```

Mix colors:

```playground
from coloraide import Color
Color("blue").mix("yellow", space="lch").to_string()
```

And much more!

## Installation

ColorAide can be installed via Python's `pip`:

```console
$ pip install coloraide
```
