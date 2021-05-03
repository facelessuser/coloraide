[![Donate via PayPal][donate-image]][donate-link]
[![Discord][discord-image]][discord-link]
[![Build][github-ci-image]][github-ci-link]
[![Coverage Status][codecov-image]][codecov-link]
[![PyPI Version][pypi-image]][pypi-link]
[![PyPI - Python Version][python-image]][pypi-link]
![License][license-image-mit]

# ColorAide

This is still a work in progress.

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

With ColorAide, you can specify a color, convert it to other color spaces, mix it with other colors, output it in
different CSS formats, and much more!

```py
>>> from coloraide import Color
>>> c = Color("red")
>>> c.to_string()
'rgb(255 0 0)'
>>> c.convert('hsl').to_string()
'hsl(0 100% 50%)'
>>> c.set("lch.chroma", 30).to_string()
'rgb(173.81 114.29 97.218)'
>>> Color("blue").mix("yellow", space="lch").to_string()
'rgb(255 65.751 107.47)'
```

[colorjs]: https://github.com/LeaVerou/color.js

# Documentation

https://facelessuser.github.io/coloraide

## License

MIT

[github-ci-image]: https://github.com/facelessuser/coloraide/workflows/build/badge.svg?branch=master&event=push
[github-ci-link]: https://github.com/facelessuser/coloraide/actions?query=workflow%3Abuild+branch%3Amaster
[discord-image]: https://img.shields.io/discord/678289859768745989?logo=discord&logoColor=aaaaaa&color=mediumpurple&labelColor=333333
[discord-link]:https://discord.gg/TWs8Tgr
[codecov-image]: https://img.shields.io/codecov/c/github/facelessuser/coloraide/master.svg?logo=codecov&logoColor=aaaaaa&labelColor=333333
[codecov-link]: https://codecov.io/github/facelessuser/coloraide
[pypi-image]: https://img.shields.io/pypi/v/coloraide.svg?logo=pypi&logoColor=aaaaaa&labelColor=333333
[pypi-link]: https://pypi.python.org/pypi/coloraide
[python-image]: https://img.shields.io/pypi/pyversions/coloraide?logo=python&logoColor=aaaaaa&labelColor=333333
[license-image-mit]: https://img.shields.io/badge/license-MIT-blue.svg?labelColor=333333
[donate-image]: https://img.shields.io/badge/Donate-PayPal-3fabd1?logo=paypal
[donate-link]: https://www.paypal.me/facelessuser
